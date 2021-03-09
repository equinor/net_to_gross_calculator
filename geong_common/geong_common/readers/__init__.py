"""Readers that can read data

Each reader should register four functions with the following signatures:

- read_all(dataset, table)
- read_filtered(dataset, table, **filters)
- read_elements(dataset, base_table, **filters)
- read_model(dataset)

All functions should return pandas dataframes. If there are no results, they
should return an empty dataframe with the expected columns.
"""

# Third party imports
import pyplugs

# Call read functions in the underlying readers
_read = pyplugs.call_factory(__package__)


def read_all(reader, dataset, table):
    """Proxy for calling read_all() with the underlying reader"""
    return _read(reader, func="read_all", dataset=dataset, table=table)


def read_filtered(reader, dataset, table, **filters):
    """Proxy for calling read_filtered() with the underlying reader"""
    return _read(reader, func="read_filtered", dataset=dataset, table=table, **filters)


def read_elements(reader, dataset, base_table, **filters):
    """Proxy for calling read_elements() with the underlying reader"""
    return _read(
        reader, func="read_elements", dataset=dataset, base_table=base_table, **filters
    )


def read_model(reader, dataset):
    """Proxy for calling read_model() with the underlying reader"""
    return _read(reader, func="read_model", dataset=dataset)
