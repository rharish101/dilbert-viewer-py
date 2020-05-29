"""Scraper to get info on the latest Dilbert comic."""
from constants import LATEST_DATE_REFRESH, SRC_PREFIX
from scraper import Scraper, ScrapingException
from utils import curr_date, date_to_str, str_to_date


class LatestDateScraper(Scraper[str, None]):
    """Class to scrape the date of the latest Dilbert comic.

    This scraper returns that date in the format used by "dilbert.com".
    """

    async def _get_cached_data(self, _: None = None) -> str:
        """Get the cached latest date from the database.

        If the latest date entry is stale (i.e. it was updated a long time
        back), or it wasn't found in the cache, None is returned.
        """
        async with self.pool.acquire() as conn:
            # The interval for "freshness" of the entry has to be given this
            # way instead of '$1 hours', because of PostgreSQL's syntax.
            # All dates managed by asyncpg are set to UTC.
            date = await conn.fetchval(
                """SELECT latest FROM latest_date
                WHERE last_check >= CURRENT_TIMESTAMP - INTERVAL '1 hour' * $1;
                """,
                LATEST_DATE_REFRESH,
            )

        if date is not None:
            # A "fresh" entry was found
            date = date_to_str(date)

        return date

    async def _cache_data(self, date: str, _: None = None):
        """Cache the latest date into the database."""
        # The WHERE condition is not required as there is always only one row
        # in the `latest_date` table.
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE latest_date SET latest = $1, last_check = DEFAULT;",
                str_to_date(date),
            )

        rows_updated = int(result.split()[1])
        if rows_updated == 1:
            self.logger.info("Successfully updated latest date in cache")
            return
        elif rows_updated > 1:
            raise RuntimeError(
                'The "latest_date" table has more than one row, '
                "i.e. this table is corrupt"
            )

        # No rows were updated, so the "latest_date" table must be empty. This
        # should only happen if this table was cleared manually, or this is the
        # first run of this code on this database.
        self.logger.info(
            "Couldn't update latest date in cache; trying to insert it"
        )

        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO latest_date (latest) VALUES ($1);",
                str_to_date(date),
            )

    async def _scrape_data(self, _: None = None) -> str:
        """Scrape the date of the latest comic from "dilbert.com"."""
        # If there is no comic for this date yet, "dilbert.com" will
        # auto-redirect to the latest comic.
        latest = date_to_str(curr_date())
        url = SRC_PREFIX + latest

        async with self.sess.get(url) as resp:
            self.logger.debug(f"Got response for latest date: {resp.status}")
            date = resp.url.path.split("/")[-1]

        # Check to see if the date is invalid
        try:
            str_to_date(date)
        except ValueError:
            raise ScrapingException(
                "Error in scraping the latest date from the URL"
            )

        return date

    async def get_latest_date(self) -> str:
        """Retrieve the date of the latest comic.

        Returns:
            The latest date
        """
        return await super().get_data(None)

    async def update_latest_date(self, date: str) -> None:
        """Update the latest date in the cache."""
        await self._cache_data(date)
