import configparser
import json
import logging
import os
import time
from datetime import datetime, timezone

import extractors.coincap as coincap
import loaders.gcs as gcs
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
TARGET_BUCKET = config["gcs"]["target_bucket"]

logging.basicConfig(
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y/%m/%d %I:%M:%S %p",
    level=logging.INFO,
)


unix_start = 1640995200000
unix_end = 1641081600000

# Asset data
for asset_id in ASSET_IDS:
    # Asset Info
    asset_info = coincap.get_asset_info(asset_id, COINCAP_API_KEY)
    ts_unix = asset_info.get("timestamp", round(time.time() * 1000)) / 1000.0
    asset_info, valparse = try_valparse(asset_info, AssetInfoResponse)

    dt = datetime.fromtimestamp(ts_unix, timezone.utc)
    yyyy, mm, dd = dt.strftime("%Y-%m-%d").split("-")
    yyyymmdd = yyyy + mm + dd

    gcs.upload_json_from_memory(
        bucket_name=TARGET_BUCKET,
        blob_name=(
            f"coincap/asset_info/year={yyyy}/month={mm}/day={dd}"
            f"/asset_info_{asset_id}_{yyyymmdd}.json"
        ),
        data=asset_info,
        valparsed=valparse,
    )

    # Asset history
    asset_history = coincap.get_asset_history(
        asset_id, COINCAP_API_KEY, unix_start, unix_end, INTERVAL
    )
    asset_history, valparse = try_valparse(asset_history, AssetHistoryResponse)

    if len(asset_history["data"]) == 0:
        logging.warning(f"AssetHistory data missing for: {asset_id}")

    dt_start = datetime.fromtimestamp(unix_start / 1000.0, timezone.utc)
    yyyy, mm, dd = dt_start.strftime("%Y-%m-%d").split("-")
    yyyymmdd = yyyy + mm + dd

    gcs.upload_json_from_memory(
        bucket_name=TARGET_BUCKET,
        blob_name=(
            f"coincap/asset_history/year={yyyy}/month={mm}/day={dd}"
            f"/asset_history_{asset_id}_{yyyymmdd}.json"
        ),
        data=asset_history,
        valparsed=valparse,
    )

# Exchange data
for exchange_id in EXCHANGE_IDS:
    exchange_info = coincap.get_exchange_info(exchange_id, COINCAP_API_KEY)
    ts_unix = exchange_info["data"].get("updated", round(time.time() * 1000)) / 1000.0
    exchange_info, valparse = try_valparse(exchange_info, ExchangeInfoResponse)

    dt = datetime.fromtimestamp(ts_unix, timezone.utc)
    yyyy, mm, dd = dt.strftime("%Y-%m-%d").split("-")
    yyyymmdd = yyyy + mm + dd

    gcs.upload_json_from_memory(
        bucket_name=TARGET_BUCKET,
        blob_name=(
            f"coincap/exchange_info/year={yyyy}/month={mm}/day={dd}"
            f"/exchange_info_{exchange_id}_{yyyymmdd}.json"
        ),
        data=exchange_info,
        valparsed=valparse,
    )

# Market history (candlestick) data
for exchange_id in EXCHANGE_IDS:
    for asset_id in ASSET_IDS:
        market_history = coincap.get_market_history(
            exchange_id,
            asset_id,
            QUOTE_ID,
            COINCAP_API_KEY,
            unix_start,
            unix_end,
            INTERVAL,
        )
        market_history, valparse = try_valparse(market_history, MarketHistoryResponse)

        if len(market_history["data"]) == 0:
            logging.warning(
                "MarketHistory data missing for exchange/asset pair:"
                f" {exchange_id}/{asset_id}"
            )

        dt_start = datetime.fromtimestamp(unix_start / 1000.0, timezone.utc)
        yyyy, mm, dd = dt_start.strftime("%Y-%m-%d").split("-")
        yyyymmdd = yyyy + mm + dd

        gcs.upload_json_from_memory(
            bucket_name=TARGET_BUCKET,
            blob_name=(
                f"coincap/market_history/year={yyyy}/month={mm}/day={dd}"
                f"/market_history_{exchange_id}-{asset_id}_{yyyymmdd}.json"
            ),
            data=market_history,
            valparsed=valparse,
        )

pass
