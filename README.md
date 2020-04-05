# Dilbert Viewer

A simple comic viewer for Dilbert by Scott Adams, hosted on Heroku [here](https://dilbert-viewer.herokuapp.com).
It uses the Heroku PostgreSQL addon for caching.

## Instructions
1. Run the script `cache_init.sql` at the beginning to create the required tables in the cache:
    ```sh
    heroku pg:psql -a dilbert-viewer -f cache_init.sql
    ```

2. *[Optional]* Test the viewer locally:
    ```sh
    DATABASE_URL=$(heroku config:get DATABASE_URL -a dilbert-viewer) heroku local web
    ```
