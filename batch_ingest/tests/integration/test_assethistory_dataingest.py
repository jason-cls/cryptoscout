import json

import pytest
from batch_ingest.main import app
from fastapi.testclient import TestClient
from google.cloud import storage

client = TestClient(app)


def test_ingest_asset_history_schema_expected(
    mocker, asset_history_response, mock_bucket, mock_time, mock_asset_ids
):
    data, datamodel = asset_history_response
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_asset_history",
        return_value=data,
    )
    params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
    response = client.get("/ingestAssetHistory", params=params)
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/asset_history/year=2022/month=01/day=01/asset_history_{id}"
            "_20220101.json"
        ),
        mock_asset_ids,
    )

    for blob in expected_blobs:
        assert blob.exists()
        expected_data = json.dumps(datamodel.parse_obj(data).dict(), default=str)
        assert json.loads(expected_data) == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all asset history data!",
        "endpoint": "/ingestAssetHistory",
        "request_params": {"interval": params},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_asset_history_schema_drifted(
    mocker, asset_history_response_diff, mock_bucket, mock_time, mock_asset_ids
):
    data, _ = asset_history_response_diff
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_asset_history",
        return_value=data,
    )
    params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
    response = client.get("/ingestAssetHistory", params=params)
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/asset_history/year=2022/month=01/day=01/asset_history_{id}"
            "_20220101.json"
        ),
        mock_asset_ids,
    )

    for blob in expected_blobs:
        assert blob.exists()
        assert data == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all asset history data!",
        "endpoint": "/ingestAssetHistory",
        "request_params": {"interval": params},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_asset_history_timeinterval_toolarge():
    with pytest.raises(KeyError) as e:
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1700000000000}
        client.get("/ingestAssetHistory", params=params)
    assert "'data'" == str(e.value)
