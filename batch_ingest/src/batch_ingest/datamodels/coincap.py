from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConstrainedFloat,
    ConstrainedInt,
    Extra,
    Field,
    HttpUrl,
    PositiveInt,
)


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


class AssetInfoResponse(BaseModel):
    data: CryptoAsset
    timestamp: datetime


class ExchangeInfoResponse(BaseModel):
    data: Exchange
    timestamp: datetime
