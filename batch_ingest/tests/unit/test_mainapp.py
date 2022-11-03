from batch_ingest.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
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
