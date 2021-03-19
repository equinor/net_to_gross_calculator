"""Check dataset tables for duplicates in the unique_id columns"""

# Standard library imports
import itertools
import pathlib

# Third party imports
import pandas as pd

# Geo:N:G imports
from app import config
from geong_common import log
from geong_common import readers
from geong_common.log import logger

DATASETS = ["deep", "shallow"]
TABLES = ["systems", "complexes", "elements"]
EXCEL_PATH = pathlib.Path("duplicates.xlsx").resolve()

log.init()
excel = pd.ExcelWriter(EXCEL_PATH, engine="xlsxwriter")

for dataset, table in itertools.product(DATASETS, TABLES):
    data = readers.read_all(config.app.apps.reader, dataset, table)
    duplicated_ids = (
        data.groupby("unique_id")
        .size()
        .to_frame()
        .rename(columns={0: "count"})
        .query("count > 1")
        .reset_index()
    )
    num_duplicates = len(duplicated_ids)
    log_func = logger.info if num_duplicates == 0 else logger.warning
    log_func(f"Found {num_duplicates} duplicates in {dataset}.{table}")
    (
        duplicated_ids.merge(data, on="unique_id", how="left").to_excel(
            excel, sheet_name=f"{dataset}-{table}"
        )
    )

logger.info(f"Storing duplicate information in {EXCEL_PATH}")
excel.save()
