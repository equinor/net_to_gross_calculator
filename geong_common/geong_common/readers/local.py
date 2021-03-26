"""Read data from the API"""

# Third party imports
import pandas as pd
import pyplugs

# Geo:N:G imports
from geong_common import config
from geong_common.data import composition
from geong_common.data import models
from geong_common.log import logger

# Read plugin configuration
*_, PACKAGE, PLUGIN = __name__.split(".")
CFG = config.geong[PACKAGE][PLUGIN]


@pyplugs.register
def read_all(dataset, table):
    """Read all data from the API, convert to pandas dataframe"""
    return _read_from_json(
        CFG.path.replace("data", dataset=dataset, table=table, converter="path")
    )


@pyplugs.register
def read_filtered(dataset, table, **filters):
    """Read filtered data from the API, convert to pandas dataframe"""
    unfiltered = read_all(dataset=dataset, table=table)
    return models.filter_data(unfiltered, filters)


@pyplugs.register
def read_elements(dataset, base_table, **filters):
    """Get elements satisfying filters on base table"""
    # Filter to get wells
    wells = read_filtered(dataset=dataset, table=base_table, **filters)
    elements = read_all(dataset=dataset, table="elements")
    return composition.combine_scale_and_elements(base_table, wells, elements)


@pyplugs.register
def read_model(dataset):
    """Read the dataset models from the API, convert to pandas dataframe"""
    elements = read_all(dataset=dataset, table="elements")
    return models.calculate(elements=elements, dataset=dataset)


def _read_from_json(path):
    """Read from one JSON file"""
    logger.debug(f"Reading JSON from {path}")
    return pd.read_json(path.read_text(), orient="split")
