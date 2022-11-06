import json

from batch_ingest.main import app
from fastapi.testclient import TestClient
from google.cloud import storage

client = TestClient(app)


def test_ingest_exchange_info_schema_expected(
    mocker, exchange_info_response, mock_bucket, mock_time, mock_exchange_ids
):
    data, datamodel = exchange_info_response
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_exchange_info",
        return_value=data,
    )
    response = client.get("/ingestExchangeInfo")
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/exchange_info/year=2022/month=10/day=31/exchange_info_{id}"
            "_20221031_1667190132.json"
        ),
        mock_exchange_ids,
    )

    for blob in expected_blobs:
        assert blob.exists()
        expected_data = json.dumps(datamodel.parse_obj(data).dict(), default=str)
        assert json.loads(expected_data) == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all exchange info data!",
        "endpoint": "/ingestExchangeInfo",
        "request_params": {},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_exchange_info_schema_drifted(
    mocker, exchange_info_response_diff, mock_bucket, mock_time, mock_exchange_ids
):
    data, _ = exchange_info_response_diff
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_exchange_info",
        return_value=data,
    )
    response = client.get("/ingestExchangeInfo")
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/exchange_info/year=2022/month=10/day=31/exchange_info_{id}"
            "_20221031_1667190132.json"
        ),
        mock_exchange_ids,
    )

    for blob in expected_blobs:
        assert blob.exists()
        assert data == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all exchange info data!",
        "endpoint": "/ingestExchangeInfo",
        "request_params": {},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }
