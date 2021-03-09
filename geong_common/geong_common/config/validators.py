# Standard library imports
import sys
from functools import lru_cache
from typing import Optional

# Third party imports
from pydantic import BaseSettings
from pydantic.error_wrappers import ValidationError


class AzureSettings(BaseSettings):
    applicationinsights_instrumentation_key: Optional[str]
    context: Optional[str]
    radix_environment: Optional[str]


def _system_exit_on_error(s):
    try:
        return s()
    except ValidationError as e:
        sys.exit(str(e))


@lru_cache
def get_azure_settings():
    return _system_exit_on_error(AzureSettings)
