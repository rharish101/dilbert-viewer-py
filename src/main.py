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

from comics import get_comic_data
from constants import (
    DB_TIMEOUT,
    FETCH_TIMEOUT,
    FIRST_COMIC,
    MAX_DB_CONN,
    MAX_FETCH_CONN,
    REPO,
    SRC_PREFIX,
)
from latest import get_latest_comic
from utils import date_to_str, str_to_date

app = Quart("Dilbert Viewer")


@app.before_serving
async def create_aux():
    """Initialize and store auxiliary items.

    The auxiliary items are:
        * The database connection pool for caching data
        * The aiohttp session for scraping comics

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

    connector = aiohttp.TCPConnector(limit=MAX_FETCH_CONN)
    timeout = aiohttp.ClientTimeout(sock_connect=FETCH_TIMEOUT)
    app.client_sess = aiohttp.ClientSession(
        connector=connector, timeout=timeout
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
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) is None:
        # If there is no comic for this date yet, "dilbert.com" will
        # auto-redirect to the latest comic.
        date = date_to_str(datetime.now())

    data, latest_comic = await asyncio.gather(
        get_comic_data(date, app.db_pool, app.client_sess),
        get_latest_comic(app.db_pool, app.client_sess),
    )

    # Links to previous and next comics
    previous_comic = date_to_str(
        max(
            str_to_date(FIRST_COMIC),
            str_to_date(data["actualDate"]) - timedelta(days=1),
        )
    )
    next_comic = date_to_str(
        min(
            str_to_date(latest_comic),
            str_to_date(data["actualDate"]) + timedelta(days=1),
        )
    )

    # Whether to disable left/right navigation buttons
    disable_left_nav = data["actualDate"] == FIRST_COMIC
    disable_right_nav = data["actualDate"] == latest_comic

    # Link to original strip on "dilbert.com"
    permalink = SRC_PREFIX + data["actualDate"]

    return await render_template(
        "layout.html",
        data=data,
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
    date = f"{year:04d}-{month:02d}-{day:02d}"
    return await serve_comic(date)


@app.route("/random")
async def random_comic():
    """Serve a random comic."""
    first = str_to_date(FIRST_COMIC)
    latest = datetime.now()
    rand_date = date_to_str(random.uniform(first, latest))
    return redirect(f"/{rand_date}")
