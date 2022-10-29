from fastapi import HTTPException
from pydantic import ConstrainedInt


class NonNegativeInt(ConstrainedInt):
    ge = 0


def unix_interval_parameters(
    unix_start_ms: NonNegativeInt, unix_end_ms: NonNegativeInt
):
    if unix_start_ms >= unix_end_ms:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid time interval params: unix_start_ms must precede unix_end_ms"
            ),
        )
    return {"unix_start_ms": unix_start_ms, "unix_end_ms": unix_end_ms}
