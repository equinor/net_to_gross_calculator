"""Data Viewer for Geo:N:G"""

# Third party imports
import panel as pn
import pyplugs

# Geo:N:G imports
from app import config

# Read configuration
*_, PACKAGE, APP, VIEW = __name__.split(".")
CFG = config.app[PACKAGE][APP][VIEW]


@pyplugs.register
def view():
    return [pn.pane.Markdown("# Data Viewer")]
