# Dilbert Viewer

A simple comic viewer for Dilbert by Scott Adams, hosted on Heroku [here](https://dilbert-viewer.herokuapp.com).
It uses the Heroku PostgreSQL addon for caching.

## Instructions
1. Install `pre-commit` and set it up for Git pre-commit hooks:
    ```sh
    pip install pre-commit
    pre-commit install
    ```

2. Run the script `cache_init.sql` at the beginning to create the required tables in the cache:
    ```sh
    heroku pg:psql -a dilbert-viewer -f cache_init.sql
    ```

3. *[Optional]* Test the viewer locally:
    ```sh
    DATABASE_URL=$(heroku config:get DATABASE_URL -a dilbert-viewer) heroku local web
    ```
