from typing import Iterator

import pytest
from batch_ingest.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture()
def mock_log_job_status(mocker):
    return mocker.patch(
        "batch_ingest.main.log_job_status", return_value="status message"
    )


# Helper for side effect return values
def _altbool(*args, **kwargs) -> bool:
    def generate_bool() -> Iterator[bool]:
        x = 0
        while True:
            yield bool(x % 2)
            x += 1

    return next(generate_bool())


class TestRoot:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "endpoints": {
                "/": ["GET"],
                "/ingestAssetInfo": ["GET"],
                "/ingestAssetHistory": ["GET"],
                "/ingestExchangeInfo": ["GET"],
                "/ingestMarketHistory": ["GET"],
            }
        }


class TestIngestAssetInfo:
    def test_ingestAssetInfo_jobsuccess(self, mocker, mock_time, mock_log_job_status):
        mocker.patch("batch_ingest.main.ingest_asset_info", return_value=True)
        response = client.get("/ingestAssetInfo")
        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "status message",
            "endpoint": "/ingestAssetInfo",
            "request_params": {},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    def test_ingestAssetInfo_jobfail(self, mocker, mock_time, mock_log_job_status):
        mocker.patch("batch_ingest.main.ingest_asset_info", side_effect=_altbool)
        response = client.get("/ingestAssetInfo")
        assert response.status_code == 200
        assert response.json() == {
            "success": False,
            "message": "status message",
            "endpoint": "/ingestAssetInfo",
            "request_params": {},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }


class TestIngestAssetHistory:
    def test_ingestAssetHistory_jobsuccess(
        self, mocker, mock_time, mock_log_job_status
    ):
        mocker.patch("batch_ingest.main.ingest_asset_history", return_value=True)
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
        response = client.get("/ingestAssetHistory", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "status message",
            "endpoint": "/ingestAssetHistory",
            "request_params": {"interval": params},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    def test_ingestAssetHistory_jobfail(self, mocker, mock_time, mock_log_job_status):
        mocker.patch("batch_ingest.main.ingest_asset_history", side_effect=_altbool)
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
        response = client.get("/ingestAssetHistory", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "success": False,
            "message": "status message",
            "endpoint": "/ingestAssetHistory",
            "request_params": {"interval": params},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    # Invalid query parameter combinations
    @pytest.mark.parametrize(
        "unix_start_ms",
        ["string", -654321, None, 1641081600000],
        ids=lambda p: f"unix_start_ms:{p}",
    )
    @pytest.mark.parametrize(
        "unix_end_ms",
        ["invalid", -12345, None, 1640995200000],
        ids=lambda p: f"unix_end_ms:{p}",
    )
    def test_ingestAssetHistory_invalidcall(self, mocker, unix_start_ms, unix_end_ms):
        mock = mocker.patch("batch_ingest.main.ingest_asset_history", return_value=None)
        response = client.get(
            "/ingestAssetHistory",
            params={"unix_start_ms": unix_start_ms, "unix_end_ms": unix_end_ms},
        )
        assert response.status_code == 422
        assert not mock.called


class TestIngestExchangeInfo:
    def test_ingestExchangeInfo_jobsuccess(
        self, mocker, mock_time, mock_log_job_status
    ):
        mocker.patch("batch_ingest.main.ingest_exchange_info", return_value=True)
        response = client.get("/ingestExchangeInfo")
        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "status message",
            "endpoint": "/ingestExchangeInfo",
            "request_params": {},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    def test_ingestExchangeInfo_jobfail(self, mocker, mock_time, mock_log_job_status):
        mocker.patch("batch_ingest.main.ingest_exchange_info", side_effect=_altbool)
        response = client.get("/ingestExchangeInfo")
        assert response.status_code == 200
        assert response.json() == {
            "success": False,
            "message": "status message",
            "endpoint": "/ingestExchangeInfo",
            "request_params": {},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }


class TestIngestMarketHistory:
    def test_ingestMarketHistory_jobsuccess(
        self, mocker, mock_time, mock_log_job_status
    ):
        mocker.patch("batch_ingest.main.ingest_market_history", return_value=True)
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
        response = client.get("/ingestMarketHistory", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "status message",
            "endpoint": "/ingestMarketHistory",
            "request_params": {"interval": params},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    def test_ingestMarketHistory_jobfail(self, mocker, mock_time, mock_log_job_status):
        mocker.patch("batch_ingest.main.ingest_market_history", side_effect=_altbool)
        params = {"unix_start_ms": 1640995200000, "unix_end_ms": 1641081600000}
        response = client.get("/ingestMarketHistory", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "success": False,
            "message": "status message",
            "endpoint": "/ingestMarketHistory",
            "request_params": {"interval": params},
            "timestamp": "1970-01-01T02:02:38+00:00",
        }

    # Invalid query parameter combinations
    @pytest.mark.parametrize(
        "unix_start_ms",
        ["string", -654321, None, 1641081600000],
        ids=lambda p: f"unix_start_ms:{p}",
    )
    @pytest.mark.parametrize(
        "unix_end_ms",
        ["invalid", -12345, None, 1640995200000],
        ids=lambda p: f"unix_end_ms:{p}",
    )
    def test_ingestMarketHistory_invalidcall(self, mocker, unix_start_ms, unix_end_ms):
        mock = mocker.patch(
            "batch_ingest.main.ingest_market_history", return_value=None
        )
        response = client.get(
            "/ingestMarketHistory",
            params={"unix_start_ms": unix_start_ms, "unix_end_ms": unix_end_ms},
        )
        assert response.status_code == 422
        assert not mock.called
