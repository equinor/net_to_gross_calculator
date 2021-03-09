"""Workflow for Deep Water Reservoirs Geo:N:G app"""

# Third party imports
import panel as pn
import pyplugs

# Geo:N:G imports
from app import config
from app import stages
from geong_common.log import logger

# Read configuration
*_, PACKAGE, APP, VIEW = __name__.split(".")
CFG = config.app[PACKAGE][APP][VIEW]


@pyplugs.register
def view():
    """Add stages defined in config to a workflow pipeline"""
    stages_cfg = config.app.stages[APP]
    pipeline = pn.pipeline.Pipeline(debug=logger.is_dev)
    for stage in CFG.stages:
        pipeline.add_stage(
            stages_cfg[stage].label,
            stages.get_stage(APP, stage),
            **stages.get_params(APP, stage)
        )

    # Use pipeline.layout to render the default layout or use pipeline.title,
    # .buttons, .network, .stage etc to create a custom layout
    return [
        pipeline.network,
        pipeline.error,
        pipeline.stage,
        pipeline.buttons,
    ]
