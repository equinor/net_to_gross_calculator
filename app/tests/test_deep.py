"""Test functionality of Deep Water workflow"""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Geo:N:G imports
from app import stages

from .mocks import readers

# Stages, with dummy initial values
APP = "deep"
STAGES = {
    "set_up": {},
    "composition": {
        "initial_values": {
            "composition": {
                "Lobe": 50,
                "Channel Fill": 30,
                "Overbank": 20,
                "MTD": 0,
                "Drape": 0,
            },
            "filter_classes": {},
        },
        "report_from_set_up": {},
    },
    "filter_classes": {
        "initial_filter_classes": {},
        "report_from_composition": {},
        "net_gross": 28.1,
    },
    "result": {
        "report_from_filter_classes": {
            "building_block_type": {
                "Lobe": 0,
                "Channel Fill": 0,
                "Overbank": 0,
                "MTD": 100,
                "Drape": 0,
            },
            "Lobe": {},
            "Channel Fill": {},
        },
        "net_gross": 28.1,
    },
}


@mock.patch("app.stages.deep.composition.readers", readers)
def get_stage(stage):
    """Get and initialize one stage"""
    stage_obj = stages.get_stage(APP, stage)
    initial_params = STAGES[stage]
    return stage_obj(**initial_params)


@pytest.mark.parametrize("stage", [get_stage(s) for s in STAGES], ids=STAGES)
def test_stage_renders(stage):
    """Test that each stage can be rendered"""
    assert stage.panel()


def test_output_from_set_up():
    """Test that output from set up stage can be calculated"""
    stage = get_stage("set_up")

    # Choose settings covered by the limited test set
    stage.gross_geomorphology = "channel"
    stage.stratigraphic_scale = "complexes"
    stage.reservoir_quality = "Moderate 30-65% NG"

    # Expected output
    expected_composition = {"Channel Fill": 29, "Lobe": 57, "MTD": 14}
    expected_filter_classes = {
        "Channel Fill": {
            "architectural_style": {
                "Laterally Migrating": 50,
                "Overbank Confined": 50,
            },
            "relative_strike_position": {"Off Axis": 100},
        },
        "Lobe": {
            "architectural_style": {"Lobe Non-Channelised": 100},
            "confinement": {
                "Confined": 50,
                "Unconfined": 25,
                "Weakly Confined": 25,
            },
            "conventional_facies_vs_hebs": {
                "Conventional Turbidites": 50,
                "Hybrid Event Beds": 50,
            },
            "spatial_position": {"Zone2": 50, "Zone3": 50},
        },
    }

    # Check actual output
    with mock.patch("app.stages.deep.set_up.readers", readers):
        actual = stage.initial_values()
    assert actual["composition"] == expected_composition
    assert actual["filter_classes"] == expected_filter_classes


def test_composition_of_no_matching_elements():
    """Test that calculation handles no matching elements gracefully"""
    stage = get_stage("set_up")

    # Choose settings not covered by the limited test set
    stage.gross_geomorphology = "fan"
    stage.stratigraphic_scale = "systems"
    stage.reservoir_quality = "Exceptional 85-100% NG"

    # Expected output
    expected_composition = {}
    expected_filter_classes = {
        "Channel Fill": {"architectural_style": {}, "relative_strike_position": {}},
        "Lobe": {
            "architectural_style": {},
            "confinement": {},
            "conventional_facies_vs_hebs": {},
            "spatial_position": {},
        },
    }

    # Check actual output
    with mock.patch("app.stages.deep.set_up.readers", readers):
        actual = stage.initial_values()
    assert actual["composition"] == expected_composition
    assert actual["filter_classes"] == expected_filter_classes


def test_next_enabled_when_weights_total_100():
    stage = get_stage("composition")

    assert stage.total == 100 and stage.sum_to_100


def test_next_disabled_when_weights_dont_total_100():
    stage = get_stage("composition")
    stage.lobe += 1

    assert stage.total != 100 and not stage.sum_to_100


def test_output_from_result():
    stage = get_stage("result")

    expected_net_gross = 28.1
    assert stage.net_gross == pytest.approx(expected_net_gross)
