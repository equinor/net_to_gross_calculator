"""Entry point for Geo:N:G

Geo:N:G has different parts based on the underlying data, include Deep Water and
Shallow Marine. Each of these parts is referred to as an app in the code. Each
app consists of several different views like instructions, workflow, data viewer
etc.
"""

# Third party imports
import panel as pn
import pyplugs
from codetiming import Timer

# Geo:N:G imports
from app import config
from app.assets import state
from geong_common import files
from geong_common.log import logger

# Read configuration
*_, PACKAGE = __name__.split(".")
CFG = config.app[PACKAGE]

# Initialize Panel
_STYLE = config.app.style
pn.extension(
    raw_css=[
        files.get_url_or_asset(css, local_assets="app.assets").read_text()
        for css in _STYLE.raw_css
    ],
    css_files=_STYLE.css_files,
)


def get_view(app, view):
    """Get a view from a given app"""
    with Timer(text=f"Added view {app}:{view} in {{:.2f}} seconds", logger=logger.time):
        return pyplugs.call(package=f"{__package__}.{app}", plugin=view)


def view():
    """The main layout of the Geo:N:G app"""
    layout = pn.template.BootstrapTemplate(
        title=CFG.title,
        theme=pn.template.theme.DefaultTheme,
        logo=str(
            files.get_url_or_asset(_STYLE["logo"], local_assets="app.assets").resolve()
        ),
        header_color=_STYLE.header_color,
        header_background=_STYLE.header_background,
        favicon=str(
            files.get_url_or_asset(
                _STYLE["favicon"], local_assets="app.assets"
            ).resolve()
        ),
    )

    # Header strip
    header_canvas = pn.pane.Markdown(
        f"#### {CFG[CFG.primary_app].label}", sizing_mode="stretch_width"
    )
    layout.header.append(header_canvas)

    # Main view
    view_canvas = pn.Column(sizing_mode="stretch_both")
    layout.main.append(view_canvas)

    # Left sidebar
    sidebar_menu = create_menu(
        header_canvas=header_canvas,
        view_canvas=view_canvas,
        sizing_mode="stretch_width",
    )
    layout.sidebar.append(sidebar_menu)

    # Initialize main view with a splash screen
    view_canvas[:] = create_splash(
        header_canvas=header_canvas,
        view_canvas=view_canvas,
        sidebar_menu=sidebar_menu,
        sizing_mode="stretch_both",
    )

    return layout


def create_splash(header_canvas, view_canvas, sidebar_menu, **layout_args):
    """Create a splash screen shown when app is starting up

    Use spacers to center button row on screen.
    """
    splash_row = pn.Row(pn.layout.HSpacer(), pn.layout.HSpacer(), **layout_args)
    for app in CFG.apps:
        app_button = pn.widgets.Button(name=CFG[app].label)
        app_button.on_click(
            _update_view_factory(
                header_canvas, view_canvas, sidebar_menu, app, CFG[app].primary_view
            )
        )
        splash_row.insert(-1, app_button)

    return [pn.layout.VSpacer(), splash_row, pn.layout.VSpacer()]


def create_menu(header_canvas, view_canvas, **layout_args):
    """Create a sidebar menu based on an Accordion layout"""
    menu = pn.Accordion(
        toggle=True, active=[CFG.apps.index(CFG.primary_app)], **layout_args
    )

    for app in CFG.apps:
        view_labels = ", ".join(v.label for v in CFG[app].sections)
        logger.debug(f"Adding menu for {CFG[app].label} with views {view_labels}")

        app_menu = pn.Column(**layout_args)
        for view in CFG[app].views:
            view_button = pn.widgets.Button(
                name=CFG[app][view].label, css_classes=["menu-view"]
            )
            view_button.on_click(
                _update_view_factory(
                    header_canvas, view_canvas, menu, app, view, view_button
                )
            )
            app_menu.append(view_button)
        menu.append((CFG[app].label, app_menu))

    return menu


def _update_view_factory(
    header_canvas, view_canvas, sidebar_menu, app, view, button=None
):
    """Create a callback that can update the canvas"""
    if button is not None:
        (
            state.get_user_state()
            .setdefault(app, {})
            .setdefault("update_view", {})[view]
        ) = button

    def update_view(event):
        """Update canvas to show the given app/view"""
        header_canvas.object = f"#### {CFG[app].label}"
        view_canvas[:] = get_view(app=app, view=view)
        sidebar_menu.active = [sidebar_menu._names.index(CFG[app].label)]

    return update_view
