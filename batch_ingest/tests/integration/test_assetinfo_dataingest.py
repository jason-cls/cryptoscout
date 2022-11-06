import json

from batch_ingest.main import app
from fastapi.testclient import TestClient
from google.cloud import storage

client = TestClient(app)


def test_ingest_asset_info_schema_expected(
    mocker, asset_info_response, mock_bucket, mock_time, mock_asset_ids
):
    data, datamodel = asset_info_response
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_asset_info",
        return_value=data,
    )
    response = client.get("/ingestAssetInfo")
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/asset_info/year=2022/month=10/day=31/asset_info_{id}"
            "_20221031_1667182765.json"
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
        "message": "Successfully ingested all asset info data!",
        "endpoint": "/ingestAssetInfo",
        "request_params": {},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_asset_info_schema_drifted(
    mocker, asset_info_response_diff, mock_bucket, mock_time, mock_asset_ids
):
    data, _ = asset_info_response_diff
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_asset_info",
        return_value=data,
    )
    response = client.get("/ingestAssetInfo")
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda id: gcs_bkt.blob(
            f"coincap/asset_info/year=2022/month=10/day=31/asset_info_{id}"
            "_20221031_1667182765.json"
        ),
        mock_asset_ids,
    )

    for blob in expected_blobs:
        assert blob.exists()
        assert data == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all asset info data!",
        "endpoint": "/ingestAssetInfo",
        "request_params": {},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }
