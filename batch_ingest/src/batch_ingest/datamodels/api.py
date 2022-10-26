from datetime import datetime
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra


class BaseModel(PydanticBaseModel):
    class Config:
        extra = Extra.forbid
        allow_mutation = False


class IngestJobResponse(BaseModel):
    success: bool
    message: str
    endpoint: str
    request_params: dict[str, Any]
    timestamp: datetime
