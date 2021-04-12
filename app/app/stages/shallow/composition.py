"""Second stage: Composition"""

# Standard library imports
import re

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes
from app.assets import state
from geong_common import config as geong_config
from geong_common import readers
from geong_common.log import logger

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")


# Get list of elements from model configuration
ELEMENT_OPTIONS = {
    section.label: name
    for name, section in geong_config.geong.models.shallow.section_items
}
QUALITY_OPTIONS = {
    "Poor": "Poor <30% NG",
    "Moderate": "Moderate 30-65% NG",
    "Good": "Good 65-85% NG",
    "Exceptional": "Exceptional 85-100% NG",
}
ALL_ELEMENTS = list(ELEMENT_OPTIONS.values())
ALL_QUALITIES = [f"{e}_quality" for e in ALL_ELEMENTS]


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    initial_values = param.Dict()
    report_from_set_up = param.Dict()

    # Parameters for the current stage
    composition_headline = param.String(label="Element Composition")
    sum_to_100 = param.Boolean(default=True)
    net_gross = param.Number(
        float("nan"), label="Calculated Net/Gross", softbounds=(0, 100)
    )
    element_names = param.List(label="Choose elements:")

    # Elements
    bay_lagoon_lake = param.Integer(0, label="Bay/Lagoon/Lake", bounds=(0, 100))
    bay_lagoon_lake_quality = param.Selector(
        QUALITY_OPTIONS, label="Bay/Lagoon/Lake Quality"
    )
    beach = param.Integer(0, label="Beach", bounds=(0, 100))
    beach_quality = param.Selector(QUALITY_OPTIONS, label="Beach Quality")
    deltaplain_overbank = param.Integer(0, label="Deltaplain Overbank", bounds=(0, 100))
    deltaplain_overbank_quality = param.Selector(
        QUALITY_OPTIONS, label="Deltaplain Overbank Quality"
    )
    distributary_fluvial_channel_fill = param.Integer(
        0, label="Distributary Fluvial Channel-Fill", bounds=(0, 100)
    )
    distributary_fluvial_channel_fill_quality = param.Selector(
        QUALITY_OPTIONS, label="Distributary Fluvial Channel-Fill Quality"
    )
    floodplain_overbank = param.Integer(0, label="Floodplain Overbank", bounds=(0, 100))
    floodplain_overbank_quality = param.Selector(
        QUALITY_OPTIONS, label="Floodplain Overbank Quality"
    )
    lower_delta_front = param.Integer(0, label="Lower Delta Front", bounds=(0, 100))
    lower_delta_front_quality = param.Selector(
        QUALITY_OPTIONS, label="Lower Delta Front Quality"
    )
    lower_fan_delta_slope = param.Integer(
        0, label="Lower Fan Delta Slope", bounds=(0, 100)
    )
    lower_fan_delta_slope_quality = param.Selector(
        QUALITY_OPTIONS, label="Lower Fan Delta Slope Quality"
    )
    lower_shoreface = param.Integer(0, label="Lower Shoreface", bounds=(0, 100))
    lower_shoreface_quality = param.Selector(
        QUALITY_OPTIONS, label="Lower Shoreface Quality"
    )
    mass_transport_deposits = param.Integer(
        0, label="Mass Transport Deposits", bounds=(0, 100)
    )
    mass_transport_deposits_quality = param.Selector(
        QUALITY_OPTIONS, label="Mass Transport Deposits Quality"
    )
    offshore_fines = param.Integer(0, label="Offshore Fines", bounds=(0, 100))
    offshore_fines_quality = param.Selector(
        QUALITY_OPTIONS, label="Offshore Fines Quality"
    )
    offshore_transition = param.Integer(0, label="Offshore Transition", bounds=(0, 100))
    offshore_transition_quality = param.Selector(
        QUALITY_OPTIONS, label="Offshore Transition Quality"
    )
    prodelta = param.Integer(0, label="Prodelta", bounds=(0, 100))
    prodelta_quality = param.Selector(QUALITY_OPTIONS, label="Prodelta Quality")
    swamp_marsh = param.Integer(0, label="Swamp/Marsh", bounds=(0, 100))
    swamp_marsh_quality = param.Selector(QUALITY_OPTIONS, label="Swamp/Marsh Quality")
    tidal_channel_fill = param.Integer(0, label="Tidal Channel-Fill", bounds=(0, 100))
    tidal_channel_fill_quality = param.Selector(
        QUALITY_OPTIONS, label="Tidal Channel-Fill Quality"
    )
    tidal_dunes_bars = param.Integer(0, label="Tidal Dunes/Bars", bounds=(0, 100))
    tidal_dunes_bars_quality = param.Selector(
        QUALITY_OPTIONS, label="Tidal Dunes/Bars Quality"
    )
    tidal_flat = param.Integer(0, label="Tidal Flat", bounds=(0, 100))
    tidal_flat_quality = param.Selector(QUALITY_OPTIONS, label="Tidal Flat Quality")
    upper_delta_front = param.Integer(0, label="Upper Delta Front", bounds=(0, 100))
    upper_delta_front_quality = param.Selector(
        QUALITY_OPTIONS, label="Upper Delta Front Quality"
    )
    upper_fan_delta_slope = param.Integer(
        0, label="Upper Fan Delta Slope", bounds=(0, 100)
    )
    upper_fan_delta_slope_quality = param.Selector(
        QUALITY_OPTIONS, label="Upper Fan Delta Slope Quality"
    )
    upper_shoreface = param.Integer(0, label="Upper Shoreface", bounds=(0, 100))
    upper_shoreface_quality = param.Selector(
        QUALITY_OPTIONS, label="Upper Shoreface Quality"
    )

    def __init__(self, report_from_set_up, initial_values):
        """Set initial values based on previous stage"""
        super().__init__()
        self.report_from_set_up = report_from_set_up
        self._state = state.get_user_state().setdefault(APP, {})
        self.element_widgets = pn.Column(sizing_mode="stretch_both")
        self.visible_elements = {}

        self._initialize_qualities(
            reservoir_quality=_to_keys(initial_values["reservoir_quality"]),
            default=report_from_set_up["set_up"][
                "What is the anticipated N:G quality bracket?"
            ],
        )
        self._initialize_composition(
            composition=_to_keys(initial_values["composition"])
        )

    def _initialize_composition(self, composition):
        """Initialize composition weights"""
        for element, value in sorted(composition.items()):
            setattr(self, element, value)
            if value > 0:
                self.element_names.append(element)
        self.update_element_widgets()

    def _initialize_qualities(self, reservoir_quality, default):
        """Initialize quality parameters"""
        for element in ALL_ELEMENTS:
            value = reservoir_quality.get(element, default)
            setattr(self, f"{element}_quality", value)

    @property
    def all_elements(self):
        return [getattr(self, element) for element in ALL_ELEMENTS]

    @property
    def total(self):
        """The total sum of the different weights"""
        return sum(self.all_elements)

    @param.depends(*ALL_ELEMENTS, watch=True)
    def adds_to_100_percent(self):
        """Ensure that the different weights add up to 100%"""
        self.sum_to_100 = self.total == 100

    @param.depends(*ALL_ELEMENTS)
    def warn_not_100_percent(self):
        """Show a warning if the total sum of weights is not 100%"""
        if self.total == 100:
            return pn.pane.Alert(
                f"Sum of weights: **{self.total}%**", alert_type="success"
            )
        else:
            return pn.pane.Alert(
                f"Sum of weights: **{self.total}%** "
                "Make sure the weights add up to **100%**",
                alert_type="warning",
            )

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_composition(self):
        """Store user input to the final report"""
        return {
            **self.report_from_set_up,
            "building_block_type": {
                self.param.params(k).label: v
                for k, v in self.param.get_param_values()
                if k in ALL_ELEMENTS or k in ALL_QUALITIES
            },
        }

    @param.depends("element_names", watch=True)
    def update_element_widgets(self, *args, **kwargs):
        """Update widgets when the user adds or removes elements"""
        for element in set(self.visible_elements) - set(self.element_names):
            self.remove_element_widget(element)

        for element in sorted(set(self.element_names) - set(self.visible_elements)):
            self.add_element_widget(element)

    def add_element_widget(self, element):
        if element in self.visible_elements:
            return

        logger.debug(f"Adding {element} widget")
        colors = config.app.style.colors
        widget = pn.Row(
            pn.pane.Markdown(
                f"**{getattr(self.param, element).label}:**",
                width=150,
                sizing_mode="fixed",
            ),
            pn.widgets.IntSlider.from_param(
                getattr(self.param, element),
                name="",
                bar_color=colors.get(element, colors.default),
                sizing_mode="stretch_width",
                show_value=False,
            ),
            pn.widgets.Spinner.from_param(
                getattr(self.param, element), name="", width=100
            ),
            pn.widgets.RadioButtonGroup.from_param(
                getattr(self.param, f"{element}_quality"),
                button_type="default",
            ),
        )
        self.element_names.append(element)
        self.visible_elements[element] = widget.name
        self.element_widgets.append(widget)

    def remove_element_widget(self, element):
        """Remove a widget for an element"""
        if element not in self.visible_elements:
            return

        logger.debug(f"Removing {element} widget")
        widget_name = self.visible_elements[element]
        for widget in self.element_widgets[:]:
            if widget.name == widget_name:
                self.element_widgets.pop(widget)
                break

        setattr(self, element, 0)
        del self.visible_elements[element]

    @param.depends("element_names", *ALL_ELEMENTS, *ALL_QUALITIES, watch=True)
    def estimate_net_gross(self):
        if self.sum_to_100:
            self.net_gross = self.calculate_net_gross(
                {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k in ALL_ELEMENTS or k in ALL_QUALITIES
                }
            )
        else:
            self.net_gross = float("nan")

    def calculate_net_gross(self, composition):
        """Calculate a net gross estimate based on the given composition"""
        if "model" not in self._state:
            self._state["model"] = readers.read_model(
                reader=config.app.apps.reader, dataset=APP
            )
        model = self._state["model"]

        net_gross = model.assign(
            bb_pct=lambda df: df.apply(
                lambda row: composition.get(row.building_block_type, 0)
                if composition.get(f"{row.building_block_type} Quality")
                == row.descriptive_reservoir_quality
                else 0,
                axis="columns",
            ),
        )

        return net_gross.loc[:, ["net_gross", "bb_pct"]].prod(axis="columns").sum()


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        return pn.Column(
            panes.headline(self.param.composition_headline),
            pn.Row(
                pn.Column(
                    pn.widgets.MultiChoice.from_param(
                        self.param.element_names,
                        options=ELEMENT_OPTIONS,
                        delete_button=True,
                        solid=False,
                        height_policy="min",
                        margin=(0, 25),
                        height=120,
                        sizing_mode="fixed",
                    ),
                    self.element_widgets,
                    self.warn_not_100_percent,
                    sizing_mode="stretch_width",
                ),
                pn.Column(
                    pn.indicators.Number.from_param(
                        self.param.net_gross,
                        format="{value:.0f}%",
                        nan_format="...",
                        default_color="gold",
                        colors=[(100, "black")],
                    )
                ),
            ),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageElementComposition(Model, View):
    """Connect the model and the view"""


def _to_keys(data):
    """Convert dictionary keys from 'human names' to 'computer names'"""
    return {re.sub("[ /-]", "_", key).lower(): val for key, val in data.items()}
