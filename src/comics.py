"""Functions and utilities to get info for requested Dilbert comics."""
import re

from asyncpg import UniqueViolationError

from constants import ALT_DATE_FMT, CACHE_LIMIT, SRC_PREFIX
from utils import date_to_str, str_to_date


async def get_cached_data(date, pool):
    """Get the cached comic data from the database.

    If the comic wasn't found in the cache, None is returned.

    Args:
        date (str): The date of the comic in the format used by "dilbert.com"
        pool (`asyncpg.pool.Pool`): The database connection pool

    Returns:
        dict: The cached data

    """
    # TODO: Raise server error
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT img_url, title FROM comic_cache WHERE comic = $1;",
            str_to_date(date),
        )
    if row is None:
        return None

    data = {
        "title": row[1],
        "actualDate": date,
        "dateStr": date_to_str(str_to_date(date), fmt=ALT_DATE_FMT),
        "imgURL": row[0],
    }

    # Update `last_used`, so that this comic isn't accidently de-cached
    # TODO: Raise server error
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
            str_to_date(date),
        )

    return data


async def clean_cache(pool):
    """Remove excess rows from the cache."""
    # TODO: Raise server error
    async with pool.acquire() as conn:
        approx_rows = await conn.fetchval(
            "SELECT reltuples FROM pg_class WHERE relname = 'comic_cache';"
        )
    if approx_rows < CACHE_LIMIT:
        return

    # TODO: Raise server error
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM comic_cache WHERE ctid in "
            "(SELECT ctid FROM comic_cache ORDER BY last_used LIMIT $1);",
            approx_rows - CACHE_LIMIT + 1,
        )


async def cache_data(date, data, pool):
    """Cache the comic data into the database.

    Args:
        date (str): The date of the comic in the format used by "dilbert.com"
        data (dict): The comic data to be cached
        pool (`asyncpg.pool.Pool`): The database connection pool

    """
    await clean_cache(pool)

    date = str_to_date(date)

    try:
        # TODO: Raise server error
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO comic_cache (comic, img_url, title) VALUES "
                "($1, $2, $3);",
                date,
                data["imgURL"],
                data["title"],
            )

    except UniqueViolationError:
        # This comic date exists, so simply update `last_used`
        # TODO: Raise server error
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
                date,
            )


async def fetch_og_comic(date, sess):
    """Fetch the original comic of the requested date from "dilbert.com".

    Args:
        date (str): The date of the requested comic in the format used by
            "dilbert.com"
        sess (`aiohttp.ClientSession`): The aiohttp session for making GET
            requests to "dilbert.com"

    Returns:
        str: The HTML contents of the original comic

    """
    url = SRC_PREFIX + date
    # TODO: Raise server error
    async with sess.get(url) as resp:
        return await resp.text()


def scrape_comic(content):
    """Scrape the comic contents and return the data obtained.

    The data obtained will be returned as a dict with the following content:
        * title: The title of that comic
        * actualDate: The date of the comic to which "dilbert.com" redirected
            when given the requested date
        * dateStr: The above date as a string formatted on "dilbert.com"
            (NOTE: This is different from the format used to fetch comics)
        * imgURL: The URL to the image

    Args:
        content (str): The HTML contents of the comic at "dilbert.com"

    Returns:
        dict: The comic data scraped

    """
    data = {}

    match = re.search(
        r'<span class="comic-title-name">([^<]+)</span>', content
    )
    if match is None:
        data["title"] = ""
    else:
        data["title"] = match.groups()[0]

    match = re.search(
        r'<date class="comic-title-date" item[pP]rop="datePublished">[^<]*'
        r'<span>([^<]*)</span>[^<]*<span item[pP]rop="copyrightYear">([^<]+)'
        r"</span>",
        content,
    )
    # TODO: Raise server error
    data["dateStr"] = " ".join(match.groups())
    data["actualDate"] = date_to_str(
        str_to_date(data["dateStr"], fmt=ALT_DATE_FMT)
    )

    match = re.search(r'<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>', content)
    # TODO: Raise server error
    data["imgURL"] = match.groups()[0]

    return data


async def get_comic_data(date, pool, sess):
    """Get the data for the requested date's comic.

    Args:
        date (str): The date of the comic in the format used by "dilbert.com"
        pool (`asyncpg.pool.Pool`): The database connection pool
        sess (`aiohttp.ClientSession`): The aiohttp session for making GET
            requests to "dilbert.com"

    """
    data = await get_cached_data(date, pool)
    if data is not None:
        return data

    scraped_content = await fetch_og_comic(date, sess)
    data = scrape_comic(scraped_content)
    await cache_data(date, data, pool)

    return data
