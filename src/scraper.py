"""Base class definition for a generic scraper that caches."""


class Scraper:
    """Generic scraper that supports caching of whatever it scrapes."""

    def __init__(self, pool, sess, logger):
        """Store the required objects.

        The objects required are:
            * A database connection pool
            * An HTTP client session
            * A logger

        """
        self.pool = pool
        self.sess = sess
        self.logger = logger

    async def get_cached_data(self, *args, **kwargs):
        """Retrieve cached data from the database."""
        raise NotImplementedError("This must be overriden per use case")

    async def cache_data(self, data, *args, **kwargs):
        """Cache data into the database."""
        raise NotImplementedError("This must be overriden per use case")

    async def scrape_data(self, *args, **kwargs):
        """Scrape data from the source."""
        raise NotImplementedError("This must be overriden per use case")

    async def get_data(self, *args, **kwargs):
        """Retrieve the data, either from the source or from cache."""
        try:
            data = await self.get_cached_data(*args, **kwargs)
        except Exception as ex:
            # Better to re-scrape now than crash
            self.logger.error(f"Retrieving data from cache failed: {ex}")
            self.logger.debug("", exc_info=True)
        else:
            if data is not None:
                self.logger.info("Successful retrieval from cache")
                return data

        self.logger.info("Couldn't fetch data from cache; trying to scrape")
        data = await self.scrape_data(*args, **kwargs)
        self.logger.info("Scraped data from source")

        try:
            await self.cache_data(data, *args, **kwargs)
        except Exception as ex:
            # Better to re-scrape later-on than crash now
            self.logger.error(f"Caching data failed: {ex}")
            self.logger.debug("", exc_info=True)
        else:
            self.logger.info("Cached scraped data")

        return data
