"""Jalali date and price formatting utilities."""
import jdatetime


def fmt_price(amount: float) -> str:
    """Format price with thousand separators."""
    return "{:,.0f}".format(amount).replace(",", ",")


def fmt_date_jalali(dt) -> str:
    """Format datetime to Jalali date string."""
    if dt is None:
        return "-"
    try:
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return jdt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return str(dt)


def fmt_date_short(dt) -> str:
    """Format datetime to short Jalali date."""
    if dt is None:
        return "-"
    try:
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return jdt.strftime("%m/%d")
    except Exception:
        return str(dt)
