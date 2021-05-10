"""Third stage: Results"""

# Standard library imports
import itertools

# Third party imports
import pandas as pd
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import charts
from app.assets import panes
from app.assets import state
from geong_common.log import logger

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")
CFG = config.app[PACKAGE][APP][STAGE]


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage
    report_from_composition = param.Dict()

    # Parameters for the current stage
    ready = param.Boolean(default=False)
    net_gross = param.Number(label="Net/Gross", softbounds=(0, 100))
    scenario_name = param.String(label="Scenario Name")
    porosity_modifier = param.Number(
        default=0, label="Porosity Modifier", bounds=(0, 100)
    )
    net_gross_modified = param.Number(label="Modified N/G", bounds=(0, 100))

    def __init__(self, report_from_composition, net_gross):
        """Set initial values based on previous stage"""
        super().__init__()
        self._state = state.get_user_state().setdefault(APP, {})
        self._state.setdefault("scenarios", {})
        self._current_scenario_name = None
        self.net_gross = net_gross
        self.report_from_composition = report_from_composition
        self.scenario_name = f"Scenario {len(self._state['scenarios']) + 1}"
        self.data = charts.data_as_dataframe(report_from_composition, CFG.columns)

        try:
            session_id = pn.state.curdoc.session_context.id
            logger.insights(f"New result: {self.net_gross}, SessionID: {session_id}")
            logger.insights(
                f"SessionID: {session_id}, Choices: {report_from_composition}"
            )
        except AttributeError as e:
            logger.error(f"SessionID not available: {e}")
            logger.insights(f"New result: {self.net_gross}")
            logger.insights(f"Choices: {report_from_composition}")

    @param.depends("net_gross", watch=True)
    def update_porosity_bounds(self):
        net_gross = dict(self.param.get_param_values())["net_gross"]
        if self.porosity_modifier > net_gross:
            self.porosity_modifier = self.net_gross
        self.param.porosity_modifier.bounds = (0, round(net_gross))

    @param.depends("net_gross", "porosity_modifier", watch=True)
    def update_ng_from_porosity(self):
        """Calculate modified net gross based on porosity"""
        if self.porosity_modifier > self.net_gross:
            self.porosity_modifier = self.net_gross

        self.net_gross_modified = self.net_gross - self.porosity_modifier

    def _store_scenario(self):
        """Store results for the current scenario"""
        scenarios = self._state["scenarios"]

        # Make sure name does not overwrite previous scenarios
        if (
            self.scenario_name != self._current_scenario_name
            and self.scenario_name in scenarios
        ):
            for suffix in itertools.count(start=2):
                name = f"{self.scenario_name} ({suffix})"
                if name not in scenarios:
                    break
            self.scenario_name = name

        # Get information about scenario
        if self._current_scenario_name in scenarios:
            scenario_info = scenarios.pop(self._current_scenario_name)
        else:
            scenario_info = {
                "net_gross": self.net_gross,
                **self.report_from_composition,
            }

        # Update scenario information
        scenario_info["net_gross_modified"] = self.net_gross_modified
        scenario_info["porosity_modifier"] = self.porosity_modifier

        # Store scenario information
        scenarios[self.scenario_name] = scenario_info
        self._current_scenario_name = self.scenario_name

    @pn.depends("scenario_name", "porosity_modifier")
    def scenario_table(self):
        """Table showing current scenarios"""
        self._store_scenario()

        scenarios = self._state["scenarios"]
        table_data = pd.DataFrame(
            {
                "Scenario Name": [s for s in scenarios.keys()],
                "Net/Gross": [round(s["net_gross"]) for s in scenarios.values()],
                "Modified N/G": [
                    round(s["net_gross_modified"]) for s in scenarios.values()
                ],
            }
        ).set_index("Scenario Name")
        return pn.pane.DataFrame(table_data, sizing_mode="stretch_width")

    def new_scenario_button(self):
        """Button for starting new scenario"""
        reset_button = self._state["update_view"]["workflow"]

        def restart_scenario(event):
            """Start a new scenario by restarting the workflow"""
            reset_button.clicks += 1

        button = pn.widgets.Button(
            name="New Scenario", button_type="success", width=125
        )
        button.on_click(restart_scenario)
        return button

    @param.output(param.List)
    def scenario_names(self):
        """Pass on names of scenarios to next stage"""
        return [sn for sn in self._state["scenarios"].keys()]


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        return pn.Column(
            pn.Row(
                pn.Column(
                    pn.Row(
                        pn.indicators.Number.from_param(
                            self.param.net_gross,
                            format="{value:.0f}%",
                            font_size="54pt",
                            title_size="18pt",
                        ),
                        pn.layout.HSpacer(),
                        pn.Column(
                            pn.Row(
                                pn.indicators.Number.from_param(
                                    self.param.net_gross_modified,
                                    format="{value:.0f}%",
                                    font_size="36pt",
                                    title_size="14pt",
                                ),
                                pn.pane.HTML(panes.popup("shallow_porosity_modifier")),
                            ),
                            pn.widgets.IntInput.from_param(
                                self.param.porosity_modifier, width=180
                            ),
                        ),
                        pn.layout.HSpacer(),
                    ),
                    pn.layout.Spacer(height=30),
                    charts.table_elements(self.data, CFG.columns),
                    charts.figure_weights(self.data, CFG.columns),
                    sizing_mode="stretch_width",
                ),
                pn.Column(
                    "##### Save scenario to report:",
                    pn.widgets.TextInput.from_param(self.param.scenario_name),
                    self.scenario_table,
                    pn.layout.Spacer(height=20),
                    pn.Row(
                        pn.layout.HSpacer(),
                        self.new_scenario_button,
                        panes.next_stage_button(APP, text="Finalize Report"),
                        pn.layout.HSpacer(),
                    ),
                ),
            ),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageResult(Model, View):
    """Connect the model and the view"""
