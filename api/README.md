# Geo:N:G - Data API

This is a REST API service built using the [FastAPI](https://fastapi.tiangolo.com/) library.


## Local installation

1. Install dependencies with Pip:

    ```
    $ python -m pip install -r requirements_dev.txt
    ```

    If you plan only plan to run Geo:N:G API, you can install the basic dependencies instead: `requirements.txt`.

2. Install Geo:N:G API. The `-e` option installs the package in _editable_ mode, meaning that you don't need to reinstall the app when you change the source code:

    ```
    $ python -m pip install -e .
    ```


## Running Geo:N:G API

Geo:N:G API is installed as an executable, named `geong_api`. You can see basic usage of the executable when running it with the `--help` option.

To run the app for testing and development, you can simply run the executable without any other options or arguments:

```
$ geong_api
```

Run `geong_api --help` for more information.


## Testing Geo:N:G API

Running tests are supported using [Tox](https://tox.readthedocs.io/). This assumes that you have installed the developer dependencies as described [above](#local-installation).

```
$ tox
```

Running `tox` will execute all tests defined in [`tests/`](tests/) as well as run some linters on the codebase:

- [Black](https://black.readthedocs.io/) to check formatting
- [Flake8](https://flake8.pycqa.org/) to check general lint
- [Isort](https://pycqa.github.io/isort/) to check organization of imports

Note that the first time you run `tox` it will build new virtual environments for running tests, which will take a few minutes. The next times you run `tox`, it will reuse the earlier environments and will run significantly faster.


## Environment Variables

Geo:N:G API requires several environment variables to be set. Using a `.env` file is supported when you're running locally. The following `.env` template shows the mandatory environment variables:

```
AUTHORITY=<URL to OAuth authority>
CLIENT_ID=<OAuth client ID>
CLIENT_SECRET=<OAuth client secret>
AUDIENCE=<OAuth audience>
STORAGE_URL=<URL to Azure blob>
CONTAINER=<Name of blob storage container>
FOLDER_NAME=<Folder inside the blob storage container>
```

Additionally, you may set the following environment variables. However, these have defaults that are set in [config/api.toml](api/config/api.toml).

- `LOG_LEVEL`: (`debug`, `info`, `warn`) Minimum log level shown in console. Default value at `log.console.level`.
- `JSON_LOGS`: (`0`, `1`) Format logs using JSON. Default value at `log.console.json_logs`.


## Docker Support

The `Dockerfile` can be used to build a Docker image for Geo:N:G. Build the image as follows:

    $ docker build -t api .

The image can be run using:

    $ docker run --rm -p 5000:5000 --env-file .env api

Note that this assumes you have any [environment variables](#environment-variables) set up in a file named `.env`. In production, the environment variables should be injected using the production system's capabilities.
