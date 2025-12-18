from unittest import mock

import pandas as pd
import pytest
import synapseclient

import compare_between_two_synapse_entities as compare


@pytest.fixture
def mock_syn():
    yield mock.Mock(spec=synapseclient.Synapse)


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("syn122453.3", True),
        ("syn129841.23", True),
        ("syn9841924", False),
    ],
    ids=[
        "single_digit_version_num",
        "two_digit_version_num",
        "no_version_num",
    ],
)
def test_that_is_synapse_id_version_format_gives_expected_result(input_value, expected):
    result = compare.is_synapse_id_version_format(value=input_value)
    assert expected == result


@pytest.mark.parametrize(
    "version_filter_results, input_version_comment_filter, expected_version_number",
    [
        (
            [
                {
                    "id": "synZZZZZ",
                    "versionNumber": 10,
                    "versionComment": "test_version_comment",
                }
            ],
            "test_version_comment",
            10,
        ),
        ([{"id": "synZZZZZ", "versionNumber": 10}], "test_version_comment", None),
        (
            [
                {
                    "id": "synZZZZZ",
                    "versionNumber": 10,
                    "versionComment": "test_version_comment",
                },
                {
                    "id": "synZZZZZ",
                    "versionNumber": 9,
                    "versionComment": "test_version_comment",
                },
            ],
            "test_version_comment",
            10,
        ),
        (
            [
                {
                    "id": "synZZZZZ",
                    "versionNumber": 10,
                    "versionComment": "test_no_match_version_comment",
                }
            ],
            "test_version_comment",
            None,
        ),
    ],
    ids=[
        "matching_version_comment",
        "no_version_comments",
        "duplicated_version_comments",
        "no_matching_version_comments",
    ],
)
def test_that_get_version_to_compare_returns_expected_version(
    mock_syn,
    version_filter_results,
    input_version_comment_filter,
    expected_version_number,
):
    with mock.patch.object(
        mock_syn, "_GET_paginated", return_value=version_filter_results
    ):
        result = compare.get_version_to_compare(
            mock_syn,
            synid="synTEST",
            version_comment_filter=input_version_comment_filter,
        )
        assert expected_version_number == result


@pytest.mark.parametrize(
    "input_df1, input_df2, input_join_keys, expected_join_keys",
    [
        (
            pd.DataFrame(dict(col1=[1], col2=[2])),
            pd.DataFrame(dict(col1=[1], col3=[2])),
            None,
            ["col1"],
        ),
        (
            pd.DataFrame(dict(col1=[1], col2=[2])),
            pd.DataFrame(dict(col3=[1], col4=[2])),
            None,
            [],
        ),
        (
            pd.DataFrame(dict(col1=[1], col2=[2])),
            pd.DataFrame(dict(col1=[1], col2=[2], col3=[3])),
            ["col2"],
            ["col2"],
        ),
    ],
    ids=["no_input_join_keys", "no_columns_in_common", "user_input_keys"],
)
def test_resolve_join_keys_returns_expected(
    input_df1, input_df2, input_join_keys, expected_join_keys
):
    result = compare.resolve_join_keys(input_df1, input_df2, input_join_keys)
    assert expected_join_keys == result


@pytest.mark.parametrize(
    "input_syn_id, input_version, expected_result",
    [("syn12741", None, "syn12741"), ("syn12741", 21, "syn12741.21")],
    ids=["no_version", "with_version"],
)
def test_resolve_synapse_id_with_version_returns_expected_format(
    input_syn_id, input_version, expected_result
):
    result = compare.resolve_synapse_id_with_version(
        syn_id=input_syn_id, version=input_version
    )
    assert expected_result == result


def test_get_synapse_file_or_table_as_dataframe_defaults_to_comma(mock_syn):
    output_df = pd.DataFrame(dict(col1=[1], col2=[2]))
    mock_entity = mock.Mock()
    mock_entity.path = "test_path"

    with mock.patch.object(
        mock_syn, "get", return_value=mock_entity
    ), mock.patch.object(pd, "read_csv", return_value=output_df) as mock_read_csv:
        compare.get_synapse_file_or_table_as_dataframe(
            syn=mock_syn,
            compare_type="file",
            syn_id="syn23423",
            na_values=compare.DEFAULT_NA_VALUES,
            keep_default_na=False,
        )
        mock_read_csv.assert_called_once_with(
            "test_path",
            na_values=compare.DEFAULT_NA_VALUES,
            keep_default_na=False,
            low_memory=False,
            engine="c",
            sep=",",
        )


def test_get_synapse_file_or_table_as_dataframe_respects_csv_kwargs(mock_syn):
    output_df = pd.DataFrame()
    mock_entity = mock.Mock()
    mock_entity.path = "test_path"

    with mock.patch.object(
        mock_syn, "get", return_value=mock_entity
    ), mock.patch.object(pd, "read_csv", return_value=output_df) as mock_read_csv:
        compare.get_synapse_file_or_table_as_dataframe(
            syn=mock_syn,
            compare_type="file",
            syn_id="syn23423",
            na_values=compare.DEFAULT_NA_VALUES,
            keep_default_na=False,
            csv_kwargs={"sep": "\t", "dtype": {"col1": "string"}},
        )
        mock_read_csv.assert_called_once_with(
            "test_path",
            na_values=compare.DEFAULT_NA_VALUES,
            keep_default_na=False,
            low_memory=False,
            engine="c",
            sep="\t",
            dtype={"col1": "string"},
        )


def test_get_synapse_file_or_table_as_dataframe_table_query(mock_syn):
    # Mock Synapse TableQuery result
    mock_query_result = mock.Mock()
    mock_df = pd.DataFrame({"col1": [1], "col2": [2]})
    mock_query_result.asDataFrame.return_value = mock_df

    # make syn.tableQuery return our mock
    mock_syn.tableQuery.return_value = mock_query_result

    df = compare.get_synapse_file_or_table_as_dataframe(
        syn=mock_syn,
        compare_type="table",
        syn_id="syn99999",
        na_values=compare.DEFAULT_NA_VALUES,
        keep_default_na=True,
    )

    # assert query was called correctly
    mock_syn.tableQuery.assert_called_once_with("SELECT * FROM syn99999")

    # Assert the DataFrame returned is the mocked DataFrame
    assert isinstance(df, pd.DataFrame)
    pd.testing.assert_frame_equal(df, mock_df)


def test_save_reports_saves_local_only(tmp_path):
    syn = mock.Mock()

    # Mock report objects
    mock_simple_report = mock.Mock()
    mock_simple_report.report.return_value = "simple report content"

    mock_detailed_report = mock.Mock()

    reports = {
        "comparison_report": mock_simple_report,
        "comparison_report_detailed": mock_detailed_report
    }

    compare.save_reports(
        syn=syn,
        reports=reports,
        report_name_prefix="test",
        output_dir=str(tmp_path),
        save_to_synapse=False
    )

    # Assert files created
    txt_file = tmp_path / "test_comparison_report.txt"
    html_file = tmp_path / "test_comparison_report_detailed.html"

    # validating text file
    assert txt_file.exists()
    assert txt_file.read_text() == "simple report content"

    # validating html file
    mock_detailed_report.to_file.assert_called_once_with(str(html_file))

    # Confirm NO Synapse store calls
    syn.store.assert_not_called()


def test_save_reports_saves_to_synapse(tmp_path):
    syn = mock.Mock()

    mock_simple_report = mock.Mock()
    mock_simple_report.report.return_value = "simple report content"

    mock_detailed_report = mock.Mock()

    reports = {
        "comparison_report": mock_simple_report,
        "comparison_report_detailed": mock_detailed_report
    }

    compare.save_reports(
        syn=syn,
        reports=reports,
        report_name_prefix="test",
        output_dir=str(tmp_path),
        output_synid="syn123",
        save_to_synapse=True
    )

    # Assert Synapse store called twice (txt + html)
    assert syn.store.call_count == 2


def test_save_reports_missing_synid_raises_exception(tmp_path):
    syn = mock.Mock()

    reports = {
        "comparison_report": mock.Mock(),
        "comparison_report_detailed": mock.Mock()
    }

    with pytest.raises(Exception, match="Missing output_synid"):
        compare.save_reports(
            syn=syn,
            reports=reports,
            report_name_prefix="test",
            output_dir=str(tmp_path),
            save_to_synapse=True,  # True but no output_synid set
        )
