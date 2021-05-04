"""Expose Geo:N:G app configuration"""

# Standard library imports
from importlib import resources

# Geo:N:G imports
from geong_common.config import config

# Read app configuration from file
with resources.path(__package__, "") as config_dir:
    app = config.read("app", config_dir)

# Add information from environment variables
app.update_from_env(
    env_paths={
        "ASSET_IMAGES": ("asset_hosts", "images"),
        "ASSET_INSTRUCTIONS": ("asset_hosts", "instructions"),
        "ASSET_POPUPS": ("asset_hosts", "popups"),
        "RAW_CSS": ("style", "raw_css"),
        "CSS_FILES": ("style", "css_files"),
        "FAVICON": ("style", "favicon"),
        "APP_TITLE": ("apps", "title"),
        "HEADER_BACKGROUND": ("style", "header_background"),
        "HEADER_COLOR": ("style", "header_color"),
        "LOGO": ("style", "logo"),
        "READER": ("apps", "reader"),
    },
    converters={"RAW_CSS": "list", "CSS_FILES": "list"},
)

# Add template to each report
app.update_from_env({"REPORT_TEMPLATE": ("report", "deep_net_gross_ppt", "template")})
app.update_from_env(
    {"REPORT_TEMPLATE": ("report", "shallow_net_gross_ppt", "template")}
)

# Set up asset hosts
app.vars.update({f"ASSET_{k.upper()}": v for k, v in app.asset_hosts.entries})
