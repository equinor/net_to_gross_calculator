"""Third stage: Filter classes"""

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes
from geong_common.log import logger


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    initial_filter_classes = param.Dict()
    report_from_composition = param.Dict()

    # Spatial position (Lobe)
    lobe_spatial = param.String(label="Spatial Position", doc="Todo")
    lobe_spatial_zone1 = param.Integer(0, label="Zone1", bounds=(0, 100))
    lobe_spatial_zone2 = param.Integer(0, label="Zone2", bounds=(0, 100))
    lobe_spatial_zone3 = param.Integer(0, label="Zone3", bounds=(0, 100))
    lobe_spatial_ignore = param.Boolean(label="Ignore Spatial Position")

    # Confinement (Lobe)
    lobe_confinement = param.String(label="Confinement")
    lobe_confinement_confined = param.Integer(0, label="Confined", bounds=(0, 100))
    lobe_confinement_unconfined = param.Integer(0, label="Unconfined", bounds=(0, 100))
    lobe_confinement_weaklyconfined = param.Integer(
        0, label="Weakly Confined", bounds=(0, 100)
    )
    lobe_confinement_ignore = param.Boolean(label="Ignore Confinement")

    # Bed type (Lobe)
    lobe_conventional = param.String(label="Bed Type")
    lobe_conventional_conventionalturbidites = param.Integer(
        0, label="Conventional Turbidites", bounds=(0, 100)
    )
    lobe_conventional_hybrideventbeds = param.Integer(
        0, label="Hybrid Event Beds", bounds=(0, 100)
    )
    lobe_conventional_ignore = param.Boolean(label="Ignore Bed Type")

    # Archetypes (Lobe)
    lobe_architectural = param.String(label="Archetypes")
    lobe_architectural_lobechannelised = param.Integer(
        0, label="Lobe Channelised", bounds=(0, 100)
    )
    lobe_architectural_lobenonchannelised = param.Integer(
        0, label="Lobe Non-Channelised", bounds=(0, 100)
    )
    lobe_architectural_ignore = param.Boolean(label="Ignore Archetypes")

    # Spatial position (Channel Fill)
    chan_relative = param.String(label="Spatial Position", doc="Todo")
    chan_relative_axial = param.Integer(0, label="Axial", bounds=(0, 100))
    chan_relative_offaxis = param.Integer(0, label="Off Axis", bounds=(0, 100))
    chan_relative_margin = param.Integer(0, label="Margin", bounds=(0, 100))
    chan_relative_ignore = param.Boolean(label="Ignore Spatial Position")

    # Archetypes (Channel Fill)
    chan_architectural = param.String(label="Archetypes")
    chan_architectural_laterallymigrating = param.Integer(
        0, label="Laterally Migrating", bounds=(0, 100)
    )
    chan_architectural_erosionallyconfined = param.Integer(
        0, label="Erosionally Confined", bounds=(0, 100)
    )
    chan_architectural_overbankconfined = param.Integer(
        0, label="Overbank Confined", bounds=(0, 100)
    )
    chan_architectural_ignore = param.Boolean(label="Ignore Archetypes")

    def __init__(self, initial_filter_classes, report_from_composition):
        """Set initial values based on previous stage"""
        super().__init__()
        self.report_from_composition = report_from_composition
        for (building_block, filter_class), classes in initial_filter_classes.items():
            prop_prefix = f"{building_block[:4].lower()}_{filter_class.split('_')[0]}"
            for label, value in classes.items():
                prop = (
                    f"{prop_prefix}_{label.replace(' ', '').replace('-', '').lower()}"
                )
                if hasattr(self, prop):
                    setattr(self, prop, value)
                else:
                    logger.warning(f"Unknown property: {prop!r}")

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_filter_classes(self):
        """Store user input to the final report"""
        return {
            **self.report_from_composition,
            "Lobe": {
                "architectural_style": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("lobe_architectural")
                },
                "confinement": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("lobe_confinement")
                },
                "conventional_facies_vs_hebs": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("lobe_conventional")
                },
                "spatial_position": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("lobe_spatial")
                },
            },
            "Channel Fill": {
                "architectural_style": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("chan_architectural")
                },
                "relative_strike_position": {
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k.startswith("chan_relative")
                },
            },
        }


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        colors = config.app.style.colors
        return pn.Column(
            pn.Card(
                pn.Row(
                    pn.Column(
                        panes.headline(self.param.lobe_spatial),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_spatial_zone1, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_spatial_zone2, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_spatial_zone3, step=1
                        ),
                        pn.widgets.Checkbox.from_param(self.param.lobe_spatial_ignore),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                    pn.Column(
                        panes.headline(self.param.lobe_confinement),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_confinement_confined, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_confinement_unconfined, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_confinement_weaklyconfined, step=1
                        ),
                        pn.widgets.Checkbox.from_param(
                            self.param.lobe_confinement_ignore
                        ),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                    pn.Column(
                        panes.headline(self.param.lobe_conventional),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_conventional_conventionalturbidites, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_conventional_hybrideventbeds, step=1
                        ),
                        pn.widgets.Checkbox.from_param(
                            self.param.lobe_conventional_ignore
                        ),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                    pn.Column(
                        panes.headline(self.param.lobe_architectural),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_architectural_lobechannelised, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.lobe_architectural_lobenonchannelised, step=1
                        ),
                        pn.widgets.Checkbox.from_param(
                            self.param.lobe_architectural_ignore
                        ),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                ),
                title="Lobe Filter Classes",
                header_background=colors.lobe,
                active_header_background=colors.lobe,
                background="white",
            ),
            pn.Card(
                pn.Row(
                    pn.Column(
                        panes.headline(self.param.chan_relative),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_relative_axial, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_relative_offaxis, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_relative_margin, step=1
                        ),
                        pn.widgets.Checkbox.from_param(self.param.chan_relative_ignore),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                    pn.Column(
                        panes.headline(self.param.chan_architectural),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_architectural_laterallymigrating, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_architectural_erosionallyconfined, step=1
                        ),
                        pn.widgets.IntInput.from_param(
                            self.param.chan_architectural_overbankconfined, step=1
                        ),
                        pn.widgets.Checkbox.from_param(
                            self.param.chan_architectural_ignore
                        ),
                        max_width=300,
                        sizing_mode="stretch_width",
                    ),
                ),
                title="Channel Fill Filter Classes",
                header_background=colors.channel_fill,
                active_header_background=colors.channel_fill,
                background="white",
            ),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageFilterClasses(Model, View):
    """Connect the model and the view"""
