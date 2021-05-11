"""Create synthetic data for the Net to Gross Calculator"""

# Standard library imports
import pathlib

# Third party imports
import numpy as np
import pandas as pd

# Geo:N:G imports
from geong_common import readers
from geong_common.log import logger

DATASETS = {
    "deep": {
        "systems": {
            "num_rows": 30,
            "extra_columns": [
                "conventional_facies_vs_hebs",
                "confinement",
                "relative_dip_position",
                "relative_strike_position",
            ],
        },
        "complexes": {
            "num_rows": 60,
            "extra_columns": [
                "conventional_facies_vs_hebs",
                "confinement",
                "relative_dip_position",
                "relative_strike_position",
            ],
        },
        "elements": {
            "num_rows": 200,
            "extra_columns": [
                "conventional_facies_vs_hebs",
                "confinement",
                "relative_dip_position",
                "relative_strike_position",
                "spatial_position",
                "architectural_style",
            ],
        },
    },
    "shallow": {
        "systems": {
            "num_rows": 50,
            "extra_columns": [],
        },
        "complexes": {
            "num_rows": 100,
            "extra_columns": [],
        },
        "elements": {
            "num_rows": 600,
            "extra_columns": [],
        },
    },
}
FILEPATH_TEMPLATE = "{dataset}/{table}.json"
READER = "api"


def calculate_quality(ngs):
    quality_thresholds = {
        "Poor <30% NG": (0, 30),
        "Moderate 30-65% NG": (30, 65),
        "Good 65-85% NG": (65, 85),
        "Exceptional 85-100% NG": (85, 101),
    }
    qualities = np.zeros(ngs.shape, dtype="<U22")
    for quality, (low, high) in quality_thresholds.items():
        idx = (ngs >= low) & (ngs < high)
        qualities[idx] = quality

    return qualities


def create_thickness(num_rows):
    thickness = {}
    thickness["base_depth_mtvd"] = np.random.random_sample(num_rows) * 8000
    thickness["thickness_mtvd"] = np.random.random_sample(num_rows) * 100
    thickness["top_depth_mtvd"] = (
        thickness["base_depth_mtvd"] + thickness["thickness_mtvd"]
    )
    return thickness


def set_up_building_block_type(bb_types, num_rows):
    bb_types = [b for b in bb_types if b != "Injectite"]

    bbs = []
    num_types = len(bb_types)
    for idx in range(num_rows):
        bbs.append(bb_types[idx % num_types])

    return bbs


def set_up_ng(num_rows):
    return np.linspace(10, 90, num_rows)


for dataset, dataset_info in DATASETS.items():
    prev_tables = []
    for table, table_info in dataset_info.items():
        num_rows = table_info["num_rows"]

        filepath = pathlib.Path(FILEPATH_TEMPLATE.format(dataset=dataset, table=table))
        filepath.parent.mkdir(parents=True, exist_ok=True)

        table_data = readers.read_all(READER, dataset=dataset, table=table)

        synthetic = {
            "unique_id": np.arange(num_rows),
            "building_block_type": set_up_building_block_type(
                table_data.loc[:, "building_block_type"].unique(), num_rows
            ),
            "ng_vsh40_pct": set_up_ng(num_rows),
            **create_thickness(num_rows),
        }
        synthetic["descriptive_reservoir_quality"] = calculate_quality(
            synthetic["ng_vsh40_pct"]
        )

        for column in table_info["extra_columns"]:
            non_empty_idx = table_data.loc[:, column].astype(str).str.len() > 0
            synthetic[column] = (
                table_data.loc[non_empty_idx, column]
                .sample(num_rows, replace=True)
                .to_numpy()
            )

        for prev_table in prev_tables:
            column = f"parent_{prev_table.rstrip('es')}_identifier"
            prev_rows = DATASETS[dataset][prev_table]["num_rows"]
            synthetic[column] = np.random.randint(prev_rows, size=num_rows)

        logger.info(f"Saving {dataset}.{table} to {filepath}")
        pd.DataFrame(synthetic).to_json(filepath, orient="split")

        prev_tables.append(table)
