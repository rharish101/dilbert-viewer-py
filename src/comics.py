"""Scraper to get info for requested Dilbert comics."""
import re
from asyncio import Lock

from asyncpg import UniqueViolationError

from constants import ALT_DATE_FMT, CACHE_LIMIT, SRC_PREFIX
from scraper import Scraper
from utils import date_to_str, str_to_date


class ComicScraper(Scraper):
    """Class for a comic scraper.

    This scraper takes a date (in the format used by "dilbert.com") and returns
    a dict representing the following info:
        * title: The title of that comic
        * actualDate: The date of the comic to which "dilbert.com" redirected
            when given the requested date
        * dateStr: The above date as a string formatted on "dilbert.com"
            (NOTE: This is different from the format used to fetch comics)
        * imgURL: The URL to the image

    """

    async def get_cached_data(self, date):
        """Get the cached comic data from the database."""
        async with self.pool.acquire() as conn:
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
        self.logger.info("Updating `last_used` for data in cache")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
                str_to_date(date),
            )

        return data

    async def _clean_cache(self):
        """Remove excess rows from the cache."""
        async with self.pool.acquire() as conn:
            approx_rows = await conn.fetchval(
                "SELECT reltuples FROM pg_class WHERE relname = 'comic_cache';"
            )

        self.logger.info(
            f"{approx_rows} rows found in `comic_cache`; limit: {CACHE_LIMIT}"
        )

        if approx_rows < CACHE_LIMIT:
            self.logger.info("No. of rows in `comic_cache` is less than limit")
            return

        self.logger.info(
            "No. of rows in `comic_cache` exceeds limit; cleaning"
        )
        async with self.pool.acquire() as conn:
            await conn.execute(
                """DELETE FROM comic_cache
                WHERE ctid in
                (SELECT ctid FROM comic_cache ORDER BY last_used LIMIT $1);""",
                approx_rows - CACHE_LIMIT + 1,
            )

    async def cache_data(self, data, date):
        """Cache the comic data into the database."""
        # This lock ensures that the no. of rows in the cache doesn't increase.
        # This can happen, as the code involves first clearing excess rows,
        # then adding a new row. Therefore, the following can increase the no.
        # of rows:
        #   1. Coroutine 1 clears excess rows
        #   2. Coroutine 2 clears no excess rows, as coroutine 1 did them
        #   3. Coroutine 1 adds its row
        #   4. Coroutine 2 adds its row
        async with Lock():
            try:
                await self._clean_cache()
            except Exception as ex:
                # This means that there will be some extra rows in the cache.
                # As the row limit is a little conservative, this is not a big
                # issue.
                self.logger.error(f"Failed to clean cache: {ex}")
                self.logger.debug("", exc_info=True)

            date = str_to_date(date)

            try:
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO comic_cache (comic, img_url, title)"
                        "VALUES ($1, $2, $3);",
                        date,
                        data["imgURL"],
                        data["title"],
                    )
            except UniqueViolationError:
                # This comic date exists, so simply update `last_used` later
                self.logger.warn(
                    f"Trying to cache date {date}, which is already cached."
                )
            else:
                return  # succeeded in inserting to cache

        # The lock isn't needed here, as this command cannot increase the no.
        # of rows in the cache.
        self.logger.info("Now trying to update `last_used` in cache.")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
                date,
            )

    async def scrape_data(self, date):
        """Scrape the comic data of the requested date from "dilbert.com"."""
        url = SRC_PREFIX + date
        async with self.sess.get(url) as resp:
            self.logger.debug(f"Got response for comic: {resp.status}")
            content = await resp.text()

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
            r'<span>([^<]*)</span>[^<]*<span item[pP]rop="copyrightYear">'
            r"([^<]+)</span>",
            content,
        )
        data["dateStr"] = " ".join(match.groups())
        data["actualDate"] = date_to_str(
            str_to_date(data["dateStr"], fmt=ALT_DATE_FMT)
        )

        match = re.search(
            r'<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>', content
        )
        data["imgURL"] = match.groups()[0]

        return data
