"""Customized panes used by Geo:N:G"""

# Third party imports
import panel as pn

# Geo:N:G imports
from geong_common import files


def headline(param):
    """Create an HTML headline pane for the given parameter"""
    text = f"<b>{param.label}</b>"
    if param.doc:
        text += f" [<abbr>?<span>{param.doc}</span></abbr>]"

    return pn.pane.HTML(text, css_classes=["headline"])


def markdown_from_url(url):
    """Create a Markdown pane by getting the markdown string from a URL"""
    markdown = files.get_url_or_asset(url, local_assets="app.assets").read_text()
    return pn.pane.Markdown(markdown)
