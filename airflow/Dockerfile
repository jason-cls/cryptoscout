FROM apache/airflow:slim-2.5.1-python3.10

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
