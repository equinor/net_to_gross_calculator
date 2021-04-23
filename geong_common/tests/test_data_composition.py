"""Test composition of data"""

# Third party imports
import pandas as pd
import pytest

# Geo:N:G imports
from geong_common.data import composition


@pytest.fixture
def synthetic_elements():
    return pd.DataFrame(
        [
            ["type_1", "A", "blue"],
            ["type_1", "A", "green"],
            ["type_1", "B", "blue"],
            ["type_1", "C", "blue"],
            ["type_2", "", "red"],
            ["type_2", "", "green"],
        ],
        columns=["building_block_type", "letter", "color"],
    )


def test_composition_of_one_group(synthetic_elements):
    actual = composition.calculate_composition_in_group(
        elements=synthetic_elements, column="building_block_type"
    )
    expected = {"type_1": 67, "type_2": 33}

    assert actual == expected


def test_composition_threshold(synthetic_elements):
    actual = composition.calculate_composition_in_group(
        elements=synthetic_elements, column="building_block_type", threshold=40
    )
    expected = {"type_1": 100}

    assert actual == expected


def test_composition_inside_classes(synthetic_elements):
    actual = composition.calculate_filter_classes(
        elements=synthetic_elements,
        filter_classes=[
            ("type_1", "letter"),
            ("type_1", "color"),
            ("type_2", "letter"),
            ("type_2", "color"),
        ],
    )
    expected = {
        "type_1": {
            "letter": {"A": 50, "B": 25, "C": 25},
            "color": {"blue": 75, "green": 25},
        },
        "type_2": {
            "letter": {"": 100},
            "color": {"red": 50, "green": 50},
        },
    }

    assert actual == expected
