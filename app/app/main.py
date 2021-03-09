"""Entry point when using panel serve

This file is run when starting Geo:N:G with a command like

    $ panel serve app
"""

# Geo:N:G imports
from app import apps
from app import config
from geong_common import log

# Serve main view of app
if __name__.startswith("bokeh"):
    log.init()
    apps.view().servable(title=config.app.apps.title)
