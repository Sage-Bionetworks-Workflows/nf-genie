from unittest import mock

import pandas as pd
import pytest
import synapseclient

from scripts.release_utils import consortium_to_bpc as to_bpc


@pytest.fixture(scope="session")
def syn():
    return mock.create_autospec(synapseclient.Synapse)

@pytest.mark.parametrize(
    "is_test, expected",
    [
        (
            True,
            {
                "data_folder_synid": "syn53879650",
                "release_table_synid": "syn12299959",
            },
        ),
        (
            False,
            {
                "data_folder_synid": "syn21574209",
                "release_table_synid": "syn16804261",
            },
        ),
    ],
    ids=["test_is_true", "test_is_false"],
)
def test_that_release_synids_returns_expected(is_test, expected):
    result = to_bpc.get_release_synids(test=is_test)
    assert result == expected


def test_that_find_release_raises_error_if_empty_release_table(syn):
    with mock.patch.object(syn, "tableQuery") as patch_table_query:
        table_mock = mock.MagicMock()
        patch_table_query.return_value = table_mock

        with mock.patch.object(
            table_mock, "asDataFrame", return_value=pd.DataFrame()
        ), pytest.raises(ValueError, match="Please specify correct release value"):
            to_bpc.find_release(
                syn, release="TEST", release_table_synid="synZZZZ", test=False
            )


def test_that_find_release_does_expected_calls_if_test_false(syn):
    with mock.patch.object(syn, "tableQuery") as patch_table_query:
        table_mock = mock.MagicMock()
        patch_table_query.return_value = table_mock

        with mock.patch.object(
            table_mock, "asDataFrame", return_value=pd.DataFrame({"col1": ["synYYYY"]})
        ):
            release_synid = to_bpc.find_release(
                syn, release="TEST", release_table_synid="synZZZZ", test=False
            )
            patch_table_query.assert_called_once_with(
                "select distinct(parentId) from synZZZZ where " "release = 'TEST'"
            )
            assert release_synid == "synYYYY"


def test_that_find_release_does_expected_calls_if_test_true(syn):
    with mock.patch.object(syn, "tableQuery") as patch_table_query:
        release_synid = to_bpc.find_release(
            syn, release="TEST", release_table_synid="synZZZZ", test=True
        )
        patch_table_query.assert_not_called()
        assert release_synid == "synZZZZ"