"""All constants used by this web page."""
from typing import Optional

from typing_extensions import Final

# ==================================================
# Date formats
# ==================================================
FIRST_COMIC: Final[str] = "1989-04-16"  # date of the first Dilbert comic ever
DATE_FMT: Final[str] = "%Y-%m-%d"  # date format used for URLs
ALT_DATE_FMT: Final[str] = "%A %B %d, %Y"  # date format used for display

# ==================================================
# Parameters for scraping from "dilbert.com"
# ==================================================
# Limit for connections to "dilbert.com"
MAX_FETCH_CONN: Final[int] = 20
# Timeout (in seconds) for establishing a connection
FETCH_TIMEOUT: Final[Optional[float]] = 3

# ==================================================
# Parameters for caching to the database
# ==================================================
MAX_DB_CONN: Final[int] = 10  # limit for connections to database
# Timeout (in seconds) for a single database operation
DB_TIMEOUT: Final[Optional[float]] = 3
# Limit (in no. of comics) for the comics cache in the database. Heroku's free
# tier limit is 10,000.
CACHE_LIMIT: Final[int] = 9000
# No. of hrs after scraping the latest date when it is to be queried again
LATEST_DATE_REFRESH: Final[int] = 2

# ==================================================
# Miscellaneous
# ==================================================
# URL prefix for each comic on "dilbert.com"
SRC_PREFIX: Final[str] = "https://dilbert.com/strip/"
# Link to the public repo; mainly for publicity :P
REPO: Final[str] = "https://github.com/rharish101/dilbert-viewer"
