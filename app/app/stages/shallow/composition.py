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
from geong_common.log import logger

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")
CFG = config.app[PACKAGE][APP][STAGE]

# Get list of elements from model configuration
ELEMENT_OPTIONS = {
    **{
        section.label: name
        for name, section in geong_config.geong.models[APP].section_items
    },
    **{"Non-Reservoir Drape": "non_reservoir_drape"},
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
    sum_to_100 = param.Boolean(default=True)
    net_gross = param.Number(
        float("nan"), label="Calculated Net/Gross", softbounds=(0, 100)
    )
    element_names = param.List(label="Choose elements:")

    def __init__(self, report_from_set_up, initial_values):
        """Set initial values based on previous stage"""

        # Add elements as parameters
        for label, element in ELEMENT_OPTIONS.items():
            self.param._add_parameter(
                element, param.Integer(0, label=label, bounds=(0, 100))
            )
            self.param._add_parameter(
                f"{element}_quality",
                param.Selector(QUALITY_OPTIONS, label=f"{label} Quality"),
            )
        super().__init__()

        # Initialize parameter values
        self.report_from_set_up = report_from_set_up
        self._state = state.get_user_state().setdefault(APP, {})
        colors = config.app.style.colors
        quality_colors = pn.Row(
            pn.layout.HSpacer(),
            pn.pane.HTML(background=colors.poor, width=40, height=20),
            pn.layout.HSpacer(),
            pn.layout.Spacer(width=4),  # Tweak to improve alignment
            pn.pane.HTML(background=colors.moderate, width=40, height=20),
            pn.layout.Spacer(width=4),  # Tweak to improve alignment
            pn.layout.HSpacer(),
            pn.pane.HTML(background=colors.good, width=40, height=20),
            pn.layout.HSpacer(),
            pn.layout.Spacer(width=5),  # Tweak to improve alignment
            pn.pane.HTML(background=colors.exceptional, width=40, height=20),
            pn.layout.Spacer(width=5),  # Tweak to improve alignment
            pn.layout.HSpacer(),
        )
        self.element_widgets = pn.GridBox(
            "**Element**",
            "",
            pn.Row(pn.layout.Spacer(width=10), "**Volume %**"),
            quality_colors,
            ncols=4,
        )
        self.visible_elements = {}

        self._initialize_qualities(
            reservoir_quality={
                ELEMENT_OPTIONS[k]: initial_values["reservoir_quality"]
                for k in initial_values["composition"]
            },
            default=initial_values["reservoir_quality"],
        )
        self._initialize_composition(
            composition={
                ELEMENT_OPTIONS[k]: v for k, v in initial_values["composition"].items()
            }
        )

    def _initialize_composition(self, composition):
        """Initialize composition weights"""
        for element in ALL_ELEMENTS:
            value = composition.get(element, 0)
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

    @param.depends("element_names", *ALL_ELEMENTS, *ALL_QUALITIES)
    def warnings(self):
        """Show a warning if the total sum of weights is not 100%"""
        if not self.element_names:
            return panes.warning(CFG.warnings.replace("no_elements_text"))
        elif self.total != 100:
            return panes.warning(CFG.warnings.replace("not_100_text", total=self.total))
        elif self.net_gross >= CFG.warnings.ng_above:
            return panes.warning(CFG.warnings.replace("ng_above_text"))
        else:
            return pn.pane.Alert("", alert_type="light")

    @param.output(param.Dict)
    def report_from_composition(self):
        """Store user input to the final report"""
        elements_used = self.element_names
        qualities_used = [f"{e}_quality" for e in elements_used]
        return {
            **self.report_from_set_up,
            "weights": {
                self.param.params(k).label: v
                for k, v in self.param.get_param_values()
                if k in elements_used
            },
            "qualities": {
                self.param.params(k).label[:-8]: v
                for k, v in self.param.get_param_values()
                if k in qualities_used
            },
        }

    @param.depends("element_names", watch=True)
    def update_element_widgets(self, *args, **kwargs):
        """Update widgets when the user adds or removes elements"""
        for element in set(self.visible_elements) - set(self.element_names):
            self.remove_element_widget(element)

        for element in [
            e
            for e in ALL_ELEMENTS
            if e in self.element_names and e not in self.visible_elements
        ]:
            self.add_element_widget(element)

    def add_element_widget(self, element):
        if element in self.visible_elements:
            return

        logger.debug(f"Adding {element} widget")
        widgets = panes.element_slider(
            param=getattr(self.param, element),
            quality_param=getattr(self.param, f"{element}_quality"),
        )

        # Sort elements in the same order as ALL_ELEMENTS
        ordered = sorted(self.element_names, key=lambda e: ALL_ELEMENTS.index(e))
        start_idx = 4 * (ordered.index(element) + 1)  # +1 because of headline

        # Add widgets to screen
        self.visible_elements[element] = list(widgets)
        for idx, widget in enumerate(widgets, start=start_idx):
            self.element_widgets.insert(idx, widget)

    def remove_element_widget(self, element):
        """Remove widgets for an element"""
        if element not in self.visible_elements:
            return

        logger.debug(f"Removing {element} widget")
        widget_to_remove = self.visible_elements[element]
        for widget in self.element_widgets[:]:
            if widget in widget_to_remove:
                self.element_widgets.pop(widget)

        setattr(self, element, 0)
        del self.visible_elements[element]

    @param.depends("element_names", *ALL_ELEMENTS, *ALL_QUALITIES, watch=True)
    def estimate_net_gross(self):
        if self.sum_to_100:
            if "model" not in self._state:
                self._state["model"] = readers.read_model(
                    reader=config.app.apps.reader, dataset=APP
                )
            self.net_gross = net_gross.calculate_shallow_net_gross(
                model=self._state["model"],
                composition={
                    self.param.params(k).label: v
                    for k, v in self.param.get_param_values()
                    if k in ALL_ELEMENTS or k in ALL_QUALITIES
                },
            )
        else:
            self.net_gross = float("nan")


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        return pn.Column(
            panes.headline(CFG.label, popup_label="shallow_composition"),
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
                        placeholder="Choose elements to build a model",
                        sizing_mode="fixed",
                    ),
                    self.element_widgets,
                    sizing_mode="stretch_width",
                ),
                pn.Column(
                    pn.indicators.Number.from_param(
                        self.param.net_gross,
                        format="{value:.0f}%",
                        nan_format="...",
                        default_color="red",
                        colors=[(CFG.warnings.ng_above, "black")],
                    ),
                    panes.warning(
                        CFG.warnings.customize_quality_text, alert_type="light"
                    ),
                ),
            ),
            self.warnings,
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageElementComposition(Model, View):
    """Connect the model and the view"""
