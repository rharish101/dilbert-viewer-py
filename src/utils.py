"""Utilities for the viewer app."""
from datetime import datetime

from constants import DATE_FMT


def str_to_date(date, fmt=DATE_FMT):
    """Convert the date string to a `datetime.Datetime` object.

    NOTE: The given date must be in the format used by "dilbert.com".
    """
    return datetime.strptime(date, fmt)


def date_to_str(date, fmt=DATE_FMT):
    """Convert the `datetime.Datetime` object to a date string.

    The returned date will be in the format used by "dilbert.com".
    """
    return date.strftime(fmt)
