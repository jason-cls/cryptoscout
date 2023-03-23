from datetime import timedelta

import pendulum
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.log.secrets_masker import mask_secret
from parameters import historical_task_params
from task_templates import (
    check_coincap_ingest_objects,
    ingest_coincap_data,
    stage_coincap_data,
)

from airflow import DAG


default_operator_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(seconds=180),
}

with DAG(
    dag_id="cryptoscout_etlt",
    description="Daily batch processing data pipeline for CryptoScout",
    schedule="0 0 * * *",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    end_date=pendulum.datetime(2022, 1, 2, tz="UTC"),
    default_args=default_operator_args,
    max_active_tasks=8,
    max_active_runs=2,
    catchup=True,
) as dag:

    @task
    def get_gauth_id_token(audience_key: str) -> str:
        """Fetches a Google ID token for an audience defined in an Airflow Variable"""
        import google.auth.transport.requests
        import google.oauth2.id_token

        audience = Variable.get(audience_key)
        print(f"Fetching ID Token for audience: {audience}")
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        mask_secret(id_token)
        return id_token

    id_token = "{{ ti.xcom_pull(task_ids='get_gauth_id_token') }}"
    get_auth_token = get_gauth_id_token("CLOUD_RUN_BATCHINGEST_URL")

    execute_dbt = BashOperator(
        task_id="dbt_run",
        bash_command="echo cmd_placeholder",
        depends_on_past=True,
        trigger_rule="none_failed_min_one_success",
    )

    for name, param in historical_task_params.items():
        ingest_historical = ingest_coincap_data(
            data_name=name,
            endpoint=param["ingest_endpoint"],
            http_auth_bearer_token=id_token,
        )

        ingest_gcs_objects_exist_historical = check_coincap_ingest_objects(
            data_name=name
        )

        stage_gcs_historical = stage_coincap_data(
            data_name=name,
            pyspark_main_python_file_uri=param["dataproc_main_python_file_uri"],
        )

        (
            get_auth_token
            >> ingest_historical
            >> ingest_gcs_objects_exist_historical
            >> stage_gcs_historical
            >> execute_dbt
        )  # type: ignore

    latest_only = LatestOnlyOperator(task_id="latest_only")
