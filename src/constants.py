"""All constants used by this web page."""
FIRST_COMIC = "1989-04-16"  # date of the first Dilbert comic ever
DATE_FMT = "%Y-%m-%d"  # date format used by "dilbert.com" for URLs
DATE_FMT_REGEX = r"\d{4}-\d{2}-\d{2}"  # for mild checking of the above format
ALT_DATE_FMT = "%A %B %d, %Y"  # date format used by "dilbert.com" for display

MAX_FETCH_CONN = 20  # limit for connections to "dilbert.com" for scraping
FETCH_TIMEOUT = 3  # timeout in seconds for fetching a comic from "dilbert.com"

MAX_DB_CONN = 10  # limit for connections to database
DB_TIMEOUT = 3  # timeout in seconds for a single database operation
CACHE_LIMIT = 9000  # in no. of comics; Heroku's free tier has a limit of 10k
LATEST_DATE_REFRESH = 2  # hrs after which the latest date needs to be queried

SRC_PREFIX = "https://dilbert.com/strip/"  # prefix for comics on "dilbert.com"
REPO = "https://github.com/rharish101/dilbert-viewer"  # for publicity
