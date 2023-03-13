import os
from datetime import timedelta

import pendulum
from airflow.decorators import task

from airflow import DAG

CLOUD_RUN_BATCHINGEST_URL = os.environ["CLOUD_RUN_BATCHINGEST_URL"]

default_operator_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(seconds=180),
}

with DAG(
    dag_id="cryptoscout_etlt",
    description="Daily batch processing data pipeline for CryptoScout",
    schedule="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    default_args=default_operator_args,
    max_active_tasks=8,
    max_active_runs=4,
    catchup=True,
) as dag:

    @task
    def get_gauth_id_token(audience: str) -> str:
        import google.auth.transport.requests
        import google.oauth2.id_token

        print(f"Fetching ID Token for audience: {audience}")
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        return id_token

    id_token = get_gauth_id_token(CLOUD_RUN_BATCHINGEST_URL)
