import configparser
import json
import logging
import os

import utils.datasources as dsrc
from datamodels.coincap import (
    AssetHistoryResponse,
    AssetInfoResponse,
    ExchangeInfoResponse,
    MarketHistoryResponse,
)
from dotenv import load_dotenv
from utils.validate import try_valparse

file_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(file_dir)

# Environment vars
load_dotenv(override=False)
COINCAP_API_KEY = os.environ["COINCAP_API_KEY"]

# Configuration
config = configparser.ConfigParser()
config.read("pipeline.cfg")
coincap_cfg = config["coincap.api"]
INTERVAL = coincap_cfg["historical_data_interval"]
QUOTE_ID = coincap_cfg["market_history_quote_id"]
ASSET_IDS = json.loads(coincap_cfg["asset_ids"])
EXCHANGE_IDS = json.loads(coincap_cfg["exchange_ids"])

logging.basicConfig(
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y/%m/%d %I:%M:%S %p",
    level=logging.INFO,
)


unix_start = 1640995200000
unix_end = 1641081600000

# Asset data
for asset_id in ASSET_IDS:
    asset_info = dsrc.get_asset_info(asset_id, COINCAP_API_KEY)
    asset_info, valparse = try_valparse(asset_info, AssetInfoResponse)

    asset_prices = dsrc.get_asset_history(
        asset_id, COINCAP_API_KEY, unix_start, unix_end, INTERVAL
    )
    asset_prices, valparse = try_valparse(asset_prices, AssetHistoryResponse)

    if len(asset_prices["data"]) == 0:
        logging.warning(f"AssetHistory data missing for: {asset_id}")

# Exchange data
for exchange_id in EXCHANGE_IDS:
    exchange_info = dsrc.get_exchange_info(exchange_id, COINCAP_API_KEY)
    exchange_info, valparse = try_valparse(exchange_info, ExchangeInfoResponse)

# Market history (candlestick) data
for exchange_id in EXCHANGE_IDS:
    for asset_id in ASSET_IDS:
        market_candles = dsrc.get_market_history(
            exchange_id,
            asset_id,
            QUOTE_ID,
            COINCAP_API_KEY,
            unix_start,
            unix_end,
            INTERVAL,
        )
        market_candles, valparse = try_valparse(market_candles, MarketHistoryResponse)

        if len(market_candles["data"]) == 0:
            logging.warning(
                "MarketHistory data missing for exchange/asset pair:"
                f" {exchange_id}/{asset_id}"
            )

pass
