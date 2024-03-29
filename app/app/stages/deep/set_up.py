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

    # Parameters representing questions for the user
    gross_geomorphology = param.Selector(
        {"Fan Shaped": "fan", "Channel Shaped": "channel"},
        label="What is the gross geomorphology?",
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

    def building_blocks_by_table(self):
        """Find name of building blocks based on the table"""
        return {
            "complexes": {"fan": "Lobe Complex", "channel": "Channel Complex"},
            "systems": {"fan": "Fan System", "channel": "Channel System"},
        }[self.stratigraphic_scale][self.gross_geomorphology]

    # Output passed on to the next stages
    @param.output(param.Dict)
    def initial_values(self):
        """Calculate initial values for the next stages by contacting the API"""
        elements = readers.read_elements(
            reader=config.app.apps.reader,
            dataset=APP,
            base_table=self.stratigraphic_scale,
            building_block_type=self.building_blocks_by_table(),
            descriptive_reservoir_quality=self.reservoir_quality,
        )

        return {
            "composition": composition.calculate_composition_in_group(
                elements=elements, column="building_block_type"
            ),
            "filter_classes": composition.calculate_filter_classes(
                elements=elements,
                filter_classes=(
                    ("Channel Fill", "architectural_style"),
                    ("Channel Fill", "relative_strike_position"),
                    ("Lobe", "architectural_style"),
                    ("Lobe", "confinement"),
                    ("Lobe", "conventional_facies_vs_hebs"),
                    ("Lobe", "spatial_position"),
                ),
            ),
        }

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_set_up(self):
        """Store user input to the final report"""
        # Map values to user strings
        value_to_user = {
            p: {v: k for k, v in self.param.params(p).names.items()}
            for p in self.param.params()
            if p != "name"
        }
        return {
            "set_up": {
                self.param.params(k).label: value_to_user[k][v]
                for k, v in self.param.get_param_values()
                if k != "name"
            }
        }


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        """Display the first stage using radio boxes"""

        return pn.Column(
            panes.multiple_choice(self.param.gross_geomorphology),
            panes.multiple_choice(self.param.stratigraphic_scale),
            panes.multiple_choice(self.param.reservoir_quality),
            pn.layout.Spacer(height=20),
            panes.next_stage_button(APP),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageSetUp(Model, View):
    """Connect the model and the view"""
