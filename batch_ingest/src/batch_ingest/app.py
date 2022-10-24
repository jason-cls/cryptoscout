import configparser
import json
import logging
import logging.config
import os
import time

from dotenv import load_dotenv
from pipelines.coincap_to_gcs import (
    ingest_asset_history,
    ingest_asset_info,
    ingest_exchange_info,
    ingest_market_history,
)

# Setup
file_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(file_dir)
logging.config.fileConfig("logging.cfg")
logging.Formatter.converter = time.gmtime

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


unix_start_ms = 1640995200000
unix_end_ms = 1641081600000

# Asset info
success = True
for asset_id in ASSET_IDS:
    success *= ingest_asset_info(asset_id, COINCAP_API_KEY, TARGET_BUCKET)
if success:
    logging.info("Successfully ingested all asset info data!")
else:
    logging.error("Failed to ingest all asset info data.")

# Asset history
success = True
for asset_id in ASSET_IDS:
    success *= ingest_asset_history(
        asset_id, COINCAP_API_KEY, unix_start_ms, unix_end_ms, INTERVAL, TARGET_BUCKET
    )
if success:
    logging.info("Successfully ingested all asset history data!")
else:
    logging.error("Failed to ingest all asset history data.")

# Exchange info
success = True
for exchange_id in EXCHANGE_IDS:
    success *= ingest_exchange_info(exchange_id, COINCAP_API_KEY, TARGET_BUCKET)
if success:
    logging.info("Successfully ingested all exchange info data!")
else:
    logging.error("Failed to ingest all exchange info data.")

# Market history (candlestick) data
success = True
for exchange_id in EXCHANGE_IDS:
    for asset_id in ASSET_IDS:
        success *= ingest_market_history(
            exchange_id,
            asset_id,
            QUOTE_ID,
            COINCAP_API_KEY,
            unix_start_ms,
            unix_end_ms,
            INTERVAL,
            TARGET_BUCKET,
        )
if success:
    logging.info("Successfully ingested all market history data!")
else:
    logging.error("Failed to ingest all market history data.")

pass
