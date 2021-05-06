"""Figures and tables"""

# Third party imports
import holoviews as hv
import pandas as pd
import panel as pn
from bokeh.models.widgets.tables import NumberFormatter


def data_as_dataframe(data, columns):
    """Data as DataFrame used in tables and figures"""
    return (
        pd.DataFrame({k: v for k, v in data.items() if k in columns})
        .rename_axis(index="Elements")
        .loc[:, columns.entry_keys]
    )


def table_elements(data, columns):
    """Table describing the contribution of each element"""
    formatters = {
        "weights": NumberFormatter(format="0 %"),
        "element_net_gross": NumberFormatter(format="0 %"),
        "contribution": NumberFormatter(format="0.0"),
    }

    return pn.widgets.Tabulator(
        data.assign(
            weights=lambda df: df.loc[:, "weights"] / 100,
            element_net_gross=lambda df: df.loc[:, "element_net_gross"] / 100,
        ),
        titles=columns.as_dict(),
        layout="fit_data_fill",
        formatters=formatters,
        sizing_mode="stretch_width",
    )


def figure_weights(data, columns):
    """Bar plot of weights and contributions of each element"""
    return pn.pane.HoloViews(
        hv.Bars(
            data.loc[:, ["weights", "contribution"]]
            .rename(columns=columns)
            .reset_index()
            .iloc[::-1]
            .melt(id_vars=["Elements"], value_vars=["Weight", "Contribution"]),
            kdims=["Elements", "variable"],
            vdims=["value"],
        ).opts(invert_axes=True, multi_level=False, legend_position="bottom_right"),
        sizing_mode="stretch_width",
    )
