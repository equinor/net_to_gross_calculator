"""Get an overview of the shallow data"""

# Standard library imports
import itertools
import pathlib

# Third party imports
import pandas as pd

# Geo:N:G imports
from app import config
from app.stages.shallow import result
from geong_common import log
from geong_common import readers
from geong_common.data import composition
from geong_common.log import logger

KDIMS = ["building_block_type", "descriptive_reservoir_quality"]
TABLES = ["complexes", "systems", "elements"]
EXCEL_PATH = pathlib.Path("shallow_data.xlsx").resolve()

log.init()

excel = pd.ExcelWriter(EXCEL_PATH, engine="xlsxwriter")
reader = config.app.apps.reader

overviews = {}
for table in TABLES:
    data = readers.read_all(reader, dataset="shallow", table=table)
    overview = overviews[table] = (
        data.groupby(KDIMS).size().to_frame().rename(columns={0: "Count"})
    )
    overview.to_excel(excel, sheet_name=table.title())

readers.read_model(reader, "shallow").to_excel(excel, sheet_name="Model")

model_results = []
for depositional, scale, bracket, threshold in itertools.product(
    ("Delta", "Shoreface", "Estuary", "Fan Delta"),
    ("complexes", "systems"),
    (
        "Poor <30% NG",
        "Moderate 30-65% NG",
        "Good 65-85% NG",
        "Exceptional 85-100% NG",
    ),
    (0, 6, 12),
):
    elements = readers.read_elements(reader, "shallow", scale)
    comp = composition.calculate_composition_in_group(
        elements.query(
            "building_block_type_table == @depositional"
            " and descriptive_reservoir_quality_table == @bracket"
        ),
        "building_block_type",
        threshold=threshold,
    )
    ng = result.calculate_net_gross(comp)
    model_results.append([depositional, scale, bracket, threshold, ng, str(comp)])

pd.DataFrame(
    model_results,
    columns=[
        "Depositional setting",
        "Stratigraphic scale",
        "Quality bracket",
        "Threshold",
        "Net:Gross",
        "Composition",
    ],
).to_excel(excel, sheet_name="Model results")

for threshold in range(0, 16, 3):
    compositions = {}
    for table in ["complexes", "systems"]:
        elements = readers.read_elements(reader, "shallow", table)
        for (bbt, drq), group in elements.groupby([f"{d}_table" for d in KDIMS]):
            comp = composition.calculate_composition_in_group(
                group, "building_block_type", threshold=threshold
            )
            compositions[table, bbt, drq] = [len(comp), str(comp)]

    pd.DataFrame.from_dict(
        compositions,
        columns=["Count", f"Composition (Threshold {threshold})"],
        orient="index",
    ).to_excel(excel, sheet_name=f"Comp. > {threshold}")

logger.info(f"Saving information to {EXCEL_PATH}")
excel.save()
