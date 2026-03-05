from typing import Any, Dict
from unittest import mock

import pandas as pd
import pytest
import synapseclient

import synapse_compare.compare_between_two_synapse_entities as compare


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


def test_get_synapse_file_or_table_as_dataframe_has_no_sep_defaults(mock_syn):
    output_df = pd.DataFrame(dict(col1=[1], col2=[2]))
    mock_entity = mock.Mock()
    mock_entity.path = "test_path"

    with mock.patch.object(
        mock_syn, "get", return_value=mock_entity
    ), mock.patch.object(
        compare, "read_csv_with_auto_sep", return_value=output_df
    ) as mock_read_csv:
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

    with mock.patch.object(compare, "query") as mock_query:
        # setup the mock behavior
        # We chain .return_value because 'query()' returns an object,
        # then we call '.convert_dtypes()' on that object.
        mock_df_final = pd.DataFrame({"col1": [1], "col2": [2]})
        mock_query.return_value.convert_dtypes.return_value = mock_df_final

        # call the function
        df = compare.get_synapse_file_or_table_as_dataframe(
            syn=mock_syn,
            compare_type="table",
            syn_id="syn99999",
        )

        # assertions
        mock_query.assert_called_once()
        assert "SELECT * FROM syn99999" in mock_query.call_args[0][0]
        pd.testing.assert_frame_equal(df, mock_df_final)


def test_save_reports_saves_local_only(tmp_path):
    syn = mock.Mock()

    # Mock report objects
    mock_simple_report = mock.Mock()
    mock_simple_report.report.return_value = "simple report content"

    mock_detailed_report = mock.Mock()

    reports = {
        "comparison_report": mock_simple_report,
        "comparison_report_detailed": mock_detailed_report,
    }

    compare.save_reports(
        syn=syn,
        reports=reports,
        report_name_prefix="test",
        output_dir=str(tmp_path),
        save_to_synapse=False,
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
        "comparison_report_detailed": mock_detailed_report,
    }

    compare.save_reports(
        syn=syn,
        reports=reports,
        report_name_prefix="test",
        output_dir=str(tmp_path),
        output_synid="syn123",
        save_to_synapse=True,
    )

    # Assert Synapse store called twice (txt + html)
    assert syn.store.call_count == 2


def test_save_reports_missing_synid_raises_exception(tmp_path):
    syn = mock.Mock()

    reports = {
        "comparison_report": mock.Mock(),
        "comparison_report_detailed": mock.Mock(),
    }

    with pytest.raises(Exception, match="Missing output_synid"):
        compare.save_reports(
            syn=syn,
            reports=reports,
            report_name_prefix="test",
            output_dir=str(tmp_path),
            save_to_synapse=True,  # True but no output_synid set
        )


def _write(tmp_path, name: str, content: str) -> str:
    """Write content to a file in the given tmp_path and return the file path as a string."""
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_respects_user_sep_and_does_not_auto_detect(tmp_path, monkeypatch):
    path = _write(tmp_path, "data.tsv", "a\tb\n1\t2\n")

    calls: list[Dict[str, Any]] = []
    real_read_csv = pd.read_csv

    def spy_read_csv(*args, **kwargs):
        calls.append(kwargs.copy())
        return real_read_csv(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", spy_read_csv)

    csv_kwargs = {"sep": "\t"}
    df = compare.read_csv_with_auto_sep(path, **csv_kwargs)
    assert df.shape == (1, 2)
    assert list(df.columns) == ["a", "b"]

    # Exactly one call; should use the provided sep
    assert len(calls) == 1
    assert calls[0].get("sep") == "\t"


def test_auto_detect_comma_success(tmp_path):
    path = _write(tmp_path, "data.csv", "a,b\n1,2\n3,4\n")

    df = compare.read_csv_with_auto_sep(path)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
    assert df["a"].tolist() == [1, 3]
    assert df["b"].tolist() == [2, 4]


def test_auto_detect_falls_back_to_tab_when_comma_results_in_one_column(tmp_path):
    # If you read this with sep="," you'll get a single column like "a\tb"
    path = _write(tmp_path, "data.tsv", "a\tb\n1\t2\n3\t4\n")

    df = compare.read_csv_with_auto_sep(path)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
    assert df["a"].tolist() == [1, 3]
    assert df["b"].tolist() == [2, 4]


def test_raises_value_error_when_neither_comma_nor_tab_produces_table(tmp_path):
    # Single column no matter what separator you choose
    path = _write(tmp_path, "onecol.txt", "only_one_column\n1\n2\n")

    with pytest.raises(ValueError, match="Unable to determine delimiter"):
        compare.read_csv_with_auto_sep(path)


def test_does_not_mutate_csv_kwargs(tmp_path):
    path = _write(tmp_path, "data.csv", "a,b\n1,2\n")
    csv_kwargs = {"dtype": {"a": "int64"}}

    _ = compare.read_csv_with_auto_sep(path, **csv_kwargs)
    assert csv_kwargs == {"dtype": {"a": "int64"}}


def test_user_sep_parser_error_is_propagated(tmp_path, monkeypatch):
    """
    When the user supplies sep, the function should not swallow ParserError
    (per the docstring).
    """
    path = _write(tmp_path, "data.csv", "a,b\n1,2\n")

    def raise_parser_error(*args, **kwargs):
        raise pd.errors.ParserError("boom")

    monkeypatch.setattr(pd, "read_csv", raise_parser_error)

    with pytest.raises(ValueError, match="boom"):
        compare.read_csv_with_auto_sep(path, sep=",")


def test_auto_detect_handles_parser_error_then_succeeds_on_tab(tmp_path, monkeypatch):
    """
    Simulate comma parse raising ParserError, then tab parse succeeding.
    This makes sure the 'except ParserError: pass' path is covered.
    """
    path = _write(tmp_path, "data.tsv", "a\tb\n1\t2\n")

    real_read_csv = pd.read_csv
    state = {"calls": 0}

    def fake_read_csv(*args, **kwargs):
        # First attempt (comma) fails; second attempt (tab) delegates to pandas
        state["calls"] += 1
        if state["calls"] == 1:
            raise pd.errors.ParserError("comma parse failed")
        return real_read_csv(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    df = compare.read_csv_with_auto_sep(path)
    assert df.shape == (1, 2)
    assert list(df.columns) == ["a", "b"]
