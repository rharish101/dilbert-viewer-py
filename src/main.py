"""The main file for the viewer app."""
import asyncio
import os
import random
import ssl
from datetime import timedelta
from typing import Union

import aiohttp
import asyncpg
from quart import Quart, Response, redirect, render_template

from comics import ComicScraper
from constants import (
    ALT_DATE_FMT,
    DB_TIMEOUT,
    FETCH_TIMEOUT,
    FIRST_COMIC,
    MAX_DB_CONN,
    MAX_FETCH_CONN,
    REPO,
    SRC_PREFIX,
)
from latest import LatestDateScraper
from utils import curr_date, date_to_str, str_to_date

app = Quart("Dilbert Viewer", static_url_path="")


async def _init_db_pool() -> None:
    """Initialize the database connection pool for caching data."""
    # Heroku needs SSL for its PostgreSQL DB, but has issues with verifying
    # the certificate. So simply disable verification while keeping SSL.
    ctx = ssl.create_default_context(cafile="")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    app.db_pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        command_timeout=DB_TIMEOUT,
        min_size=1,
        max_size=MAX_DB_CONN,
        ssl=ctx,
    )


async def _init_client_sess() -> None:
    """Initialize the aiohttp session for scraping comics."""
    # Limit max connections to "dilbert.com", else we might get blocked
    connector = aiohttp.TCPConnector(limit=MAX_FETCH_CONN)
    timeout = aiohttp.ClientTimeout(sock_connect=FETCH_TIMEOUT)
    app.client_sess = aiohttp.ClientSession(
        connector=connector, timeout=timeout
    )


@app.before_serving
async def create_aux() -> None:
    """Initialize and store auxiliary items.

    The auxiliary items are:
        * The database connection pool for caching data
        * The aiohttp session for scraping comics
        * The scrapers for the comics and the latest comic date
    """
    # Initialize independent components in parallel
    await asyncio.gather(_init_db_pool(), _init_client_sess())

    # Initialization of scrapers depends on the DB pool and the aiohttp
    # client session. Hence, this can't be done in the above
    # `asyncio.gather`.
    app.comic_scraper = ComicScraper(app.db_pool, app.client_sess, app.logger)
    app.latest_date_scraper = LatestDateScraper(
        app.db_pool, app.client_sess, app.logger
    )


@app.after_serving
async def close_aux() -> None:
    """Gracefully close the auxiliary items."""
    # Close independent components in parallel
    await asyncio.gather(app.db_pool.close(), app.client_sess.close())


async def _serve_template(date: str, data: dict, latest_comic: str) -> str:
    """Serve the HTML given scraped data.

    Both input dates must be in the format used by "dilbert.com".

    Args:
        date: The (possibly corrected) date of the comic
        data: The scraped comic data
        latest_comic: The date of the latest comic

    Returns:
        The rendered template for the comic page
    """
    date_obj = str_to_date(date)

    # Links to previous and next comics
    previous_comic = date_to_str(
        max(str_to_date(FIRST_COMIC), date_obj - timedelta(days=1))
    )
    next_comic = date_to_str(
        min(str_to_date(latest_comic), date_obj + timedelta(days=1))
    )

    # Whether to disable left/right navigation buttons
    disable_left_nav = date == FIRST_COMIC
    disable_right_nav = date == latest_comic

    # Link to original strip on "dilbert.com"
    permalink = SRC_PREFIX + date

    return await render_template(
        "layout.html",
        data=data,
        date=date,
        first_comic=FIRST_COMIC,
        previous_comic=previous_comic,
        next_comic=next_comic,
        disable_left_nav=disable_left_nav,
        disable_right_nav=disable_right_nav,
        permalink=permalink,
        repo=REPO,
    )


async def serve_comic(
    date: str, *, allow_redirect: bool = True
) -> Union[str, Response]:
    """Serve the requested comic.

    Args:
        date: The date of the requested comic, in the format used by
            "dilbert.com"
        allow_redirect: If there is no comic found for this date, then
            whether to redirect to the correct date

    Returns:
        The rendered template for the comic page
    """
    # Execute both in parallel, as they are independent of each other
    data, latest_comic = await asyncio.gather(
        app.comic_scraper.get_comic_data(date),
        app.latest_date_scraper.get_latest_date(),
    )

    # This date differs from the input date if the input is invalid (i.e.
    # "dilbert.com" would redirect to a comic with a different date).
    actual_date_obj = str_to_date(data["dateStr"], fmt=ALT_DATE_FMT)
    actual_date = date_to_str(actual_date_obj)

    # Replicates the behaviour of "dilbert.com" by redirecting to the correct
    # date.
    if allow_redirect and actual_date != date:
        return redirect(f"/{actual_date}")

    # This will contain awaitables for caching data (if required) and rendering
    # the template. They are both independent of each other, and thus can be
    # run in parallel.
    todos = []

    # The date of the latest comic is often retrieved from the cache. If
    # "dilbert.com" has redirected to a date which is newer than the cached
    # value, then there is a new "latest comic". So cache the answer of
    # "dilbert.com".
    if str_to_date(latest_comic) < actual_date_obj:
        latest_comic = actual_date
        todos.append(app.latest_date_scraper.update_latest_date(actual_date))

    todos.append(_serve_template(actual_date, data, latest_comic))
    results = await asyncio.gather(*todos)
    return results[-1]  # this is the rendered template


@app.route("/")
async def latest_comic() -> str:
    """Serve the latest comic."""
    # If there is no comic for this date yet, "dilbert.com" will auto-redirect
    # to the latest comic.
    today = date_to_str(curr_date())

    # If there is no comic for this date yet, we still want to keep this as the
    # homepage, as a redirection would alter the URL, and lead to slower
    # loading.
    return await serve_comic(today, allow_redirect=False)


@app.route("/<int:year>-<int:month>-<int:day>")
async def comic_page(year: int, month: int, day: int) -> Union[str, Response]:
    """Serve the requested comic from the given URL."""
    # This depends on the format given by `DATE_FMT` from constants.py
    date = f"{year:04d}-{month:02d}-{day:02d}"

    # Check to see if the date is invalid
    try:
        str_to_date(date)
    except ValueError:
        # Replicates the behaviour of "dilbert.com" by redirecting to the
        # homepage.
        return redirect("/")

    return await serve_comic(date)


@app.route("/random")
async def random_comic() -> Response:
    """Serve a random comic."""
    first = str_to_date(FIRST_COMIC)
    latest = curr_date()
    rand_date = date_to_str(random.uniform(first, latest))  # type: ignore
    # If there is no comic for this date yet, "dilbert.com" will auto-redirect
    # to the latest comic.
    return redirect(f"/{rand_date}")
