"""Scraper to get info on the latest Dilbert comic."""
from datetime import datetime

from constants import LATEST_DATE_REFRESH, SRC_PREFIX
from scraper import Scraper
from utils import date_to_str, str_to_date


class LatestDateScraper(Scraper):
    """Class to scrape the date of the latest Dilbert comic.

    This scraper returns that date in the format used by "dilbert.com".
    """

    async def get_cached_data(self):
        """Get the cached latest date from the database.

        If the latest date is stale (ie. was updated a long time back), or it
        wasn't found in the cache, None is returned.
        """
        async with self.pool.acquire() as conn:
            date = await conn.fetchval(
                "SELECT latest FROM latest_date WHERE last_check >= "
                "CURRENT_TIMESTAMP - INTERVAL '1 hour' * $1;",
                LATEST_DATE_REFRESH,
            )

        if date is not None:
            date = date_to_str(date)

        return date

    async def cache_data(self, date):
        """Cache the latest date into the database."""
        # WHERE condition is not required as there is always only one row in
        # this table.
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE latest_date SET latest = $1, last_check = DEFAULT;",
                str_to_date(date),
            )

        if int(result.split()[1]) > 0:
            self.logger.info("Successfully updated latest date in cache")
            return

        # No rows were updated, so the table must be empty
        self.logger.info(
            "Couldn't update latest date in cache; trying to insert it"
        )

        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO latest_date (latest) VALUES ($1);",
                str_to_date(date),
            )

    async def scrape_data(self):
        """Scrape the date of the latest comic from "dilbert.com"."""
        latest = date_to_str(datetime.now())
        url = SRC_PREFIX + latest
        async with self.sess.get(url) as resp:
            self.logger.debug(f"Got response for latest date: {resp.status}")
            return resp.url.path.split("/")[-1]
