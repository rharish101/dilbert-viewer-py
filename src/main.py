"""The main file for the viewer app."""
import asyncio
import os
import random
import re
import ssl
from datetime import datetime, timedelta

import aiohttp
import asyncpg
from quart import Quart, redirect, render_template

from comics import ComicScraper
from constants import (
    ALT_DATE_FMT,
    DATE_FMT_REGEX,
    DB_TIMEOUT,
    FETCH_TIMEOUT,
    FIRST_COMIC,
    MAX_DB_CONN,
    MAX_FETCH_CONN,
    REPO,
    SRC_PREFIX,
)
from latest import LatestDateScraper
from utils import date_to_str, str_to_date

app = Quart("Dilbert Viewer")


@app.before_serving
async def create_aux():
    """Initialize and store auxiliary items.

    The auxiliary items are:
        * The database connection pool for caching data
        * The aiohttp session for scraping comics
        * The scrapers for the comics and the latest comic date

    """
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

    # Limit max connections to "dilbert.com", else we might get blocked
    connector = aiohttp.TCPConnector(limit=MAX_FETCH_CONN)
    timeout = aiohttp.ClientTimeout(sock_connect=FETCH_TIMEOUT)
    app.client_sess = aiohttp.ClientSession(
        connector=connector, timeout=timeout
    )

    app.comic_scraper = ComicScraper(app.db_pool, app.client_sess, app.logger)
    app.latest_date_scraper = LatestDateScraper(
        app.db_pool, app.client_sess, app.logger
    )


@app.after_serving
async def close_aux():
    """Gracefully close the auxiliary items."""
    await app.db_pool.close()
    await app.client_sess.close()


async def serve_comic(date):
    """Serve the requested comic.

    Args:
        date (str): The date of the requested comic, in the format used by
            "dilbert.com"

    Returns:
        The rendered template for the comic page

    """
    if re.fullmatch(DATE_FMT_REGEX, date) is None:
        # If there is no comic for this date yet, "dilbert.com" will
        # auto-redirect to the latest comic.
        date = date_to_str(datetime.now())

    # Execute both in parallel, as they are independent of each other
    data, latest_comic = await asyncio.gather(
        app.comic_scraper.get_data(date), app.latest_date_scraper.get_data(),
    )

    # This date differs from the input date if the input is invalid (i.e.
    # "dilbert.com" would redirect to a comic with a different date).
    actual_date_obj = str_to_date(data["dateStr"], fmt=ALT_DATE_FMT)
    actual_date = date_to_str(actual_date_obj)

    # Links to previous and next comics
    previous_comic = date_to_str(
        max(str_to_date(FIRST_COMIC), actual_date_obj - timedelta(days=1))
    )
    next_comic = date_to_str(
        min(str_to_date(latest_comic), actual_date_obj + timedelta(days=1))
    )

    # Whether to disable left/right navigation buttons
    disable_left_nav = actual_date == FIRST_COMIC
    disable_right_nav = actual_date == latest_comic

    # Link to original strip on "dilbert.com"
    permalink = SRC_PREFIX + actual_date

    return await render_template(
        "layout.html",
        data=data,
        date=actual_date,
        first_comic=FIRST_COMIC,
        previous_comic=previous_comic,
        next_comic=next_comic,
        disable_left_nav=disable_left_nav,
        disable_right_nav=disable_right_nav,
        permalink=permalink,
        repo=REPO,
    )


@app.route("/")
async def latest_comic():
    """Serve the latest comic."""
    # If there is no comic for this date yet, "dilbert.com" will auto-redirect
    # to the latest comic.
    today = date_to_str(datetime.now())
    return await serve_comic(today)


@app.route("/<int:year>-<int:month>-<int:day>")
async def comic_page(year, month, day):
    """Serve the requested comic from the given URL."""
    # This depends on the format given by `DATE_FMT` in `constants.py`
    date = f"{year:04d}-{month:02d}-{day:02d}"
    return await serve_comic(date)


@app.route("/random")
async def random_comic():
    """Serve a random comic."""
    first = str_to_date(FIRST_COMIC)
    latest = datetime.now()
    rand_date = date_to_str(random.uniform(first, latest))
    # If there is no comic for this date yet, "dilbert.com" will auto-redirect
    # to the latest comic.
    return redirect(f"/{rand_date}")
