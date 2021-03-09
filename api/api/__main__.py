"""Geo:N:G - Data API

Run a REST API server serving Geo:N:G data.

Version: {version}
"""

# Standard library imports
import logging
import os
import pathlib

# Third party imports
import typer
from dotenv import load_dotenv
from loguru import logger
from uvicorn import Config
from uvicorn import Server

# Geo:N:G imports
import api
from geong_common import log

# Handle environment variables
load_dotenv(f"{pathlib.Path.cwd()}/.env")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()


def main():
    """Dispatch to typer"""
    parse_cli.__doc__ = __doc__.format(version=api.__version__)
    typer.run(parse_cli)


def parse_cli():
    """Run the FastAPI server"""
    # Find numerical value of log level
    try:
        level_num = logger.level(LOG_LEVEL).no
    except ValueError as err:
        logging.error(
            f"Unknown log level {err}. Use one of {', '.join(logger._core.levels)}"
        )
        raise SystemExit()

    # Set up server
    server = Server(
        Config(
            "api.main:app",
            host="0.0.0.0",
            log_level=level_num,
            port=5000,
            proxy_headers=True,
        ),
    )

    # Set up logging last, to make sure no library overwrites it (they
    # shouldn't, but it happens)
    log.init(LOG_LEVEL)

    # Start server
    server.run()


if __name__ == "__main__":
    main()
