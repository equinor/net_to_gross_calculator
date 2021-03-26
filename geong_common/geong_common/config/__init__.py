"""Expose Geo:N:G configuration"""

# Standard library imports
import os
from importlib import resources

# Geo:N:G imports
from geong_common.config import config

# Read Geo:N:G common configuration from file
with resources.path(__package__, "") as config_dir:
    geong = config.read("geong", config_dir)

# Add information from environment variables
geong.vars.update(
    {
        "API_URL": os.environ.get(
            "API_URL", "Please set the API_URL environment variable"
        ),
        "DATA_PATH": os.environ.get(
            "DATA_PATH", "Please set the DATA_PATH environment variable"
        ),
    }
)
geong.update_from_env(
    {
        "LOG_LEVEL": ("log", "console", "level"),
        "JSON_LOGS": ("log", "console", "json_logs"),
    },
    converters={"JSON_LOGS": "bool"},
)

# Set up assets directory
with resources.path("geong_common.assets", "") as assets_dir:
    geong.vars.update({"path_assets": str(assets_dir)})

# Simplify access to log configuration
log = geong.log
