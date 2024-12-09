# Build and run the Docker container locally - 
- docker build -t artifact-size-delta-calculator .
- docker run -p 5000:5000 artifact-size-delta-calculator


# Push image to Docker hub - 
- docker login
- docker tag artifact-size-delta-calculator piyushdiwan/artifact-size-delta-calculator:v1.0
- docker push piyushdiwan/artifact-size-delta-calculator:v1.0


# Pull image from Docker hub -
- docker pull piyushdiwan/artifact-size-delta-calculator:v1.0


# Test on terminal - 
## Valid cases
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.3&end=v2.9.2"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.3&end=v2.8.3"


## Invalid cases
- curl "http://localhost:5000/apache/airflow/bloat"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.0"
- curl "http://localhost:5000/apache/airflow/bloat?end=v2.15.6"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2&end=v2.15.6"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.0&end=v2"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.3&end=v2.8.1"
- curl "http://localhost:5000/apache/airflow/bloat?start=v2.8.0&end=v2.15.6"
