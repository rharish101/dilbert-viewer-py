"""Utilities for the viewer app."""
from datetime import datetime

from constants import DATE_FMT


def str_to_date(date, fmt=DATE_FMT):
    """Convert the date string to a `datetime.Datetime` object.

    Args:
        date (str): The input date
        fmt (str): The format of the input date

    Returns:
        `datetime.Datetime`: The converted date

    """
    return datetime.strptime(date, fmt)


def date_to_str(date, fmt=DATE_FMT):
    """Convert the `datetime.Datetime` object to a date string.

    Args:
        date (`datetime.Datetime`): The input date
        fmt (str): The format for the output date

    Returns:
        str: The converted date

    """
    return date.strftime(fmt)
