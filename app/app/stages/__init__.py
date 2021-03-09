"""Definitions of stages in a pipeline"""

# Third party imports
import pyplugs
from codetiming import Timer

# Geo:N:G imports
from app import config
from geong_common.log import logger

# Configuration of stages
*_, PACKAGE = __name__.split(".")
CFG = config.app[PACKAGE]


def get_stage(app, stage):
    """Get a stage from a given app"""
    with Timer(
        text=f"Loaded stage {app}:{stage} in {{:.2f}} seconds", logger=logger.time
    ):
        return pyplugs.get(package=f"{__package__}.{app}", plugin=stage)


def get_params(app, stage):
    """Get parameters for one pipeline stage"""
    return CFG[app][stage].get("params", {})
