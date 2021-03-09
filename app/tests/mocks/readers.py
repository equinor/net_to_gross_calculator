"""Mock out reading from the API

Use local data stored in simplified_*.csv files
"""

# Standard library imports
import pathlib

# Third party imports
import pandas as pd

DATA_DIR = pathlib.Path(__file__).resolve().parent


def read_all(reader, dataset, table):
    """Mock for calling read_all() without contacting the API"""
    return pd.read_csv(DATA_DIR / f"simplified_{table}.csv")


def read_filtered(reader, dataset, table, **filters):
    """Mock for calling read_filtered() without contacting the API"""
    unfiltered = read_all(reader, dataset=dataset, table=table)

    # Combine filters to a query
    query = " and ".join(f"{col} == {value!r}" for col, value in filters.items())
    if query:
        return unfiltered.query(query)
    else:
        return unfiltered


def read_elements(reader, dataset, base_table, **filters):
    """Mock for calling read_elements() without contacting the API"""
    # Filter to get wells
    wells = read_filtered(reader, dataset=dataset, table=base_table, **filters)

    # Merge with elements
    parents = {
        "complexes": "parent_complex_identifier",
        "systems": "parent_system_identifier",
    }
    return wells.merge(
        read_all(reader, dataset=dataset, table="elements"),
        how="left",
        left_on="unique_id",
        right_on=parents[base_table],
        suffixes=("_table", ""),
    )


def read_model(reader, dataset):
    """Mock for calling read_model() without contacting the API"""
    return pd.read_csv(DATA_DIR / "simplified_models.csv")
