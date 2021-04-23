"""Customized panes used by Geo:N:G"""

# Standard library imports
import textwrap

# Third party imports
import panel as pn
import param
from bokeh.models.widgets.tables import NumberFormatter

# Geo:N:G imports
from app import config
from geong_common import files
from geong_common import readers


def headline(param):
    """Create an HTML headline pane for the given parameter"""
    text = f"<b>{param.label}</b>"
    if param.doc:
        text += f" [<abbr>?<span>{param.doc}</span></abbr>]"

    return pn.pane.HTML(text, css_classes=["headline"])


def element_slider(param, quality_param=None):
    """Create a widget with a slider and spinner for an element

    Optionally, a quality bracket button group can be added by specifying
    quality_param
    """
    colors = config.app.style.colors
    widget = pn.Row(
        pn.pane.Markdown(
            f"**{param.label}:**",
            width=150,
            sizing_mode="fixed",
        ),
        pn.widgets.IntSlider.from_param(
            param,
            name="",
            bar_color=colors.get(param.name, colors.default),
            sizing_mode="stretch_width",
            show_value=False,
        ),
        pn.widgets.IntInput.from_param(param, name="", width=120),
    )

    if quality_param is not None:
        widget.append(
            pn.widgets.RadioButtonGroup.from_param(quality_param, button_type="default")
        )

    return widget


def division_slider(
    building_block_type,
    label,
    params,
    param_1,
    param_2,
    param_3=None,
    ignore_param=None,
):
    """Create a slider used to divide the range 0-100 into 2 or 3 parts"""
    colors = config.app.style.colors
    color = colors.get(building_block_type.lower().replace(" ", "_"), colors.default)

    if param_3 is None:
        spinners, slider = _division_slider_with_2_params(params, param_1, param_2)
    else:
        spinners, slider = _division_slider_with_3_params(
            params, param_1, param_2, param_3
        )

    widget = pn.Card(
        pn.Row(pn.layout.HSpacer(), *spinners, pn.layout.HSpacer()),
        pn.Row(slider),
        title=f"{building_block_type}: {label}",
        header_background=color,
        active_header_background=color,
        background="white",
        sizing_mode="stretch_width",
    )

    if ignore_param is not None:
        var_ignore = getattr(params, ignore_param)
        widget.append(
            pn.Row(
                pn.layout.HSpacer(),
                pn.widgets.Checkbox.from_param(var_ignore, width_policy="min"),
                pn.layout.HSpacer(),
            )
        )

        @param.depends(widget.param.collapsed, watch=True)
        def update_ignore_param(collapsed):
            """Set ignore parameter when card is collapsed"""
            params.set_param(**{ignore_param: collapsed})

        @param.depends(var_ignore, watch=True)
        def collapse_card(var_ignore):
            """Collapse card when parameter is ignored"""
            widget.collapsed = var_ignore

    return widget


def _division_slider_with_2_params(params, param_1, param_2):
    """Set up spinners and a slider for 2 params"""
    var_1 = getattr(params, param_1)
    var_2 = getattr(params, param_2)

    spinner_width = 180
    spinners = [
        pn.widgets.IntInput.from_param(var_1, max_width=spinner_width),
        pn.widgets.IntInput.from_param(var_2, max_width=spinner_width),
    ]
    slider = pn.widgets.IntSlider.from_param(
        var_1, name="", tooltips=False, show_value=False, sizing_mode="stretch_width"
    )

    @param.depends(var_2, watch=True)
    def update_param_1(var_2):
        """Update param_1 when param_2 changes"""
        var_2 = min(max(0, var_2), 100)
        params.set_param(**{param_1: 100 - var_2, param_2: var_2})

    @param.depends(var_1, watch=True)
    def update_param_2(var_1):
        """Update param_2 when param_1 changes"""
        var_1 = min(max(0, var_1), 100)
        params.set_param(**{param_1: var_1, param_2: 100 - var_1})

    return spinners, slider


def _division_slider_with_3_params(params, param_1, param_2, param_3):
    """Set up spinners and a slider for 3 params"""

    var_1 = getattr(params, param_1)
    var_2 = getattr(params, param_2)
    var_3 = getattr(params, param_3)

    values = dict(params.get_param_values())
    spinner_width = 120
    spinners = [
        pn.widgets.IntInput.from_param(var_1, max_width=spinner_width),
        pn.widgets.IntInput.from_param(var_2, max_width=spinner_width),
        pn.widgets.IntInput.from_param(var_3, max_width=spinner_width),
    ]
    slider = pn.widgets.IntRangeSlider(
        name="",
        start=0,
        end=100,
        value=(values[param_1], values[param_1] + values[param_2]),
        tooltips=False,
        show_value=False,
        sizing_mode="stretch_width",
    )

    @param.depends(var_1, var_2, watch=True)
    def update_param_3(var_1, var_2):
        var_1 = min(max(0, var_1), 100)
        var_2 = min(max(0, var_2), 100)
        var_3 = max(0, 100 - var_1 - var_2)
        params.set_param(**{param_1: var_1, param_2: var_2, param_3: var_3})
        slider.value = (var_1, var_1 + var_2)

    @param.depends(var_1, var_3, watch=True)
    def update_param_2(var_1, var_3):
        var_1 = min(max(0, var_1), 100)
        var_3 = min(max(0, var_3), 100)
        var_2 = max(0, 100 - var_1 - var_3)
        params.set_param(**{param_1: var_1, param_2: var_2, param_3: var_3})
        slider.value = (var_1, var_1 + var_2)

    @param.depends(var_2, var_3, watch=True)
    def update_param_1(var_2, var_3):
        var_2 = min(max(0, var_2), 100)
        var_3 = min(max(0, var_3), 100)
        var_1 = max(0, 100 - var_2 - var_3)
        params.set_param(**{param_1: var_1, param_2: var_2, param_3: var_3})
        slider.value = (var_1, var_1 + var_2)

    @param.depends(slider.param.value, watch=True)
    def update_from_slider(slider_value):
        start, end = slider_value
        var_1 = min(max(0, start), 100)
        var_2 = min(max(0, end - var_1), 100)
        var_3 = min(max(0, 100 - var_1 - var_2), 100)
        params.set_param(**{param_1: var_1, param_2: var_2, param_3: var_3})

    return spinners, slider


def markdown_from_url(url, **markdown_args):
    """Create a Markdown pane by getting the markdown string from a URL"""
    markdown = files.get_url_or_asset(url, local_assets="app.assets").read_text()
    return pn.pane.Markdown(markdown, **markdown_args)


def warning(text):
    """Create a warning alert pane with the given text"""
    return pn.pane.Alert(f"**Warning:** {textwrap.dedent(text)}", alert_type="danger")


def data_viewer(dataset, tables, columns_per_table, **widget_args):
    """Show all data in a downloadable table"""

    formatters = {
        "ng_vsh40_pct": NumberFormatter(format="0 %"),
        "thickness_mtvd": NumberFormatter(format="0.0"),
        "top_depth_mtvd": NumberFormatter(format="0.0"),
        "base_depth_mtvd": NumberFormatter(format="0.0"),
    }

    table_name = pn.widgets.Select(
        name="Choose table",
        options={t.title(): t for t in tables},
        value=tables[0],
        size=1,
    )

    @pn.depends(table_name.param.value)
    def table(table_name):
        columns = columns_per_table.get(table_name, {})
        data = (
            readers.read_all(config.app.apps.reader, dataset, table_name)
            .loc[:, columns.keys()]
            .assign(ng_vsh40_pct=lambda d: d.ng_vsh40_pct / 100)  # Percent
        )

        return pn.widgets.Tabulator(
            data,
            disabled=True,
            titles=columns,
            formatters=formatters,
            layout="fit_data_table",
            **widget_args,
        )

    return pn.Column(table_name, table, sizing_mode="stretch_width")
