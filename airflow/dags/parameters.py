GCP_PROJECT_ID = "{{ var.value.GCP_PROJECT_ID }}"
GCS_RAW_BUCKET = "{{ var.value.GCS_RAW_BUCKET }}"
GCS_STAGE_BUCKET = "{{ var.value.GCS_STAGE_BUCKET }}"
GCS_DEPS_BUCKET = "{{ var.value.GCS_DEPS_BUCKET }}"
DATAPROC_REGION = "{{ var.value.DATAPROC_REGION }}"
DATAPROC_SERVICEACCOUNT = "{{ var.value.DATAPROC_SERVICEACCOUNT }}"
DATAPROC_SUBNET_URI = "{{ var.value.DATAPROC_SUBNET_URI }}"

# Historical data
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

# Snapshot data
snapshot_task_params = {
    "asset_info": {
        "ingest_endpoint": "ingestAssetInfo",
        "dataproc_main_python_file_uri": (
            f"gs://{GCS_DEPS_BUCKET}/dependencies/spark_batch/stage_asset_info.py"
        ),
    },
    "exchange_info": {
        "ingest_endpoint": "ingestExchangeInfo",
        "dataproc_main_python_file_uri": (
            f"gs://{GCS_DEPS_BUCKET}/dependencies/spark_batch/stage_exchange_info.py"
        ),
    },
}
