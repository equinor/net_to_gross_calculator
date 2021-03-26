"""First stage: Set up"""

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes
from geong_common import readers
from geong_common.data import composition

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")


class Model(param.Parameterized):
    """Data defining this stage"""

    composition_threshold = param.Selector(
        {
            "Simple composition": 12,
            "Detailed composition": 6,
        },
        label="Choose starting point for composition:",
    )
    depositional_setting = param.Selector(
        {
            "Delta": "Delta",
            "Shoreface": "Shoreface",
            "Estuary": "Estuary",
            "Fan Delta": "Fan Delta",
        },
        label="What is the overall depositional setting?",
    )
    stratigraphic_scale = param.Selector(
        {
            "Complex (~10's m thickness)": "complexes",
            "System (10's-100's m thickness)": "systems",
        },
        label="What is the stratigraphic scale?",
    )
    reservoir_quality = param.Selector(
        {
            "Poor (0 - 30%)": "Poor <30% NG",
            "Moderate (30 - 65%)": "Moderate 30-65% NG",
            "Good (65 - 85%)": "Good 65-85% NG",
            "Exceptional (85 - 100%)": "Exceptional 85-100% NG",
        },
        label="What is the anticipated N:G quality bracket?",
    )

    # Output passed on to the next stages
    @param.output(param.Dict)
    def initial_values(self):
        """Calculate initial values for the next stages by contacting the API"""
        elements = readers.read_elements(
            reader=config.app.apps.reader,
            dataset=APP,
            base_table=self.stratigraphic_scale,
            building_block_type=self.depositional_setting,
            descriptive_reservoir_quality=self.reservoir_quality,
        )

        return {
            "composition": composition.calculate_composition_in_group(
                elements=elements,
                column="building_block_type",
                threshold=self.composition_threshold,
            )
        }

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_set_up(self):
        """Store user input to the final report"""
        return {
            "set_up": {
                self.param.params(k).label: v
                for k, v in self.param.get_param_values()
                if k != "name"
            }
        }


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        """Display the first stage using radio boxes"""

        return pn.Column(
            panes.headline(self.param.composition_threshold),
            pn.widgets.RadioBoxGroup.from_param(self.param.composition_threshold),
            panes.headline(self.param.depositional_setting),
            pn.widgets.RadioBoxGroup.from_param(self.param.depositional_setting),
            panes.headline(self.param.stratigraphic_scale),
            pn.widgets.RadioBoxGroup.from_param(self.param.stratigraphic_scale),
            panes.headline(self.param.reservoir_quality),
            pn.widgets.RadioBoxGroup.from_param(self.param.reservoir_quality),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageSetUp(Model, View):
    """Connect the model and the view"""
