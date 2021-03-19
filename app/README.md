# Net to Gross Calculator - Quantitative reservoir predictor

This is a web app built using the [Panel](https://panel.holoviz.org/) library.


## Local installation

1. Install dependencies with Pip:

    ```
    $ python -m pip install -r requirements_dev.txt
    ```

    If you plan only plan to run it, you can install the basic dependencies instead: `requirements.txt`.

2. Install the app. The `-e` option installs the package in _editable_ mode, meaning that you don't need to reinstall the app when you change the source code:

    ```
    $ python -m pip install -e .
    ```


## Running the Net to Gross Calculator

The Net to Gross Calculator is based on [Panel](https://panel.holoviz.org/). You run the app by starting it with `panel serve`:

```
$ python -m panel serve app
```

During development, it could also be useful to run with `--dev`. This will watch your source code files for updates and automatically restart the server:

```
$ python -m panel serve app --dev *.py
```


## Testing the app

Running tests are supported using [Tox](https://tox.readthedocs.io/). This assumes that you have installed the developer dependencies as described [above](#local-installation).

```
$ tox
```

Running `tox` will execute all tests defined in [`tests/`](tests/) as well as run some linters on the codebase:

- [Black](https://black.readthedocs.io/) to check formatting
- [Flake8](https://flake8.pycqa.org/) to check general lint
- [Isort](https://pycqa.github.io/isort/) to check organization of imports

Note that the first time you run `tox` it will build new virtual environments for running tests, which will take a few minutes. The next times you run `tox`, it will reuse the earlier environments and will run significantly faster.


## Docker Support

Use Docker compose in the repo root directory to run Geo:N:G with Docker.
