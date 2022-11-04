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

curdir = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
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


@pytest.fixture()
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


@pytest.fixture()
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


@pytest.fixture()
def coincap_response_shallowextra(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)
    mod_data["shallow_extra"] = 123
    return mod_data, datamodel


@pytest.fixture()
def coincap_response_deepextra(coincap_response):
    data, datamodel = coincap_response
    mod_data = deepcopy(data)
    if datamodel.__name__ in {"AssetHistoryResponse", "MarketHistoryResponse"}:
        mod_data["data"][0]["deep_extra"] = "nested extra"
    else:
        mod_data["data"]["deep_extra"] = "nested extra"
    return mod_data, datamodel
