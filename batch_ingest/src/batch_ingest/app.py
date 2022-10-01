import logging
import os

from datamodels.coincap import AssetInfoResponse, ExchangeInfoResponse
from dotenv import load_dotenv
from utils.datasources import get_asset_info, get_exchange_info
from utils.validate import try_valparse

load_dotenv(override=False)
COINCAP_API_KEY = os.environ["COINCAP_API_KEY"]

logging.basicConfig(
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y/%m/%d %I:%M:%S %p",
    level=logging.INFO,
)

asset_id = "bitcoin"
exchange_id = "binance"

asset_info = get_asset_info(asset_id, COINCAP_API_KEY)
asset_info, valparse = try_valparse(asset_info, AssetInfoResponse)

exchange_info = get_exchange_info(exchange_id, COINCAP_API_KEY)
exchange_info, valparse = try_valparse(exchange_info, ExchangeInfoResponse)

pass
