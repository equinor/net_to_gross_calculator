"""Functions for calculating compositions from data"""

# Third party imports
from iteround import saferound

# Geo:N:G imports
from geong_common.log import logger


def calculate_composition_in_group(elements, column, threshold=0):
    """Calculate composition of elements in a given column"""
    logger.info(f"Calculate {column} composition based on {len(elements)} elements")
    return (
        elements.groupby(column)
        .size()
        .to_frame("col_count")
        .assign(ratio=lambda df: 100 * df.col_count / (df.col_count.sum() or 1))
        .query("ratio > @threshold")
        .assign(ratio=lambda df: 100 * df.col_count / (df.col_count.sum() or 1))
        .apply(
            lambda col: saferound(0 if col.empty else col.astype(float), 0),
            axis="index",
        )
        .loc[:, "ratio"]
        .astype(int)
        .to_dict()
    )


def calculate_filter_classes(elements, filter_classes):
    """Calculate initial filter classes based on historical elements"""

    # Calculate filter classes as ratio of each building block type
    composition = {}
    for building_block_type, filter_class in filter_classes:
        composition[building_block_type, filter_class] = calculate_composition_in_group(
            elements.query("building_block_type == @building_block_type"),
            column=filter_class,
        )

    return composition
