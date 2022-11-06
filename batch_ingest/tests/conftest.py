import json
import os
from copy import deepcopy

import pytest
from batch_ingest.datamodels.coincap import (
    AssetHistoryResponse,
    AssetInfoResponse,
    ExchangeInfoResponse,
    MarketHistoryResponse,
)
from google.cloud import storage

curdir = os.path.dirname(os.path.realpath(__file__))
skip_test_msg = "Test not applicable"


@pytest.fixture
def mock_asset_ids(mocker):
    return mocker.patch("batch_ingest.main.ASSET_IDS", new=["asset1", "asset2"])


@pytest.fixture
def mock_exchange_ids(mocker):
    return mocker.patch("batch_ingest.main.EXCHANGE_IDS", new=["exch1", "exch2"])


@pytest.fixture
def mock_bucket(mocker):
    temp_bucket = "temp-cryptoscout"
    yield mocker.patch("batch_ingest.main.TARGET_BUCKET", new=temp_bucket)
    # Teardown logic - clear blob objects in bucket after test
    gcs_client = storage.Client()
    blobs = list(gcs_client.list_blobs(temp_bucket))
    gcs_client.bucket(temp_bucket).delete_blobs(blobs)


@pytest.fixture
def mock_time(mocker):
    return mocker.patch("time.time", return_value=7357.592)


@pytest.fixture(
    params=[
        ("asset_info_response.json", AssetInfoResponse),
        ("asset_history_response.json", AssetHistoryResponse),
        ("exchange_info_response.json", ExchangeInfoResponse),
        ("market_history_response.json", MarketHistoryResponse),
    ],
    ids=lambda p: f"{p[1].__name__}",
)
def coincap_response(request):
    path = os.path.join(curdir, "fixtures", request.param[0])
    with open(path) as file:
        data = json.load(file)
    return data, request.param[1]


@pytest.fixture
def coincap_response_invalidtype(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)

    if datamodel.__name__ == "AssetInfoResponse":
        mod_data["data"]["priceUsd"] = -1.337
    elif datamodel.__name__ == "AssetHistoryResponse":
        mod_data["data"][0]["date"] = "not a timestamp"
    elif datamodel.__name__ == "ExchangeInfoResponse":
        mod_data["data"]["tradingPairs"] = "not numeric"
    elif datamodel.__name__ == "MarketHistoryResponse":
        mod_data["data"][0]["high"] = -181

    return mod_data, datamodel


@pytest.fixture
def coincap_response_missingfield(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)

    if datamodel.__name__ == "AssetInfoResponse":
        del mod_data["data"]["priceUsd"]
    elif datamodel.__name__ == "AssetHistoryResponse":
        del mod_data["data"][0]["date"]
    elif datamodel.__name__ == "ExchangeInfoResponse":
        del mod_data["data"]["tradingPairs"]
    elif datamodel.__name__ == "MarketHistoryResponse":
        del mod_data["data"][0]["high"]

    return mod_data, datamodel


@pytest.fixture
def coincap_response_shallowextra(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)
    mod_data["shallow_extra"] = 123
    return mod_data, datamodel


@pytest.fixture
def coincap_response_deepextra(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)
    if datamodel.__name__ in {"AssetHistoryResponse", "MarketHistoryResponse"}:
        mod_data["data"][0]["deep_extra"] = "nested extra"
    else:
        mod_data["data"]["deep_extra"] = "nested extra"
    return mod_data, datamodel


@pytest.fixture
def asset_info_response(coincap_response):
    data, datamodel = coincap_response
    if datamodel.__name__ != "AssetInfoResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel


@pytest.fixture
def asset_info_response_diff(coincap_response_missingfield):
    mod_data, datamodel = coincap_response_missingfield
    if datamodel.__name__ != "AssetInfoResponse":
        pytest.skip(skip_test_msg)
    return mod_data, datamodel


@pytest.fixture
def asset_history_response(coincap_response):
    data, datamodel = coincap_response
    if datamodel.__name__ != "AssetHistoryResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel


@pytest.fixture
def asset_history_response_diff(coincap_response_missingfield):
    data, datamodel = coincap_response_missingfield
    if datamodel.__name__ != "AssetHistoryResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel


@pytest.fixture
def exchange_info_response(coincap_response):
    data, datamodel = coincap_response
    if datamodel.__name__ != "ExchangeInfoResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel


@pytest.fixture
def exchange_info_response_diff(coincap_response_missingfield):
    mod_data, datamodel = coincap_response_missingfield
    if datamodel.__name__ != "ExchangeInfoResponse":
        pytest.skip(skip_test_msg)
    return mod_data, datamodel


@pytest.fixture
def market_history_response(coincap_response):
    data, datamodel = coincap_response
    if datamodel.__name__ != "MarketHistoryResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel


@pytest.fixture
def market_history_response_diff(coincap_response_missingfield):
    data, datamodel = coincap_response_missingfield
    if datamodel.__name__ != "MarketHistoryResponse":
        pytest.skip(skip_test_msg)
    return data, datamodel
