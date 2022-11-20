FROM python:3.10.6-slim-bullseye

# Allow log messages to immediately appear in cloud logging
ENV PYTHONUNBUFFERED=True

# Cache requirements installation in docker layer
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app to docker image
WORKDIR /app/batch_ingest
COPY ./src/batch_ingest .

# Run app when container launches
ENTRYPOINT ["python3", "main.py"]
