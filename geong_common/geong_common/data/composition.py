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


def calculate_quality_in_group(all_elements, elements, column):
    """Calculate quality of elements grouped on a given column

    For each group, pick the quality bracket with the most elements relative to
    the overall distribution of all elements.
    """
    quality_col = "descriptive_reservoir_quality"
    logger.info(f"Calculate {column} quality based on {len(elements)} elements")

    distribution = all_elements.groupby([quality_col, column]).size().unstack()
    group_distribution = elements.groupby([quality_col, column]).size().unstack()

    return (group_distribution / distribution).idxmax().dropna().to_dict()


def calculate_filter_classes(elements, filter_classes):
    """Calculate initial filter classes based on historical elements"""

    # Calculate filter classes as ratio of each building block type
    composition = {}
    for building_block_type, filter_class in filter_classes:
        bb_composition = composition.setdefault(building_block_type, {})
        bb_composition[filter_class] = calculate_composition_in_group(
            elements.query("building_block_type == @building_block_type"),
            column=filter_class,
        )

    return composition


def combine_scale_and_elements(scale_table, wells, elements):
    """Combine systems or complexes table with elements"""
    parents = {
        "complexes": "parent_complex_identifier",
        "systems": "parent_system_identifier",
    }
    return wells.merge(
        elements,
        how="left",
        left_on="unique_id",
        right_on=parents[scale_table],
        suffixes=("_table", ""),
    )
