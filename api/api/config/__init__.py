"""Expose Geo:N:G API configuration"""

# Standard library imports
from importlib import resources

# Geo:N:G imports
from geong_common.config import config

# Read API configuration from file
with resources.path(__package__, "") as config_dir:
    api = config.read("api", config_dir)
