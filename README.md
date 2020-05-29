# Dilbert Viewer

A simple comic viewer for Dilbert by Scott Adams, hosted on Heroku [here](https://dilbert-viewer.herokuapp.com).
It uses the Heroku PostgreSQL addon for caching.

## Instructions
Run the script `cache_init.sql` at the beginning to create the required tables in the cache:
```sh
heroku pg:psql -a dilbert-viewer -f cache_init.sql
```

### Local Testing
1. Install all required Python dependencies (with Python 3.8+):
    ```sh
    pip install -r requirements.txt
    ```

2. Run the viewer locally:
    ```sh
    DATABASE_URL=$(heroku config:get DATABASE_URL -a dilbert-viewer) heroku local web
    ```

### For Contributing
1. Install extra dependencies for development:
    ```sh
    pip install -r requirements-dev.txt
    ```

2. Install pre-commit hooks:
    ```sh
    pre-commit install
    ```

**NOTE**: You need to be inside the virtual environment where you installed the above dependencies every time you commit.
