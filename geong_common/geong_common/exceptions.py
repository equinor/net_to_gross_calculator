"""Custom exceptions used in Geo:N:G"""

# Third party imports
import panel as pn

# Geo:N:G imports
from geong_common.log import logger


class GeongError(pn.pipeline.PipelineError):
    """Base class for exceptions in the GeoNG application

    Attributes:
        user_message: explanation of the error, showed to the user
        log_message: more technical explanation of the error
    """

    def __init__(self, *, user_message, log_message):
        logger.error(f"{user_message} {log_message}")
        super().__init__(user_message)


class MissingAccessTokenError(GeongError):
    """Access token is missing

    Attributes:
        user_message: explanation of the error, showed to the user
        log_message: more technical explanation of the error
    """


class APIResponseError(GeongError):
    """Response status code from the API is above 400

    Attributes:
        user_message: explanation of the error, showed to the user
        status_code: HTTP response status code
        reason: HTTP response error reason
    """

    def __init__(self, *, user_message, status_code, reason):
        log_message = f"{status_code} API Error: {reason}"
        super().__init__(user_message=user_message, log_message=log_message)
