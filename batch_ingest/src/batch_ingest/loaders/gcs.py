import json
import logging
from typing import Any

from google.cloud import storage


def upload_json_from_memory(
    bucket_name: str, blob_name: str, data: dict[str, Any], valparsed: bool
):
    """
    Uploads data as a JSON formatted string to a GCS bucket.

    Args:
        bucket_name: Target GCS bucket to store the object
        blob_name: Name of the blob object to store in the bucket
        data: In-memory object to serialize to JSON and upload
        valparsed: Boolean flag indicating if data has been validated prior
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(
        json.dumps(data, sort_keys=True, default=str), content_type="application/json"
    )
    exists = blob.exists()

    if exists and valparsed:
        logging.info(f"Uploaded validated data to gs://{bucket_name}/{blob_name}")
    elif exists and not valparsed:
        logging.warning(
            f"Uploaded non-validated data to gs://{bucket_name}/{blob_name}"
        )
    else:
        logging.error(
            "Following upload request, blob does not exist at"
            f" gs://{bucket_name}/{blob_name}"
        )
