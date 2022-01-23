# Dilbert Viewer (Legacy)

A simple comic viewer for Dilbert by Scott Adams.
This is meant to be hosted on Heroku [here](https://dilbert-viewer.herokuapp.com), using the third-party [Python Poetry Buildpack](https://elements.heroku.com/buildpacks/moneymeets/python-poetry-buildpack) with the [Heroku PostgreSQL add-on](https://elements.heroku.com/addons/heroku-postgresql) for caching.

## Deprecation Notice
This is now deprecated in favour of a Rust-based version in [this repository](https://github.com/rharish101/dilbert-viewer).

## Instructions
Run the script `cache_init.sql` at the beginning to create the required tables in the cache:
```sh
heroku pg:psql -a dilbert-viewer -f cache_init.sql
```

### Local Testing
#### Setup
[Poetry](https://python-poetry.org/) is used for conveniently installing and managing dependencies.
The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) is used to locally run the code as specified in the [Procfile](./Procfile).

1. *[Optional]* Create a virtual environment with a compatible Python version (specified in [pyproject.toml](./pyproject.toml)).

2. Install Poetry globally (recommended), or in a virtual environment.
    Please refer to [Poetry's installation guide](https://python-poetry.org/docs/#installation) for recommended installation options.

    You can use pip to install it:
    ```sh
    pip install poetry
    ```

3. Install all dependencies with Poetry:
    ```sh
    poetry install --no-dev
    ```
    If you didn't create and activate a virtual environment in step 1, Poetry creates one for you and installs all dependencies there.

4. Install the Heroku CLI.
    Please refer to [Heroku's installation guide](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) for recommended installation options.

#### Running
1. Activate the virtual environment where you installed the dependencies.
    To use the virtual environment created by Poetry, run:
    ```sh
    poetry shell
    ```

2. Set the required environment variables and run the viewer locally with the Heroku CLI:
    ```sh
    DATABASE_URL=$(heroku config:get DATABASE_URL -a dilbert-viewer) WEB_CONCURRENCY=1 heroku local web
    ```

### For Contributing
[pre-commit](https://pre-commit.com/) is used for managing hooks that run before each commit, to ensure code quality and run some basic tests.
Thus, this needs to be set up only when one intends to commit changes to git.

1. Activate the virtual environment where you installed the dependencies.

2. Install all dependencies, including extra dependencies for development:
    ```sh
    poetry install
    ```

3. Install pre-commit hooks:
    ```sh
    pre-commit install
    ```

**NOTE**: You need to be inside the virtual environment where you installed the above dependencies every time you commit.
However, this is not required if you have installed pre-commit globally.
