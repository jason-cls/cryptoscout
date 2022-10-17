from datetime import datetime, timezone


def unixtime_to_yyyymmdd(unix_seconds: int | float) -> tuple[str, str, str]:
    """Converts Unix time in seconds to zero-padded year, month, day values in UTC."""
    dt = datetime.fromtimestamp(unix_seconds, timezone.utc)
    year, month, day = dt.strftime("%Y-%m-%d").split("-")
    return year, month, day
