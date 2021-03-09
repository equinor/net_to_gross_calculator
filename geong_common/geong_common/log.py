"""Set up logging for Geo:N:G

Logging is based on the Loguru library: https://github.com/Delgan/loguru/
"""

# Standard library imports
import functools
import logging
import sys

# Third party imports
from loguru import logger
from loguru._logger import Level
from opencensus.ext.azure.log_exporter import AzureLogHandler
from pyconfs import Configuration

# Geo:N:G imports
from geong_common.config import log as log_config
from geong_common.config.validators import get_azure_settings


class AzureProxyHandler(logging.Handler):
    def __init__(self, connection_string, context, environment):
        super().__init__()
        self._handler = AzureLogHandler(connection_string=connection_string)
        self.context = context
        self.environment = environment

    def emit(self, record):
        record.custom_dimensions = record.extra.get("custom_dimensions", {})
        if self.context is not None:
            record.custom_dimensions["context"] = self.context
        if self.environment is not None:
            record.custom_dimensions["environment"] = self.environment
        self._handler.emit(record)


def init(level: str = log_config.console.level) -> None:
    """Initialize a logger based on configuration settings and options"""
    # Remove the default logger
    logger.remove()

    # Wrap standard library logging calls with loguru
    _intercept_stdlib_logging(level.upper())

    # Configure logging to console (and Docker logs)
    logger.add(
        sys.stdout,
        level=level.upper(),
        format=log_config.console.format,
        serialize=log_config.console.json_logs,
    )

    # Update .is_dev property
    _add_is_dev(level)

    # Configure logging to Azure
    context = get_azure_settings().context
    environment = get_azure_settings().radix_environment
    instrumentation_key = get_azure_settings().applicationinsights_instrumentation_key
    connection_string = f"InstrumentationKey={instrumentation_key}"
    handler = None
    try:
        handler = AzureProxyHandler(connection_string, context, environment)
    except ValueError as e:
        logger.warning(f"Not sending logs to azure app insight: {e}")
    if handler is not None:
        logger.add(
            handler,
            level=log_config.azure.level.upper(),
            format=log_config.azure.format,
            serialize=log_config.azure.json_logs,
        )


def _add_levels(additional_levels: Configuration) -> None:
    """Add custom log levels"""
    for level_cfg in additional_levels.sections:
        # Validate configuration
        level = level_cfg.as_named_tuple(Level)

        # Add level and corresponding method to logger
        logger.level(**level_cfg)
        setattr(
            logger.__class__,
            level.name.lower(),
            functools.partial(logger.log, level.name),
        )


def _add_is_dev(level: str) -> None:
    """Add property identifying DEV (log level <= DEBUG) vs PROD (log level > DEBUG)"""
    setattr(
        logger.__class__,
        "is_dev",
        logger.level(level.upper()).no <= logger.level(log_config.dev_level.upper()).no,
    )


def _intercept_stdlib_logging(level: str):
    """Route log messages using logging in the standard library through loguru

    Based on https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
    """

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Set up InterceptHandler to handle logs done with logging
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logger.level(level).no)

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


# Add custom levels and .is_dev property at import
_add_levels(log_config.custom_levels)
_add_is_dev(log_config.console.level)
