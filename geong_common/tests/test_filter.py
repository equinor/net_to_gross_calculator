# Third party imports
import numpy as np
import pandas as pd
import pytest

# Geo:N:G imports
from geong_common.data.models import filter_data


@pytest.fixture()
def single_column_row():
    return pd.DataFrame.from_dict({"key": ["val"]})


@pytest.fixture()
def data_multiple():
    return pd.DataFrame.from_dict(
        {"key0": ["val00", "val01"], "key1": ["val10", "val11"]}
    )


def test_no_filter(single_column_row):
    result = filter_data(single_column_row, {})
    assert result.compare(single_column_row).empty


def test_filter_match_single_element(single_column_row):
    result = filter_data(single_column_row, {"key": "val"})
    assert result.compare(single_column_row).empty


def test_filter_no_match(single_column_row):
    result = filter_data(single_column_row, {"key": "missing_value"})
    assert result.empty


def test_filter_unknown_key(single_column_row):
    with pytest.raises(KeyError):
        filter_data(single_column_row, {"unknown_key": ""})


def test_filter_non_overlapping_selection_is_empty(data_multiple):
    result = filter_data(data_multiple, {"key0": "val00", "key1": "val11"})
    assert result.empty


def test_filter_select_one_row(data_multiple):
    result = filter_data(data_multiple, {"key0": "val00"})
    assert (result.to_numpy() == np.array([["val00", "val10"]])).all()


def test_filter_select_one_row_multiple_keys(data_multiple):
    result = filter_data(data_multiple, {"key0": "val00", "key1": "val10"})
    assert (result.to_numpy() == np.array([["val00", "val10"]])).all()
