"""All constants used by this web page."""
from typing_extensions import Final

FIRST_COMIC: Final = "1989-04-16"  # date of the first Dilbert comic ever
DATE_FMT: Final = "%Y-%m-%d"  # date format used for URLs
ALT_DATE_FMT: Final = "%A %B %d, %Y"  # date format used for display

MAX_FETCH_CONN: Final = 20  # limit for connections for scraping
FETCH_TIMEOUT: Final = 3  # timeout in seconds for fetching a comic

MAX_DB_CONN: Final = 10  # limit for connections to database
DB_TIMEOUT: Final = 3  # timeout in seconds for a single database operation
CACHE_LIMIT: Final = 9000  # no. of comics; Heroku's free tier limits it to 10k
LATEST_DATE_REFRESH: Final = 2  # hrs after which latest date is to be queried

SRC_PREFIX: Final = "https://dilbert.com/strip/"  # "dilbert.com" comic prefix
REPO: Final = "https://github.com/rharish101/dilbert-viewer"  # for publicity
