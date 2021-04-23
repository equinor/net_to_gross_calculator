"""Instructions for how to use the Net to Gross Calculator"""

# Third party imports
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes

# Read configuration
*_, PACKAGE, APP, VIEW = __name__.split(".")
CFG = config.app[PACKAGE][APP][VIEW]


@pyplugs.register
def view():
    return [
        panes.markdown_from_url(CFG.replace("url")),
    ]
