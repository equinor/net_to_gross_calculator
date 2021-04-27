"""Fifth stage: Report"""

# Standard library imports
import io
from datetime import datetime

# Third party imports
import panel as pn
import param
import pyplugs

# Geo:N:G imports
from app import config
from app.assets import panes
from app.assets import state
from geong_common import reports
from geong_common.log import logger

# Find name of app and stage
*_, PACKAGE, APP, STAGE = __name__.split(".")
CFG = config.app[PACKAGE][APP][STAGE]


class Model(param.Parameterized):
    """Data defining this stage"""

    # Values set by previous stage

    # Parameters for the current stage
    geox_id = param.String(label="GeoX ID")
    scenario_names = param.List()

    def __init__(self, scenario_names, *args, **kwargs):
        """Initialize values of stage"""
        super().__init__()
        self._report_cfg = config.app.report[CFG.report]
        self._state = state.get_user_state().setdefault(APP, {})
        self.scenario_names = scenario_names
        self.scenario_selector = pn.widgets.CrossSelector(
            name="Choose scenarios",
            value=self.scenario_names,
            options=self.scenario_names,
            definition_order=False,
        )
        self.scenarios = self._state["scenarios"].copy()

    @property
    def data(self):
        """Data made available for the final report"""
        return {
            "date": datetime.now(),
            "geox_id": self.geox_id,
            "scenario_list": "\n".join(self.scenario_selector.value),
            "scenarios": [
                dict(self.scenarios[s], scenario_name=s)
                for s in self.scenario_selector.value
            ],
        }

    @param.depends("geox_id")
    def download_report_button(self):
        """Button for downloading report"""
        return pn.widgets.FileDownload(
            name="Download report",
            button_type="success",
            callback=self.download_report,
            filename=self._report_cfg.replace("file_name", **self.data),
        )

    def download_report(self, *event):
        """Generate and download final report"""
        report_stream = io.BytesIO()
        reports.generate(
            self._report_cfg.generator,
            template_url=self._report_cfg.template,
            cfg=self._report_cfg,
            data=self.data,
            output_path=report_stream,
        )

        try:
            session_id = pn.state.curdoc.session_context.id
            logger.insights(
                f"New report with GeoXID: {self.geox_id}, SessionID: {session_id}"
            )
        except AttributeError as e:
            logger.insights(f"New report with GeoXID: {self.geox_id}")
            logger.error(f"SessionID not available: {e}")

        # Clear scenarios from state
        self._state["scenarios"].clear()

        # Reset report byte stream to start before passing it back
        report_stream.seek(0)
        return report_stream


class View:
    """Define the look and feel of the stage"""

    def panel(self):
        return pn.Column(
            panes.headline(CFG.label),
            self.scenario_selector,
            pn.Row(
                pn.widgets.TextInput.from_param(self.param.geox_id),
                self.download_report_button,
            ),
            sizing_mode="stretch_width",
        )


@pyplugs.register
class StageReport(Model, View):
    """Connect the model and the view"""
