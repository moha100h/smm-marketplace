"""Jalali (Shamsi) date utilities & formatting."""
import jdatetime
from datetime import datetime


def to_jalali_full(dt: datetime) -> str:
    """Convert datetime to Jalali date string."""
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    return jdt.strftime("%Y/%m/%d")


def to_jalali_with_year(date_str: str) -> str:
    """Convert YYYY-MM-DD to Jalali with day name."""
    try:
        dt = datetime.fromisoformat(date_str)
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return jdt.strftime("%A %Y/%m/%d")
    except Exception:
        return date_str


def fmt_price(amount: int) -> str:
    """Format price with thousand separators."""
    return f"{amount:,}"


def today_tehran() -> datetime:
    """Get current time in Tehran timezone."""
    import pytz
    tz = pytz.timezone("Asia/Tehran")
    return datetime.now(tz)
