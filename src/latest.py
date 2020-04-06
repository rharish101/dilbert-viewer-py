"""Functions and utilities to get info on the latest Dilbert comic."""
from datetime import datetime

from constants import LATEST_DATE_REFRESH, SRC_PREFIX
from utils import date_to_str, str_to_date


async def get_cached_latest_date(pool):
    """Get the cached latest date from the database.

    If the latest date is stale (ie. was updated a long time back), or it
    wasn't found in the cache, None is returned.

    Args:
        pool (`asyncpg.pool.Pool`): The database connection pool

    Returns:
        str: The date of the latest comic

    """
    # TODO: Raise server error
    async with pool.acquire() as conn:
        date = await conn.fetchval(
            "SELECT latest FROM latest_date WHERE last_check >= "
            "CURRENT_TIMESTAMP - INTERVAL '1 hour' * $1;",
            LATEST_DATE_REFRESH,
        )

    if date is not None:
        date = date_to_str(date)

    return date


async def cache_latest_date(date, pool):
    """Cache the latest date into the database.

    Args:
        date (str): The date of the latest comic in the format used by
            "dilbert.com"
        pool (`asyncpg.pool.Pool`): The database connection pool

    """
    # WHERE condition is not required as there is always only one row in
    # this table.
    # TODO: Raise server error
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE latest_date SET latest = $1, last_check = DEFAULT;",
            str_to_date(date),
        )
    if int(result.split()[1]) > 0:
        return

    # No rows were updated, so the table must be empty
    # TODO: Raise server error
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO latest_date (latest) VALUES ($1);", str_to_date(date),
        )


async def fetch_latest_date(sess):
    """Fetch the date of the latest comic from "dilbert.com".

    Args:
        sess (`aiohttp.ClientSession`): The aiohttp session for making GET
            requests to "dilbert.com"

    Returns:
        str: The HTML contents of the original comic

    """
    latest = date_to_str(datetime.now())
    url = SRC_PREFIX + latest
    # TODO: Raise server error
    async with sess.get(url) as resp:
        return resp.url.path.split("/")[-1]


async def get_latest_comic(pool, sess):
    """Get the date for the latest comic.

    Args:
        pool (`asyncpg.pool.Pool`): The database connection pool
        sess (`aiohttp.ClientSession`): The aiohttp session for making GET
            requests to "dilbert.com"

    Returns:
        str: The date of the latest comic, in the format used by "dilbert.com"

    """
    date = await get_cached_latest_date(pool)
    if date is not None:
        return date

    date = await fetch_latest_date(sess)
    await cache_latest_date(date, pool)

    return date
