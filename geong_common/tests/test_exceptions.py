"""Test Geo:N:G exceptions"""

# Third party imports
import pytest

# Geo:N:G imports
from geong_common import exceptions


def test_geong_error_can_be_instatiated():
    with pytest.raises(exceptions.GeongError):
        raise exceptions.GeongError(user_message="user", log_message="log")


def test_missing_access_token_error_can_be_instatiated():
    with pytest.raises(exceptions.MissingAccessTokenError):
        raise exceptions.MissingAccessTokenError(user_message="user", log_message="log")


def test_api_response_error_can_be_instatiated():
    with pytest.raises(exceptions.APIResponseError):
        raise exceptions.APIResponseError(
            user_message="user", status_code=404, reason="because"
        )
