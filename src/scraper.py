"""Abstract base class definition for a scraper, and a scraping exception."""
import asyncio
from abc import ABC, abstractmethod
from logging import Logger
from typing import Generic, Optional, TypeVar

from aiohttp import ClientSession
from asyncpg.pool import Pool
from typing_extensions import final

ScrapedData = TypeVar("ScrapedData")
DataRef = TypeVar("DataRef")


class ScrapingException(Exception):
    """Used to indicate that the contents of "dilbert.com" have changed."""


class Scraper(ABC, Generic[ScrapedData, DataRef]):
    """Generic scraper that supports caching of whatever it scrapes.

    Attributes:
        pool: The database connection pool
        sess: The HTTP client session
        logger: The main app logger
    """

    def __init__(
        self, pool: Pool, sess: ClientSession, logger: Logger
    ) -> None:
        """Store the required objects.

        Args:
            pool: The database connection pool
            sess: The HTTP client session
            logger: The main app logger
        """
        self.pool = pool
        self.sess = sess
        self.logger = logger

    @abstractmethod
    async def _get_cached_data(
        self, reference: DataRef
    ) -> Optional[ScrapedData]:
        """Retrieve cached data from the database.

        If data is not found in the cache, None should be returned.
        """

    @abstractmethod
    async def _cache_data(self, data: ScrapedData, reference: DataRef) -> None:
        """Cache data into the database."""

    @abstractmethod
    async def _scrape_data(self, reference: DataRef) -> ScrapedData:
        """Scrape data from the source."""

    @final
    async def _safely_cache_data(
        self, data: ScrapedData, reference: DataRef
    ) -> None:
        """Cache data while handling exceptions."""
        try:
            await self._cache_data(data, reference)
        except Exception as ex:
            # Better to re-scrape later on than crash unexpectedly, so simply
            # log it.
            self.logger.error(f"Caching data failed: {ex}")
            # This logs the crash traceback for debugging purposes
            self.logger.debug("", exc_info=True)

    @final
    async def get_data(self, reference: DataRef) -> ScrapedData:
        """Retrieve the data, either from the source or from cache.

        Args:
            reference: The thing that uniquely identifies the data that is
                requested, i.e. a reference to the requested data

        Returns:
            The requested data
        """
        try:
            data = await self._get_cached_data(reference)
        except Exception as ex:
            # Better to re-scrape now than crash unexpectedly, so simply log it
            self.logger.error(f"Retrieving data from cache failed: {ex}")
            # This logs the crash traceback for debugging purposes
            self.logger.debug("", exc_info=True)
        else:
            if data is not None:
                self.logger.info("Successful retrieval from cache")
                return data

        self.logger.info("Couldn't fetch data from cache; trying to scrape")
        data = await self._scrape_data(reference)
        self.logger.info("Scraped data from source")

        # We already have the data to be returned, so caching the newly scraped
        # data can be done independently in the background.
        bg_awaitable = self._safely_cache_data(data, reference)
        asyncio.create_task(bg_awaitable)

        self.logger.info("Cached scraped data")
        return data
