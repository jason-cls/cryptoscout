import configparser
import inspect
import json
import logging
import logging.config
import os
import time

from datamodels.api import IngestJobResponse
from dependencies import unix_interval_parameters
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from pipelines.coincap_to_gcs import (
    ingest_asset_history,
    ingest_asset_info,
    ingest_exchange_info,
    ingest_market_history,
)
from utils.tools import log_job_status

# Setup
file_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(file_dir)
logging.config.fileConfig("logging.cfg", disable_existing_loggers=False)
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

app = FastAPI()


@app.get("/")
def root():
    """Returns a list of exposed API endpoints and their respective HTTP methods."""
    return {
        "endpoints": {
            route.path: route.methods
            for route in app.routes
            if isinstance(route, APIRoute)
        }
    }


@app.get("/ingestAssetInfo", response_model=IngestJobResponse)
def ingest_asset_info_job():
    """Ingests current asset info snapshot data for a fixed set of assets."""
    success = True
    for asset_id in ASSET_IDS:
        success *= ingest_asset_info(asset_id, COINCAP_API_KEY, TARGET_BUCKET)
    msg = log_job_status("asset info", bool(success))
    locvars = locals()
    return {
        "success": success,
        "message": msg,
        "endpoint": "/ingestAssetInfo",
        "request_params": {
            k: locvars.get(k)
            for k in inspect.signature(ingest_asset_info_job).parameters.keys()
        },
        "timestamp": round(time.time()),
    }


@app.get("/ingestAssetHistory", response_model=IngestJobResponse)
def ingest_asset_history_job(interval: dict = Depends(unix_interval_parameters)):
    """Ingests historical asset data within a time interval for a fixed set of assets.
    """
    success = True
    for asset_id in ASSET_IDS:
        success *= ingest_asset_history(
            asset_id,
            COINCAP_API_KEY,
            interval["unix_start_ms"],
            interval["unix_end_ms"],
            INTERVAL,
            TARGET_BUCKET,
        )
    msg = log_job_status("asset history", bool(success))
    locvars = locals()
    return {
        "success": success,
        "message": msg,
        "endpoint": "/ingestAssetHistory",
        "request_params": {
            k: locvars.get(k)
            for k in inspect.signature(ingest_asset_history_job).parameters.keys()
        },
        "timestamp": round(time.time()),
    }


@app.get("/ingestExchangeInfo", response_model=IngestJobResponse)
def ingest_exchange_info_job():
    """Ingests current exchange info snapshot data for a fixed set of exchanges."""
    success = True
    for exchange_id in EXCHANGE_IDS:
        success *= ingest_exchange_info(exchange_id, COINCAP_API_KEY, TARGET_BUCKET)
    msg = log_job_status("exchange info", bool(success))
    locvars = locals()
    return {
        "success": success,
        "message": msg,
        "endpoint": "/ingestExchangeInfo",
        "request_params": {
            k: locvars.get(k)
            for k in inspect.signature(ingest_exchange_info_job).parameters.keys()
        },
        "timestamp": round(time.time()),
    }


@app.get("/ingestMarketHistory", response_model=IngestJobResponse)
def ingest_market_history_job(interval: dict = Depends(unix_interval_parameters)):
    """Ingests historical market data (OHLCV candles) within a time interval for a
    fixed combination of assets and exchanges.
    """
    success = True
    for exchange_id in EXCHANGE_IDS:
        for asset_id in ASSET_IDS:
            success *= ingest_market_history(
                exchange_id,
                asset_id,
                QUOTE_ID,
                COINCAP_API_KEY,
                interval["unix_start_ms"],
                interval["unix_end_ms"],
                INTERVAL,
                TARGET_BUCKET,
            )
    msg = log_job_status("market history", bool(success))
    locvars = locals()
    return {
        "success": success,
        "message": msg,
        "endpoint": "/ingestMarketHistory",
        "request_params": {
            k: locvars.get(k)
            for k in inspect.signature(ingest_market_history_job).parameters.keys()
        },
        "timestamp": round(time.time()),
    }


if __name__ == "__main__":
    import uvicorn

    server_port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=server_port, log_level="info")
