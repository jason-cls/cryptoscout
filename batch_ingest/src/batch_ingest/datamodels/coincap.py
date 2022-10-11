import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConstrainedFloat,
    ConstrainedInt,
    Extra,
    Field,
    HttpUrl,
    PositiveInt,
    validator,
)


def data_non_empty_warning(data: list[Any]) -> list[Any]:
    if len(data) == 0:
        logging.warning("Empty list returned for data field.")
    return data


class BaseModel(PydanticBaseModel):
    class Config:
        extra = Extra.forbid
        allow_mutation = False


class NonNegativeInt(ConstrainedInt):
    ge = 0


class NonNegativeFloat(ConstrainedFloat):
    ge = 0


class CryptoAsset(BaseModel):
    id: str
    rank: PositiveInt
    symbol: str
    name: str
    supply: NonNegativeFloat
    maxSupply: NonNegativeFloat | None = Field(...)
    marketCapUsd: NonNegativeFloat
    volumeUsd24Hr: NonNegativeFloat
    priceUsd: NonNegativeFloat
    changePercent24Hr: float
    vwap24Hr: NonNegativeFloat
    explorer: HttpUrl


class Exchange(BaseModel):
    exchangeId: str
    name: str
    rank: PositiveInt
    percentTotalVolume: NonNegativeFloat
    volumeUsd: NonNegativeFloat
    tradingPairs: NonNegativeInt
    socket: bool
    exchangeUrl: HttpUrl
    updated: datetime


class AssetHistory(BaseModel):
    priceUsd: NonNegativeFloat
    time: NonNegativeInt
    circulatingSupply: NonNegativeFloat
    date: datetime


class MarketHistory(BaseModel):
    open: NonNegativeFloat
    high: NonNegativeFloat
    low: NonNegativeFloat
    close: NonNegativeFloat
    volume: NonNegativeFloat
    period: datetime


class AssetInfoResponse(BaseModel):
    data: CryptoAsset
    timestamp: datetime


class ExchangeInfoResponse(BaseModel):
    data: Exchange
    timestamp: datetime


class AssetHistoryResponse(BaseModel):
    data: list[AssetHistory]
    timestamp: datetime

    _nonempty_data = validator("data", allow_reuse=True)(data_non_empty_warning)


class MarketHistoryResponse(BaseModel):
    data: list[MarketHistory]
    timestamp: datetime

    _nonempty_data = validator("data", allow_reuse=True)(data_non_empty_warning)
