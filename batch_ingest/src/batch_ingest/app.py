import logging
import os

from datamodels.coincap import (
    AssetHistoryResponse,
    AssetInfoResponse,
    ExchangeInfoResponse,
    MarketHistoryResponse,
)
from dotenv import load_dotenv
from utils.datasources import (
    get_asset_history,
    get_asset_info,
    get_exchange_info,
    get_market_history,
)
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

interval_start = 1660348800000
interval_end = 1660435200000
INTERVAL = "h1"
QUOTE_ID = "tether"

asset_info = get_asset_info(asset_id, COINCAP_API_KEY)
asset_info, valparse = try_valparse(asset_info, AssetInfoResponse)

exchange_info = get_exchange_info(exchange_id, COINCAP_API_KEY)
exchange_info, valparse = try_valparse(exchange_info, ExchangeInfoResponse)

asset_prices = get_asset_history(
    asset_id, COINCAP_API_KEY, interval_start, interval_end, INTERVAL
)
asset_prices, valparse = try_valparse(asset_prices, AssetHistoryResponse)

market_candles = get_market_history(
    exchange_id,
    asset_id,
    QUOTE_ID,
    COINCAP_API_KEY,
    interval_start,
    interval_end,
    INTERVAL,
)
market_candles, valparse = try_valparse(market_candles, MarketHistoryResponse)

pass
