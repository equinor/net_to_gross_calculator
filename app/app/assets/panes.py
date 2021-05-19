"""Customized panes used by Geo:N:G"""

# Standard library imports
import io
import textwrap

# Third party imports
import pandas as pd
import panel as pn
import param
from bokeh.models.widgets.tables import NumberFormatter
from pyconfs.configuration import Variables

# Geo:N:G imports
from app import config
from app.assets import state
from geong_common import files
from geong_common import readers


def headline(label, popup_label=None):
    """Create an HTML headline pane for the given parameter"""
    widget = pn.Row(
        pn.pane.HTML(
            f"<b>{label}</b>", css_classes=["headline"], sizing_mode="stretch_width"
        )
    )
    if popup_label is not None:
        widget.insert(0, pn.pane.HTML(popup(label=popup_label)))

    return widget


def markdown_from_url(url, **markdown_args):
    """Create a Markdown pane by getting the markdown string from a URL"""
    markdown = (
        files.get_url_or_asset(url, local_assets="app.assets")
        .read_text()
        .format_map(Variables(**config.app.vars))
    )
    return pn.pane.Markdown(markdown, **markdown_args)


def warning(text, label="Warning", alert_type="danger"):
    """Create a warning alert pane with the given text"""
    return pn.pane.Alert(f"**{label}:** {textwrap.dedent(text)}", alert_type=alert_type)


def popup(label, text="?"):
    """Create HTML for a popup tip based on a label that corresponds to templates"""
    popup_html = (
        files.get_url_or_asset(
            config.app.asset_hosts.replace("popups"),
            f"{label}.html",
            local_assets="app.assets",
        )
        .read_text()
        .format_map(Variables(**config.app.vars))  # Interpolate with config variables
    )

    return f"[<abbr>{text}<span>{popup_html}</span></abbr>]"


def pipeline_button(app, text, trigger, button_type="success", width=125):
    """Trigger a parameter on the pipeline"""

    def trigger_param(event):
        """Trigger a parameter"""
        pipeline = state.get_user_state().get(app, {}).get("pipeline")
        if not pipeline:
            raise ValueError("No pipeline is available")

        pipeline.param.trigger(trigger)

    button = pn.widgets.Button(name=text, button_type=button_type, width=width)
    button.on_click(trigger_param)
    return button


def next_stage_button(app, text="Next", button_type="success"):
    """Trigger the next stage"""
    return pipeline_button(app, text=text, trigger="next", button_type=button_type)


def previous_stage_button(app, text="Previous", button_type="default"):
    """Trigger the previous stage"""
    return pipeline_button(app, text=text, trigger="previous", button_type=button_type)


def multiple_choice(param, popup_label=None):
    """Create a multiple choice widget"""
    return pn.Column(
        headline(param.label, popup_label=popup_label),
        pn.widgets.RadioBoxGroup.from_param(param),
    )


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
    popup_label=None,
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

    if popup_label is not None:
        widget[-1].append(popup(label=popup_label))

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


def data_viewer(dataset, tables, columns_per_table, **widget_args):
    """Show all data in a downloadable table"""

    formatters = {
        "ng_vsh40_pct": NumberFormatter(format="0 %"),
        "thickness_mtvd": NumberFormatter(format="0.0"),
        "top_depth_mtvd": NumberFormatter(format="0.0"),
        "base_depth_mtvd": NumberFormatter(format="0.0"),
    }

    def get_filename(table):
        return f"{dataset}-{table}.xlsx"

    def get_data(table_name):
        columns = columns_per_table.get(table_name, {})
        return (
            readers.read_all(config.app.apps.reader, dataset, table_name)
            .loc[:, columns.keys()]
            .sort_values(by="ng_vsh40_pct", ascending=False)
            .reset_index(drop=True)
        )

    table_name = pn.widgets.Select(
        name="Choose table",
        options={t.title(): t for t in tables},
        value=tables[0],
        size=1,
    )
    filename = pn.widgets.TextInput(
        name="File name", value=get_filename(table_name.value)
    )

    @pn.depends(table_name.param.value)
    def table(table_name):
        data = get_data(table_name).assign(
            ng_vsh40_pct=lambda d: d.ng_vsh40_pct / 100  # Show N:G as percent
        )

        return pn.widgets.Tabulator(
            data,
            disabled=True,
            titles=columns_per_table[table_name],
            formatters=formatters,
            layout="fit_data_table",
            **widget_args,
        )

    @pn.depends(table_name.param.value, watch=True)
    def update_filename(table_name):
        filename.value = get_filename(table_name)

    def download_file():
        """Download data as an Excel file"""
        output_bytes = io.BytesIO()

        # Write data as Excel
        excel_writer = pd.ExcelWriter(output_bytes, engine="xlsxwriter")
        get_data(table_name.value).to_excel(
            excel_writer, sheet_name=table_name.value.title(), index=False
        )
        excel_writer.save()

        # Reset output stream and return it
        output_bytes.seek(0)
        return output_bytes

    @pn.depends(filename.param.value)
    def download_button(filename):
        return pn.widgets.FileDownload(
            callback=download_file, filename=filename, button_type="success"
        )

    return pn.Row(
        pn.Column(
            table_name,
            filename,
            download_button,
        ),
        pn.Column(table, sizing_mode="stretch_width"),
    )
