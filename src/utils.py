"""Utilities for the viewer app."""
from datetime import datetime

from constants import DATE_FMT


def curr_date() -> datetime:
    """Return the current date.

    The timezone is fixed to UTC so that the code is independent of local time.

    Returns:
        The current date
    """
    return datetime.utcnow()


def str_to_date(date_str: str, /, *, fmt: str = DATE_FMT) -> datetime:
    """Convert the date string to a `datetime.datetime` object.

    Args:
        date_str: The input date
        fmt: The format of the input date

    Returns:
        The converted date
    """
    return datetime.strptime(date_str, fmt)


def date_to_str(date_obj: datetime, /, *, fmt: str = DATE_FMT) -> str:
    """Convert the `datetime.datetime` object to a date string.

    Args:
        date_obj: The input date
        fmt: The format for the output date

    Returns:
        The converted date
    """
    return date_obj.strftime(fmt)
