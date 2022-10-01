from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure API request settings
DEFAULT_TIMEOUT = 10  # seconds
RETRY_CONFIG = Retry(
    total=8,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "HEAD"],
    backoff_factor=1,
)

http_adapter = HTTPAdapter(max_retries=RETRY_CONFIG)
http = requests.Session()
http.mount("http://", http_adapter)
http.mount("https://", http_adapter)


def get_asset_info(
    asset_id: str, api_key: str, timeout: int | float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    ENDPOINT = f"https://api.coincap.io/v2/assets/{asset_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = http.get(ENDPOINT, headers=headers, timeout=timeout)
    return response.json()


def get_exchange_info(
    exchange_id: str, api_key: str, timeout: int | float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    ENDPOINT = f"https://api.coincap.io/v2/exchanges/{exchange_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = http.get(ENDPOINT, headers=headers, timeout=timeout)
    return response.json()
