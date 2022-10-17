import logging
import time

import extractors.coincap as coincap
import loaders.gcs as gcs
from datamodels.coincap import (
    AssetHistoryResponse,
    AssetInfoResponse,
    ExchangeInfoResponse,
    MarketHistoryResponse,
)
from utils.tools import unixtime_to_yyyymmdd
from utils.validate import try_valparse


def ingest_asset_info(asset_id: str, api_key: str, target_bucket: str) -> bool:
    """
    Extracts snapshot asset info from the CoinCap API, validates the response against a
    datamodel, and uploads it to a GCS bucket. Note - validation failure logs an error
    for alerting, and continues to upload the extracted data to GCS.

    Args:
        asset_id: CoinCap unique identifier for an asset
        api_key: CoinCap API key
        target_bucket: Target GCS bucket to store ingested data

    Returns:
        A boolean indicating if data was successfully uploaded to GCS.
    """
    asset_info = coincap.get_asset_info(asset_id, api_key)
    ts_unix = asset_info.get("timestamp", round(time.time() * 1000)) / 1000.0
    asset_info, valparse = try_valparse(asset_info, AssetInfoResponse)

    yyyy, mm, dd = unixtime_to_yyyymmdd(ts_unix)
    yyyymmdd = yyyy + mm + dd

    return gcs.upload_json_from_memory(
        bucket_name=target_bucket,
        blob_name=(
            f"coincap/asset_info/year={yyyy}/month={mm}/day={dd}"
            f"/asset_info_{asset_id}_{yyyymmdd}_{ts_unix}.json"
        ),
        data=asset_info,
        valparsed=valparse,
    )


def ingest_asset_history(
    asset_id: str,
    api_key: str,
    start_ms: int,
    end_ms: int,
    interval: str,
    target_bucket: str,
) -> bool:
    """
    Extracts historical asset data from the CoinCap API, validates the response against
    a datamodel, and uploads it to a GCS bucket. Note - validation failure logs an error
    for alerting, and continues to upload the extracted data to GCS.

    Args:
        asset_id: CoinCap unique identifier for an asset
        api_key: CoinCap API key
        start_ms: Unix timestamp in milliseconds. Start of the data range (inclusive).
        end_ms: Unix timestamp in milliseconds. End of the data range (exclusive).
        interval: Data interval in the range - (m1, m5, m15, m30, h1, h2, h6, h12, d1)
        target_bucket: Target GCS bucket to store ingested data

    Returns:
        A boolean indicating if data was successfully uploaded to GCS.
    """
    asset_history = coincap.get_asset_history(
        asset_id, api_key, start_ms, end_ms, interval
    )
    asset_history, valparse = try_valparse(asset_history, AssetHistoryResponse)

    if len(asset_history["data"]) == 0:
        logging.warning(f"AssetHistory data missing for: {asset_id}")

    yyyy, mm, dd = unixtime_to_yyyymmdd(start_ms / 1000.0)
    yyyymmdd = yyyy + mm + dd

    return gcs.upload_json_from_memory(
        bucket_name=target_bucket,
        blob_name=(
            f"coincap/asset_history/year={yyyy}/month={mm}/day={dd}"
            f"/asset_history_{asset_id}_{yyyymmdd}.json"
        ),
        data=asset_history,
        valparsed=valparse,
    )


def ingest_exchange_info(exchange_id: str, api_key: str, target_bucket: str) -> bool:
    """
    Extracts snapshot exchange info from the CoinCap API, validates the response
    against a datamodel, and uploads it to a GCS bucket. Note - validation failure
    logs an error for alerting, and continues to upload the extracted data to GCS.

    Args:
        exchange_id: CoinCap unique identifier for an exchange
        api_key: CoinCap API key
        target_bucket: Target GCS bucket to store ingested data

    Returns:
        A boolean indicating if data was successfully uploaded to GCS.
    """
    exchange_info = coincap.get_exchange_info(exchange_id, api_key)
    ts_unix = exchange_info["data"].get("updated", round(time.time() * 1000)) / 1000.0
    exchange_info, valparse = try_valparse(exchange_info, ExchangeInfoResponse)

    yyyy, mm, dd = unixtime_to_yyyymmdd(ts_unix)
    yyyymmdd = yyyy + mm + dd

    return gcs.upload_json_from_memory(
        bucket_name=target_bucket,
        blob_name=(
            f"coincap/exchange_info/year={yyyy}/month={mm}/day={dd}"
            f"/exchange_info_{exchange_id}_{yyyymmdd}_{ts_unix}.json"
        ),
        data=exchange_info,
        valparsed=valparse,
    )


def ingest_market_history(
    exchange_id: str,
    asset_id: str,
    quote_id: str,
    api_key: str,
    start_ms: int,
    end_ms: int,
    interval: str,
    target_bucket: str,
) -> bool:
    """
    Extracts historical market data (OHLCV candles) from the CoinCap API, validates the
    response against a datamodel, and uploads it to a GCS bucket. Note - validation
    failure logs an error for alerting, and continues to upload the extracted data to
    GCS.

    Args:
        exchange_id: CoinCap unique identifier for an exchange
        asset_id: CoinCap unique identifier for an asset
        quote_id: CoinCap asset id of the quote
        api_key: CoinCap API key
        start_ms: Unix timestamp in milliseconds. Start of the data range (inclusive).
        end_ms: Unix timestamp in milliseconds. End of the data range (exclusive).
        interval: Data interval in the range - (m1, m5, m15, m30, h1, h2, h6, h12, d1)
        target_bucket: Target GCS bucket to store ingested data

    Returns:
        A boolean indicating if data was successfully uploaded to GCS.
    """
    market_history = coincap.get_market_history(
        exchange_id,
        asset_id,
        quote_id,
        api_key,
        start_ms,
        end_ms,
        interval,
    )
    market_history, valparse = try_valparse(market_history, MarketHistoryResponse)

    if len(market_history["data"]) == 0:
        logging.warning(
            "MarketHistory data missing for exchange/asset/quote combination:"
            f" {exchange_id}/{asset_id}/{quote_id}"
        )

    yyyy, mm, dd = unixtime_to_yyyymmdd(start_ms / 1000.0)
    yyyymmdd = yyyy + mm + dd

    return gcs.upload_json_from_memory(
        bucket_name=target_bucket,
        blob_name=(
            f"coincap/market_history/year={yyyy}/month={mm}/day={dd}"
            f"/market_history_{exchange_id}-{asset_id}_{yyyymmdd}.json"
        ),
        data=market_history,
        valparsed=valparse,
    )
