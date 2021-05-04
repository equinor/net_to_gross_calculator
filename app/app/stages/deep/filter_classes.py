"""Third stage: Filter classes"""

# Standard library imports
import re

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app.assets import panes
from app.assets import state
from geong_common import config as geong_config
from geong_common.data import net_gross

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")

# Generate nested dictionary of parameters from model definition in geong.toml:
#
# {
#     "Lobe": {                                      <- building_block (label)
#         "Spatial Position": (                      <- filter_class (label)
#             "spatial_position",                    <- filter_class
#             {
#                 "Zone1": "lobe_spatial_zone1",     <- value (label: param)
#                 "Zone2": "lobe_spatial_zone2",
#                 "Zone3": "lobe_spatial_zone3",
#                 "Ignore Spatial Position": "lobe_spatial_ignore",
#             },
#         ),
#         "Confinement": ...,
#     }
# }
FILTER_CLASS_PARAMS = {
    building_block.label: {
        building_block[filter_class].label: (
            filter_class,
            {
                **{
                    value: (
                        f"{name[:4]}_{filter_class.split('_')[0]}_"
                        f"{re.sub('[ -]', '', value.lower())}"
                    )
                    for value in building_block[filter_class]["values"]
                },
                f"Ignore {building_block[filter_class].label}": (
                    f"{name[:4]}_{filter_class.split('_')[0]}_ignore"
                ),
            },
        )
        for filter_class in building_block.factors
    }
    for name, building_block in geong_config.geong.models[APP].section_items
    if building_block.factors
}

# List of leafs (parameters) in FILTER_CLASS_PARAMS
ALL_PARAMS = [
    param
    for fc in FILTER_CLASS_PARAMS.values()
    for _, val in fc.values()
    for param in val.values()
]


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    initial_filter_classes = param.Dict()
    report_from_composition = param.Dict()
    net_gross = param.Number(
        float("nan"), label="Calculated Net/Gross", softbounds=(0, 100)
    )

    def __init__(self, initial_filter_classes, report_from_composition, net_gross):
        """Set initial values based on previous stage"""

        # Add filter classes as parameters
        for bblock, filter_classes in FILTER_CLASS_PARAMS.items():
            for fclass, values in filter_classes.values():
                for label, param_name in values.items():
                    if label.startswith("Ignore "):
                        self.param._add_parameter(
                            param_name, param.Boolean(False, label=label)
                        )
                    else:
                        value = initial_filter_classes[bblock][fclass].get(label, 0)
                        self.param._add_parameter(
                            param_name,
                            param.Integer(value, label=label, bounds=(0, 100)),
                        )
        super().__init__()

        # Set up other parameters
        self._state = state.get_user_state().setdefault(APP, {})
        self.report_from_composition = report_from_composition
        self.net_gross = net_gross

    # Output recorded in the final report
    @param.output(param.Dict)
    def report_from_filter_classes(self):
        """Store user input to the final report"""
        param_values = dict(self.param.get_param_values())

        params = {}
        for bblock, filter_classes in FILTER_CLASS_PARAMS.items():
            for fclass, values in filter_classes.values():
                key = f"{bblock.lower()[:4]}_{fclass.split('_')[0]}"
                params.setdefault(key, {})
                ignore_param = f"{key}_ignore"
                for param_label, param_name in values.items():
                    if param_name == ignore_param:
                        continue
                    params[key][param_label] = (
                        100 / (len(values) - 1)
                        if param_values[ignore_param]
                        else param_values[param_name]
                    )

        return {**self.report_from_composition, **params}

    def filter_class_model_input(self):
        """Input to the model from filter classes"""
        param_values = dict(self.param.get_param_values())

        params = {}
        for bblock, filter_classes in FILTER_CLASS_PARAMS.items():
            params.setdefault(bblock, {})
            for fclass, values in filter_classes.values():
                params[bblock].setdefault(fclass, {})
                for param_label, param_name in values.items():
                    params[bblock][fclass][param_label] = param_values[param_name]

        return params

    @param.depends(*ALL_PARAMS, watch=True)
    def estimate_net_gross(self):
        self.net_gross = net_gross.calculate_deep_net_gross(
            model=self._state["model"],
            composition={
                **self.report_from_composition,
                **self.filter_class_model_input(),
            },
        )


class View:
    """Define the look and feel of the stage"""

    def division_slider(self, building_block_type, filter_class):
        """Simplify setting up division slider widgets"""
        param_info = FILTER_CLASS_PARAMS[building_block_type][filter_class][1]
        params = {
            f"param_{n}": p
            for n, (label, p) in enumerate(param_info.items(), start=1)
            if not label.startswith("Ignore ")
        }
        ignore_param = [
            p for label, p in param_info.items() if label.startswith("Ignore ")
        ][0]
        popup_label = f"deep_{ignore_param[:-7]}"  # Without _ignore suffix

        return panes.division_slider(
            building_block_type,
            filter_class,
            params=self.param,
            ignore_param=ignore_param,
            popup_label=popup_label,
            **params,
        )

    def panel(self):
        return pn.Row(
            pn.layout.HSpacer(),
            pn.Column(
                self.division_slider("Lobe", "Spatial Position"),
                self.division_slider("Lobe", "Confinement"),
                self.division_slider("Channel Fill", "Spatial Position"),
            ),
            pn.Column(
                self.division_slider("Lobe", "Bed Type"),
                self.division_slider("Lobe", "Archetypes"),
                self.division_slider("Channel Fill", "Archetypes"),
            ),
            pn.layout.HSpacer(),
            pn.Column(
                pn.indicators.Number.from_param(
                    self.param.net_gross,
                    format="{value:.0f}%",
                    nan_format="...",
                    default_color="red",
                    colors=[(100, "black")],
                ),
            ),
            pn.layout.HSpacer(),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageFilterClasses(Model, View):
    """Connect the model and the view"""
