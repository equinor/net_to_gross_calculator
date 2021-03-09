# Standard library imports
import sys
from functools import lru_cache
from typing import Optional

# Third party imports
from pydantic import BaseSettings
from pydantic.error_wrappers import ValidationError


class OAuthSettings(BaseSettings):
    authority: str
    client_id: str
    client_secret: str
    audience: str


class BlobSettings(BaseSettings):
    storage_url: str
    container: str
    folder_name: str


class LogSettings(BaseSettings):
    log_user_info: Optional[bool]


def _system_exit_on_error(s):
    try:
        return s()
    except ValidationError as e:
        sys.exit(str(e))


@lru_cache
def get_oauth_settings():
    return _system_exit_on_error(OAuthSettings)


@lru_cache
def get_blob_settings():
    return _system_exit_on_error(BlobSettings)


@lru_cache
def get_log_settings():
    return _system_exit_on_error(LogSettings)
