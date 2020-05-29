"""Scraper to get info for requested Dilbert comics."""
import asyncio
import re
from html import unescape

from asyncpg import UniqueViolationError

from constants import ALT_DATE_FMT, CACHE_LIMIT, SRC_PREFIX
from scraper import Scraper, ScrapingException
from utils import date_to_str, str_to_date


class ComicScraper(Scraper):
    """Class for a comic scraper.

    This scraper takes a date (in the format used by "dilbert.com") as input.
    It returns a dict representing the following info:
        * title: The title of that comic
        * dateStr: The date of that comic as displayed on "dilbert.com"
        * imgURL: The URL to the comic image

    NOTE: The value for the key "dateStr" represents the date in a format which
    is different from the format used to fetch comics. Also, this date can be
    different from the given date, as "dilbert.com" can redirect to a different
    date. This redirection only happens if the input date in invalid.

    """

    async def _update_last_used(self, date):
        """Update the last used date for the given comic."""
        self.logger.info("Updating `last_used` for data in cache")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
                str_to_date(date),
            )

    async def get_cached_data(self, date):
        """Get the cached comic data from the database."""
        async with self.pool.acquire() as conn:
            # The other columns in the table are: `comic`, `last_used`. `comic`
            # is not required here, as we already have the date as a function
            # argument. In case the date given here is invalid (i.e. it would
            # redirect to a comic with a different date), we cannot retrieve
            # the correct date from the cache, as we aren't caching the mapping
            # of incorrect:correct dates. `last_used` will be updated later.
            row = await conn.fetchrow(
                "SELECT img_url, title FROM comic_cache WHERE comic = $1;",
                str_to_date(date),
            )

        if row is None:
            # This means that the comic for this date wasn't cached, or the
            # date is invalid (i.e. it would redirect to a comic with a
            # different date).
            return None

        data = {
            "title": row[1],
            "dateStr": date_to_str(str_to_date(date), fmt=ALT_DATE_FMT),
            "imgURL": row[0],
        }

        # Update `last_used`, so that this comic isn't accidently de-cached. We
        # want to keep the most recently used comics in the cache, and we are
        # currently using this comic. Since this can be run independely in the
        # background, we do so.
        bg_awaitable = self._update_last_used(date)
        asyncio.create_task(bg_awaitable)

        return data

    async def _clean_cache(self):
        """Remove excess rows from the cache."""
        # This is an approximate of the no. of rows in the `comic_cache` table.
        # This is much faster than the accurate measurement, as given here:
        # https://wiki.postgresql.org/wiki/Count_estimate
        async with self.pool.acquire() as conn:
            approx_rows = await conn.fetchval(
                "SELECT reltuples FROM pg_class WHERE relname = 'comic_cache';"
            )

        if approx_rows < CACHE_LIMIT:
            self.logger.info(
                f"No. of rows in `comic_cache` ({approx_rows}) is less than "
                f"the limit ({CACHE_LIMIT})"
            )
            return

        rows_to_clear = approx_rows - CACHE_LIMIT + 1
        self.logger.info(
            f"No. of rows in `comic_cache` ({approx_rows}) exceeds the limit "
            f"({CACHE_LIMIT}); now clearing the oldest {rows_to_clear} rows"
        )
        async with self.pool.acquire() as conn:
            await conn.execute(
                """DELETE FROM comic_cache
                WHERE ctid in
                (SELECT ctid FROM comic_cache ORDER BY last_used LIMIT $1);""",
                rows_to_clear,
            )

    async def cache_data(self, data, date):
        """Cache the comic data into the database."""
        # The given date can be invalid (i.e. we may have been redirected to a
        # comic with a different date), hence get the correct date from the
        # scraped data.
        date = date_to_str(str_to_date(data["dateStr"], fmt=ALT_DATE_FMT))

        # This lock ensures that the no. of rows in the cache doesn't increase.
        # This can happen, as the code involves first clearing excess rows,
        # then adding a new row. Therefore, the following can increase the no.
        # of rows:
        #   1. Coroutine 1 clears excess rows
        #   2. Coroutine 2 clears no excess rows, as coroutine 1 did them
        #   3. Coroutine 1 adds its row
        #   4. Coroutine 2 adds its row
        async with asyncio.Lock():
            try:
                await self._clean_cache()
            except Exception as ex:
                # This crash means that there can be some extra rows in the
                # cache. As the row limit is a little conservative, this should
                # not be a big issue.
                self.logger.error(f"Failed to clean cache: {ex}")
                self.logger.debug("", exc_info=True)

            date_obj = str_to_date(date)

            try:
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        """INSERT INTO comic_cache (comic, img_url, title)
                        VALUES ($1, $2, $3);""",
                        date_obj,
                        data["imgURL"],
                        data["title"],
                    )
            except UniqueViolationError:
                # This comic date exists, so some other coroutine has already
                # cached this date in parallel. So we can simply update
                # `last_used` later (outside the lock).
                self.logger.warn(
                    f"Trying to cache date {date}, which is already cached."
                )
            else:
                return  # succeeded in caching data, so exit

        # This only executes if caching data led to a UniqueViolation error.
        # The lock isn't needed here, as this command cannot increase the no.
        # of rows in the cache.
        self.logger.info("Now trying to update `last_used` in cache.")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE comic_cache SET last_used = DEFAULT WHERE comic = $1;",
                date_obj,
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
            # Some comics don't have a title. This is mostly for older comics.
            data["title"] = ""
        else:
            data["title"] = unescape(match.groups()[0])

        match = re.search(
            r'<date class="comic-title-date" item[pP]rop="datePublished">[^<]*'
            r'<span>([^<]*)</span>[^<]*<span item[pP]rop="copyrightYear">'
            r"([^<]+)</span>",
            content,
        )
        if match is None:
            raise ScrapingException("Error in scraping the date string")
        data["dateStr"] = " ".join(match.groups())

        match = re.search(
            r'<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>', content
        )
        if match is None:
            raise ScrapingException("Error in scraping the image's URL")
        data["imgURL"] = match.groups()[0]

        return data
