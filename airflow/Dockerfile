FROM apache/airflow:slim-2.5.1-python3.10

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

USER root
RUN mkdir -p /venvs
RUN chown 50000 /venvs
WORKDIR /venvs
USER 50000
RUN python3 -m venv dbt
RUN source dbt/bin/activate
RUN pip install --no-cache-dir dbt-bigquery==1.4.3

WORKDIR /opt/airflow
