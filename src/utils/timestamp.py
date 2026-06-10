"""Timestamp formatting helpers."""

from datetime import datetime


def format_timestamp(dt: datetime | None = None) -> str:
    """Format datetime as HH:MM:SS.mmm."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M:%S.") + f"{dt.microsecond // 1000:03d}"
