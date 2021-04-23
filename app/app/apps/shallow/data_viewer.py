"""Data Viewer for Geo:N:G"""

# Third party imports
import panel as pn
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes

# Read configuration
*_, PACKAGE, APP, VIEW = __name__.split(".")
CFG = config.app[PACKAGE][APP][VIEW]


@pyplugs.register
def view():
    """Show the underlying data in a downloadable table"""
    return [
        pn.pane.Markdown(f"# {CFG.label}"),
        panes.data_viewer(
            dataset=APP,
            tables=CFG.tables,
            columns_per_table=CFG.columns.as_dict(),
            name=CFG.label,
            pagination="remote",
            page_size=CFG.page_size,
            show_index=False,
        ),
    ]
