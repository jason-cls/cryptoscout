import logging
from datetime import datetime, timezone


def unixtime_to_yyyymmdd(unix_seconds: int | float) -> tuple[str, str, str]:
    """Converts Unix time in seconds to zero-padded year, month, day values in UTC."""
    dt = datetime.fromtimestamp(unix_seconds, timezone.utc)
    year, month, day = dt.strftime("%Y-%m-%d").split("-")
    return year, month, day


def log_job_status(job_name: str, success_flag: bool) -> str:
    """Logs and returns the logged message based on a job's success/failure status."""
    if success_flag:
        message = f"Successfully ingested all {job_name} data!"
        logging.info(message)
    else:
        message = f"Failed to ingest all {job_name} data."
        logging.error(message)
    return message
