from datetime import timedelta

import pendulum
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateBatchOperator,
)
from airflow.providers.google.cloud.sensors.gcs import (
    GCSObjectsWithPrefixExistenceSensor,
)
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.log.secrets_masker import mask_secret

from airflow import DAG

GCP_PROJECT_ID = "{{ var.value.GCP_PROJECT_ID }}"
GCS_RAW_BUCKET = "{{ var.value.GCS_RAW_BUCKET }}"
GCS_STAGE_BUCKET = "{{ var.value.GCS_STAGE_BUCKET }}"
GCS_DEPS_BUCKET = "{{ var.value.GCS_DEPS_BUCKET }}"
DATAPROC_REGION = "{{ var.value.DATAPROC_REGION }}"
DATAPROC_SERVICEACCOUNT = "{{ var.value.DATAPROC_SERVICEACCOUNT }}"
DATAPROC_SUBNET_URI = "{{ var.value.DATAPROC_SUBNET_URI }}"

historical_task_params = {
    "asset_history": {
        "ingest_endpoint": "ingestAssetHistory",
        "dataproc_main_python_file_uri": (
            f"gs://{GCS_DEPS_BUCKET}/dependencies/spark_batch/stage_asset_history.py"
        ),
    },
    "market_history": {
        "ingest_endpoint": "ingestMarketHistory",
        "dataproc_main_python_file_uri": (
            f"gs://{GCS_DEPS_BUCKET}/dependencies/spark_batch/stage_market_history.py"
        ),
    },
}

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
    max_active_tasks=4,
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
        ingest_historical = SimpleHttpOperator(
            task_id=f"ingest_{name}",
            http_conn_id="CLOUD_RUN_BATCHINGEST",
            endpoint=param["ingest_endpoint"],
            method="GET",
            data={
                "unix_start_ms": "{{ data_interval_start.format('x') }}",
                "unix_end_ms": "{{ data_interval_end.format('x') }}",
            },
            headers={"Authorization": "Bearer " + id_token},
            response_check=lambda response: bool(response.json()["success"]),
            log_response=True,
        )

        ingest_gcs_objects_exist_historical = GCSObjectsWithPrefixExistenceSensor(
            task_id=f"ingest_gcs_objects_exist_{name}",
            bucket=GCS_RAW_BUCKET,
            prefix=(
                "{{ data_interval_start.format"
                f"('[coincap/{name}/year=]YYYY[/month=]MM[/day=]DD')"
                " }}"
            ),
            poke_interval=5.0,
            timeout=30.0,
        )

        stage_gcs_historical = DataprocCreateBatchOperator(
            task_id=f"stage_{name}",
            project_id=GCP_PROJECT_ID,
            region=DATAPROC_REGION,
            batch={
                "pyspark_batch": {
                    "main_python_file_uri": param["dataproc_main_python_file_uri"],
                    "args": ["{{ ds }}", GCS_RAW_BUCKET, GCS_STAGE_BUCKET],
                    "python_file_uris": [
                        f"gs://{GCS_DEPS_BUCKET}/dependencies/spark_batch/commons.py"
                    ],
                },
                "runtime_config": {"version": "2.0"},
                "environment_config": {
                    "execution_config": {
                        "service_account": DATAPROC_SERVICEACCOUNT,
                        "subnetwork_uri": DATAPROC_SUBNET_URI,
                    }
                },
            },
            batch_id=f"stage-{name}".replace("_", "-")
            + "-{{ ds_nodash }}-{{ macros.time.time() | int }}",
            # impersonation_chain=DATAPROC_SERVICEACCOUNT,
            depends_on_past=True,
            wait_for_downstream=True,
        )

        (
            get_auth_token
            >> ingest_historical
            >> ingest_gcs_objects_exist_historical
            >> stage_gcs_historical
            >> execute_dbt
        )  # type: ignore

    latest_only = LatestOnlyOperator(task_id="latest_only")
