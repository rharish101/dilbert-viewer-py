"""All constants used by this web page."""
from typing_extensions import Final

# ==================================================
# Date formats
# ==================================================
FIRST_COMIC: Final = "1989-04-16"  # date of the first ever Dilbert comic
DATE_FMT: Final = "%Y-%m-%d"  # date format used for URLs on "dilbert.com"
# Date format used for display with the comic on "dilbert.com"
ALT_DATE_FMT: Final = "%A %B %d, %Y"

# ==================================================
# Parameters for scraping from "dilbert.com"
# ==================================================
# Limit for connections to "dilbert.com"
MAX_FETCH_CONN: Final = 20
# Timeout (in seconds) for establishing a connection
FETCH_TIMEOUT: Final = 3

# ==================================================
# Parameters for caching to the database
# ==================================================
# Limit for connections to the cache database. Heroku's free tier limit is 20.
MAX_DB_CONN: Final = 19
# Timeout (in seconds) for a single database operation
DB_TIMEOUT: Final = 3
# Limit (in no. of comics) for the comics cache in the database. Heroku's free
# tier limit is 10,000 rows in a database with max. size 1GB. Note that apart
# from this, we have the latest date table, which always has exactly one row.
CACHE_LIMIT: Final = 9900
# No. of hrs after scraping the latest date when it is to be scraped again
LATEST_DATE_REFRESH: Final = 2

# ==================================================
# Miscellaneous
# ==================================================
# URL prefix for each comic on "dilbert.com"
SRC_PREFIX: Final = "https://dilbert.com/strip/"
# Link to the public version of this repo; mainly for publicity :P
REPO: Final = "https://github.com/rharish101/dilbert-viewer"
