import itertools
import json

import pytest
from batch_ingest.main import app
from fastapi.testclient import TestClient
from google.cloud import storage

client = TestClient(app)


def test_ingest_market_history_schema_expected(
    mocker,
    market_history_response,
    mock_bucket,
    mock_time,
    mock_asset_ids,
    mock_exchange_ids,
):
    data, datamodel = market_history_response
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_market_history",
        return_value=data,
    )
    params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
    response = client.get("/ingestMarketHistory", params=params)
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda ids: gcs_bkt.blob(
            "coincap/market_history/year=2022/month=01/day=01/market_history"
            f"_{ids[1]}-{ids[0]}_20220101.json"
        ),
        list(itertools.product(mock_asset_ids, mock_exchange_ids)),
    )

    for blob in expected_blobs:
        assert blob.exists()
        expected_data = json.dumps(datamodel.parse_obj(data).dict(), default=str)
        assert json.loads(expected_data) == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all market history data!",
        "endpoint": "/ingestMarketHistory",
        "request_params": {"interval": params},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_market_history_schema_drifted(
    mocker,
    market_history_response_diff,
    mock_bucket,
    mock_time,
    mock_asset_ids,
    mock_exchange_ids,
):
    data, _ = market_history_response_diff
    mocker.patch(
        "batch_ingest.pipelines.coincap_to_gcs.coincap.get_market_history",
        return_value=data,
    )
    params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
    response = client.get("/ingestMarketHistory", params=params)
    gcs_bkt = storage.Client().bucket(mock_bucket)
    expected_blobs = map(
        lambda ids: gcs_bkt.blob(
            "coincap/market_history/year=2022/month=01/day=01/market_history"
            f"_{ids[1]}-{ids[0]}_20220101.json"
        ),
        list(itertools.product(mock_asset_ids, mock_exchange_ids)),
    )

    for blob in expected_blobs:
        assert blob.exists()
        assert data == json.loads(blob.download_as_bytes())

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Successfully ingested all market history data!",
        "endpoint": "/ingestMarketHistory",
        "request_params": {"interval": params},
        "timestamp": "1970-01-01T02:02:38+00:00",
    }


def test_ingest_market_history_timeinterval_toolarge():
    with pytest.raises(KeyError) as e:
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1700000000000}
        client.get("/ingestMarketHistory", params=params)
    assert "'data'" == str(e.value)
