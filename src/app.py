
from flask import Flask, request, jsonify
import requests
import semver

# Using flask is great for PoC apps, for any production applications, 
# I'd use more robust frameworks such as FastAPI or Starlette 
# that offer better concurrency via async-await model to handle large scale traffic 
app = Flask(__name__)

# This function pulls all the release artifacts metadata from github and creates 2 data structures - 
# versions - list of SemVer objects representing all release versions for this product
# release_size_info - dict/map of version numbers as keys and the size of the tarball as value
def get_release_info():
    try:
        # Get all the releases metadata
        resp = requests.get(
                                "https://api.github.com/repos/apache/airflow/releases",
                                headers={"Accept": "application/vnd.github.v3+json"}
                            )
        if resp.status_code != 200:
            raise Exception("Failed to get release data from GitHub")
    except Exception as e:
        print(str(e))

    # Extract size information for the .tar.gz asset
    versions = []
    release_size_info = {}
    for release in resp.json():
        try:
            release_version = release.get("tag_name")
            release_version = release_version.lstrip("v")         
            if not semver.version.Version.is_valid(release_version):
                continue
            
            version = semver.VersionInfo.parse(release_version)
            for asset in release.get("assets", []):
                release_name = asset.get("name")
                if release_name == "apache-airflow-{}.tar.gz".format(release_version) or \
                    release_name == "apache_airflow-{}.tar.gz".format(release_version):
                    size = asset.get("size", 0)
                    break

            versions.append(version)
            release_size_info[str(release_version)] = size
        except Exception as e:
            print("get_release_info: error in processing releases - " , str(e), release_version)

    return versions, release_size_info


# Function to return Semver object as a tuple for sorting purpose
def semver_tuple(version):
    return version.to_tuple()


# Healthcheck endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"Status": "Healthy"}), 200


# / endpoint
@app.route("/", methods=["GET"])
def home():
    return jsonify({"Message": "Welcome to artifacts size delta calculater app"}), 200


# API definition for extracting bloat ratios
@app.route("/apache/airflow/bloat", methods=["GET"])
def get_artifact_deltas():
    # Fetch the query parameters
    start = request.args.get("start")
    end = request.args.get("end")

    # Validation checks
    if not start or not end:
        return jsonify({"error": "'start' and 'end' query parameters are required"}), 400
    
    start = start.lstrip("v")
    end = end.lstrip("v")

    # More validation checks
    if not semver.version.Version.is_valid(start):
        return jsonify({"Error": "Invalid 'start' version"}), 400
    if not semver.version.Version.is_valid(end):
        return jsonify({"Error": "Invalid 'end' version"}), 400
    if not semver.version.Version.parse(start).match("<={}".format(end)):
        return jsonify({"Error": "'start' version should be less than or equal to 'end' version"}), 400

    
    result = {"deltas": []}
    try:
        # Get all the release versions and their sizes
        versions, release_size_info = get_release_info()

        # Sort the versions list and slice it from start-1 to end versions 
        versions = sorted(versions, key=semver_tuple)
        try:
            i = versions.index(semver.VersionInfo.parse(start))
        except ValueError:
            return jsonify({"Error": "'start' version in not in the releases"}), 400
        try:
            j = versions.index(semver.VersionInfo.parse(end))
        except ValueError:
            return jsonify({"Error": "'end' version in not in the releases"}), 400

        selected_versions = versions[i-1 if i > 0 else 0 : j+1 if j < len(versions)-1 else len(versions)-1]

        # Iterate over the list and fetch the corresponding size from the
        # release_size_info for current and previous versions and calculate the bloat ratio
        for i in range(1, len(selected_versions)):
            prev_build_size = release_size_info.get(str(selected_versions[i-1]))
            cur_build_size = release_size_info.get(str(selected_versions[i]))                 
            result['deltas'].append({
                                        "previous_tag": str(selected_versions[i-1]),
                                        "tag": str(selected_versions[i]),
                                        "delta": cur_build_size / prev_build_size if prev_build_size else None
                                    })

    except Exception as e:
        print("get_artifact_deltas: error - ", str(e))
        return jsonify({"error": str(e)}), 500
    
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
