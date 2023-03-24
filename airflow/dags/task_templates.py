from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateBatchOperator,
)
from airflow.providers.google.cloud.sensors.gcs import (
    GCSObjectsWithPrefixExistenceSensor,
)
from airflow.providers.http.operators.http import SimpleHttpOperator
from parameters import (
    DATAPROC_REGION,
    DATAPROC_SERVICEACCOUNT,
    DATAPROC_SUBNET_URI,
    GCP_PROJECT_ID,
    GCS_DEPS_BUCKET,
    GCS_RAW_BUCKET,
    GCS_STAGE_BUCKET,
)


def ingest_coincap_data(
    data_name: str, endpoint: str, http_auth_bearer_token: str
) -> SimpleHttpOperator:
    return SimpleHttpOperator(
        task_id=f"ingest_{data_name}",
        http_conn_id="CLOUD_RUN_BATCHINGEST",
        endpoint=endpoint,
        method="GET",
        data={
            "unix_start_ms": "{{ data_interval_start.format('x') }}",
            "unix_end_ms": "{{ data_interval_end.format('x') }}",
        },
        headers={"Authorization": "Bearer " + http_auth_bearer_token},
        response_check=lambda response: bool(response.json()["success"]),
        log_response=True,
    )


def check_coincap_ingest_objects(
    data_name: str, datetime_template: str
) -> GCSObjectsWithPrefixExistenceSensor:
    return GCSObjectsWithPrefixExistenceSensor(
        task_id=f"ingest_gcs_objects_exist_{data_name}",
        bucket=GCS_RAW_BUCKET,
        prefix=(
            f"{{{{ {datetime_template}.format"
            f"('[coincap/{data_name}/year=]YYYY[/month=]MM[/day=]DD') }}}}"
        ),
        poke_interval=5.0,
        timeout=30.0,
    )


def stage_coincap_data(
    data_name: str, datetime_template: str, pyspark_main_python_file_uri: str
) -> DataprocCreateBatchOperator:
    return DataprocCreateBatchOperator(
        task_id=f"stage_{data_name}",
        project_id=GCP_PROJECT_ID,
        region=DATAPROC_REGION,
        batch={
            "pyspark_batch": {
                "main_python_file_uri": pyspark_main_python_file_uri,
                "args": [
                    f"{{{{ {datetime_template} | ds }}}}",
                    GCS_RAW_BUCKET,
                    GCS_STAGE_BUCKET,
                ],
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
        batch_id=f"stage-{data_name}".replace("_", "-")
        + f"-{{{{ {datetime_template} | ds_nodash }}}}"
        + "-{{ macros.time.time() | int }}",
        depends_on_past=True,
        wait_for_downstream=True,
    )
