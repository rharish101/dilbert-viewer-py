-- To avoid scraping every time
CREATE TABLE IF NOT EXISTS comic_cache (
  comic DATE NOT NULL,
  img_url VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  last_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (comic)
);

-- For efficient lookup of the oldest comic.
-- This is used for clearing the oldest comic, and enforcing a row limit.
CREATE INDEX IF NOT EXISTS idx_last_used ON comic_cache (last_used);


-- This will only have a single row, for the latest date
CREATE TABLE IF NOT EXISTS latest_date (
  latest DATE NOT NULL,
  last_check TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (latest)
);
