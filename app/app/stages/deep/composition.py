"""Second stage: Composition"""

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
from geong_common.data import net_gross

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")
CFG = config.app[PACKAGE][APP][STAGE]

# Get list of elements from model configuration
ELEMENT_OPTIONS = {
    section.label: name
    for name, section in geong_config.geong.models[APP].section_items
}
ALL_ELEMENTS = list(ELEMENT_OPTIONS.values())


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    initial_values = param.Dict()
    report_from_set_up = param.Dict()

    # Parameters for the current stage
    net_gross = param.Number(
        float("nan"), label="Calculated Net/Gross", softbounds=(0, 100)
    )

    def __init__(self, report_from_set_up, initial_values):
        """Set initial values based on previous stage"""

        # Add elements as parameters
        for label, element in ELEMENT_OPTIONS.items():
            self.param._add_parameter(
                element, param.Integer(0, label=label, bounds=(0, 100))
            )
        super().__init__()

        self.report_from_set_up = report_from_set_up
        self._state = state.get_user_state().setdefault(APP, {})
        self._initial_filter_classes = initial_values["filter_classes"]
        for building_block_type, value in initial_values["composition"].items():
            setattr(self, building_block_type.replace(" ", "_").lower(), value)

    @property
    def total(self):
        """The total sum of the different weights"""
        return sum(getattr(self, element) for element in ALL_ELEMENTS)

    @param.depends(*ALL_ELEMENTS, watch=True)
    def adds_to_100_percent(self):
        """Only enable next stage if the weights add up to 100%"""
        self.next_stage_button.disabled = self.total != 100

    @param.depends(*ALL_ELEMENTS)
    def warnings(self):
        """Show a warning if the total sum of weights is not 100%"""
        if self.total != 100:
            return panes.warning(CFG.warnings.replace("not_100_text", total=self.total))
        else:
            return pn.pane.Alert("", alert_type="light")

    # Output passed on to the next stage
    @param.output(param.Dict)
    def initial_filter_classes(self):
        """Pass on initial values for next stage calculated earlier by API"""
        return self._initial_filter_classes

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_composition(self):
        """Store user input to the final report"""
        return {
            **self.report_from_set_up,
            "weights": {
                self.param.params(e).label: getattr(self, e) for e in ALL_ELEMENTS
            },
        }

    @param.depends(*ALL_ELEMENTS, watch=True)
    def estimate_net_gross(self):
        if self.total == 100:
            if "model" not in self._state:
                self._state["model"] = readers.read_model(
                    reader=config.app.apps.reader, dataset=APP
                )
            self.net_gross = net_gross.calculate_deep_net_gross(
                model=self._state["model"],
                composition={
                    **self._initial_filter_classes,
                    "building_block_type": {
                        self.param.params(k).label: v
                        for k, v in self.param.get_param_values()
                        if k in ALL_ELEMENTS
                    },
                },
            )
        else:
            self.net_gross = float("nan")


class View:
    """Define the look and feel of the stage"""

    next_stage_button = panes.next_stage_button(APP)

    def panel(self):
        sliders = [
            panes.element_slider(getattr(self.param, element))
            for element in ALL_ELEMENTS
        ]

        return pn.Column(
            panes.headline(CFG.label, popup_label="deep_composition"),
            pn.Row(
                pn.Column(*sliders, sizing_mode="stretch_width"),
                pn.Column(
                    pn.indicators.Number.from_param(
                        self.param.net_gross,
                        format="{value:.0f}%",
                        nan_format="...",
                        default_color="red",
                        colors=[(100, "black")],
                    ),
                    pn.layout.Spacer(height=20),
                    pn.Row(panes.previous_stage_button(APP), self.next_stage_button),
                ),
            ),
            self.warnings,
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageElementComposition(Model, View):
    """Connect the model and the view"""
