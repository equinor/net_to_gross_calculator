"""Mock out reading from the API

Use local data stored in simplified_*.csv files
"""

# Standard library imports
import pathlib

# Third party imports
import pandas as pd

# Geo:N:G imports
from geong_common.data import composition
from geong_common.data import models

DATA_DIR = pathlib.Path(__file__).resolve().parent


def read_all(reader, dataset, table):
    """Mock for calling read_all() without contacting the API"""
    return pd.read_csv(DATA_DIR / f"simplified_{table}.csv")


def read_filtered(reader, dataset, table, **filters):
    """Mock for calling read_filtered() without contacting the API"""
    unfiltered = read_all(reader, dataset=dataset, table=table)
    return models.filter_data(unfiltered, filters)


def read_elements(reader, dataset, base_table, **filters):
    """Mock for calling read_elements() without contacting the API"""
    # Filter to get wells
    wells = read_filtered(reader, dataset=dataset, table=base_table, **filters)
    elements = read_all(reader, dataset=dataset, table="elements")
    return composition.combine_scale_and_elements(base_table, wells, elements)


def read_model(reader, dataset):
    """Mock for calling read_model() without contacting the API"""
    return pd.read_csv(DATA_DIR / "simplified_models.csv")
