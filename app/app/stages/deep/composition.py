"""Second stage: Composition"""

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")
CFG = config.app[PACKAGE][APP][STAGE]


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    initial_values = param.Dict()
    report_from_set_up = param.Dict()

    # Parameters for the current stage
    headline = param.String(label="Element Composition", doc="Todo")
    ready = param.Boolean(default=True)

    lobe = param.Integer(0, label="Lobe", bounds=(0, 100))
    channel_fill = param.Integer(0, label="Channel Fill", bounds=(0, 100))
    overbank = param.Integer(0, label="Overbank", bounds=(0, 100))
    mtd = param.Integer(0, label="MTD", bounds=(0, 100))
    drape = param.Integer(0, label="Drape", bounds=(0, 100))

    def __init__(self, report_from_set_up, initial_values):
        """Set initial values based on previous stage"""
        super().__init__()
        self.report_from_set_up = report_from_set_up
        self._initial_filter_classes = initial_values["filter_classes"]
        for building_block_type, value in initial_values["composition"].items():
            setattr(self, building_block_type.replace(" ", "_").lower(), value)

    @property
    def total(self):
        """The total sum of the different weights"""
        return self.lobe + self.channel_fill + self.overbank + self.mtd + self.drape

    @param.depends("lobe", "channel_fill", "overbank", "mtd", "drape", watch=True)
    def adds_to_100_percent(self):
        """Ensure that the different weights add up to 100%"""
        self.ready = self.total == 100

    @param.depends("lobe", "channel_fill", "overbank", "mtd", "drape")
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
            "building_block_type": {
                self.param.params(k).label: v
                for k, v in self.param.get_param_values()
                if k in {"lobe", "channel_fill", "overbank", "mtd", "drape"}
            },
        }


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        colors = config.app.style.colors
        return pn.Column(
            panes.headline(self.param.headline),
            pn.widgets.IntSlider.from_param(self.param.lobe, bar_color=colors.lobe),
            pn.widgets.IntSlider.from_param(
                self.param.channel_fill, bar_color=colors.channel_fill
            ),
            pn.widgets.IntSlider.from_param(
                self.param.overbank, bar_color=colors.overbank
            ),
            pn.widgets.IntSlider.from_param(self.param.mtd, bar_color=colors.mtd),
            pn.widgets.IntSlider.from_param(self.param.drape, bar_color=colors.drape),
            self.warnings,
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageElementComposition(Model, View):
    """Connect the model and the view"""
