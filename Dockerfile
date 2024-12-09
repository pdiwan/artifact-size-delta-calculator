FROM python:3.10-slim
WORKDIR /
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "src/app.py"]
