import logging
from typing import Any, Type

from pydantic import BaseModel, ValidationError


def try_valparse(
    raw_data: dict[str, Any], datamodel: Type[BaseModel]
) -> tuple[dict[str, Any], bool]:
    """
    Attempts data validation and type parsing using Pydantic models. Logs validation
    errors upon failure.

    Args:
        raw_data: raw data to validate
        datamodel: Pydantic Model to use for validation

    Returns:
        A tuple of either parsed or raw data, and a boolean indicating if
        validation and parsing were successful.
    """
    valparse = False
    try:
        parsed_data = datamodel.parse_obj(raw_data).dict()
        valparse = True
        logging.info(
            f"Validated and parsed raw data according to {datamodel.__name__} model"
        )
        return parsed_data, valparse
    except ValidationError as e:
        logging.error(
            f"Schema inconsistency detected between {datamodel.__name__} model. Unable"
            f" to validate and parse raw data:\n {e}"
        )
    return raw_data, valparse
