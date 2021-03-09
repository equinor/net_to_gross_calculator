# Standard library imports
import pathlib

# Third party imports
import pandas as pd
import pytest
from pyconfs import Configuration

# Geo:N:G imports
from api import config
from api.models import calculate


@pytest.fixture
def synthetic_data():
    return pd.DataFrame(
        [
            ["type_1", "A", 0.1],
            ["type_1", "A", 0.2],
            ["type_1", "B", 0.2],
            ["type_1", "C", 0.5],
            ["type_2", "", 0.7],
            ["type_2", "", 0.8],
        ],
        columns=["type", "key", "value"],
    )


@pytest.fixture
def synthetic_config():
    return Configuration.from_str(
        """
        [models]
        target          = "value"
        label_column    = "type"

          [models.type_1]
          label           = "type_1"
          factors         = ["key"]
          key             = ["A", "B", "C"]

          [models.type_2]
          label           = "type_2"
          factors         = []
        """,
        format="toml",
    ).models


@pytest.fixture
def simplified_data():
    return pd.read_csv(
        pathlib.Path(__file__).resolve().parent / "simplified_elements.csv"
    )


@pytest.fixture
def model_config():
    return config.api.models.deep


def test_synthetic_model(synthetic_data, synthetic_config):
    models = calculate(synthetic_data, synthetic_config)
    expected = pd.DataFrame(
        [
            ["type_1", "A", 0.15],
            ["type_1", "B", 0.2],
            ["type_1", "C", 0.5],
            ["type_2", "", 0.75],
        ],
        columns=["type", "key", "net_gross"],
    )
    pd.testing.assert_frame_equal(models, expected)


def test_model_with_config(simplified_data, model_config):
    models = calculate(simplified_data, model_config)

    # Test the output of some models
    assert models.query(
        "building_block_type == 'MTD'"
    ).net_gross.item() == pytest.approx(0.41)
    assert models.query(
        "building_block_type == 'Channel Fill' "
        "and relative_strike_position == 'Off Axis' "
        "and architectural_style == 'Laterally Migrating'"
    ).net_gross.item() == pytest.approx(0.925)
    assert models.groupby("building_block_type").mean().loc[
        "Lobe", "net_gross"
    ] == pytest.approx(0.6677, abs=1e-4)

    # Sanity checks on all models
    assert models.net_gross.min() >= 0
    assert models.net_gross.max() <= 1
    assert len(models) == 48
    assert len(models.query("building_block_type == 'Lobe'")) == 36
    assert len(models.query("building_block_type == 'Channel Fill'")) == 9
