"""This code is adapted to be run for two synapse files or tables.
The main function run_compare can be imported into a custom script
to be used to run for entire projects or your own lists/dicts of
synapse ids that you want to compare against
"""

import argparse
import logging
import os
import re
from typing import Any, Dict, List

import datacompy
import pandas as pd
from pandas.testing import assert_frame_equal
import synapseclient
from synapseclient.models import query
from ydata_profiling import ProfileReport

logger = logging.getLogger("compare_report_logger")
logger.setLevel(logging.INFO)


syn = synapseclient.login(silent=True)

DEFAULT_NA_VALUES = [
    "-1.#IND",
    "1.#QNAN",
    "1.#IND",
    "-1.#QNAN",
    "#N/A N/A",
    "#N/A",
    "N/A",
    "n/a",
    "NA",
    "<NA>",
    "#NA",
    "NULL",
    "null",
    "NaN",
    "-NaN",
    "nan",
    "-nan",
    "",
]

DEFAULT_KEEP_DEFAULT_NA = False


def is_synapse_id_version_format(value: str) -> bool:
    """Check if the string value matches the synapse id version format
    for when you are trying to get a specific version of a synapse entity:
        {synapse_id}.{version_id}

    Args:
        value (str): the input synapse id format

    Returns:
        bool: Whether it's in the synapse id version format or not
    """
    pattern = r"^[^.\s]+?\.[^.\s]+?$"
    return bool(re.match(pattern, value))


def get_version_to_compare(
    syn: synapseclient.Synapse, synid: str, version_comment_filter: str
) -> str:
    """Gets the version number

    Args:
        syn (synapseclient.Synapse): synapse client connection
        synid (str): synapse id of entity
        version_comment_filter (str): the version comment to filter on

    Returns:
        str: returns the version number
    """
    results = syn._GET_paginated(f"/entity/{synid}/version")
    for result in results:
        if "versionComment" in result:
            if result["versionComment"] == version_comment_filter:
                return result["versionNumber"]
    return None


def resolve_join_keys(
    df1: pd.DataFrame, df2: pd.DataFrame, join_keys: List[str]
) -> List[str]:
    """Gets join keys as the columns in common
        between the two input dataframes if user inputted
        join keys is NA

    Args:
        df1 (pd.DataFrame): input dataframe 1
        df2 (pd.DataFrame): input dataframe 2
        join_keys (List[str]): user inputted join keys

    Returns:
        List[str]: join keys
    """
    if join_keys is None:
        return list(set(df1.columns).intersection(df2.columns))
    else:
        return join_keys


def resolve_synapse_id_with_version(syn_id: str, version: str = None) -> str:
    """Returns synapse id with version if version is provided otherwise
        returns the regular synapse id

    Args:
        syn_id (str): original user input synapse id
        version (str, optional): version to use for synapse entity.
            Defaults to None.

    Returns:
        str: synapse id with adjusted format
    """
    return f"{syn_id}.{version}" if version else syn_id


def get_synapse_file_or_table_as_dataframe(
    syn: synapseclient.Synapse,
    compare_type: str,
    syn_id: str,
    na_values: List[str] = DEFAULT_NA_VALUES,
    keep_default_na: bool = DEFAULT_KEEP_DEFAULT_NA,
    csv_kwargs: Dict[str, Any] = None,
) -> pd.DataFrame:
    """Takes the synapse file and table and converts it to
        a pandas dataframe for comparison later

    Args:
        syn (synapseclient.Synapse): synapse client connection
        compare_type (str): comparison type - only file or table are allowed
        syn_id (str): synapse id of file
        na_values (list): List of na values to convert from str to na when reading in the data to pandas.
            See docs for pandas.read_csv for more info.
        keep_default_na (bool): Whether to use default NaN values when parsing the data.
            See docs for pandas.read_csv for more info.
        csv_kwargs (Dict[str, Any], optional): Additional keyword arguments to pass directly to
            `pandas.read_csv`. This allows advanced customization such as specifying
            column types, delimiters, quoting behavior, skipping rows, or any other
            supported `read_csv` parameter. User-supplied values override default
            settings used by this utility.

            Examples:
                csv_kwargs={
                    "dtype": {"sample_id": "string"},
                    "sep": "\t",
                    "skiprows": 1,
                    "quoting": 3
                }

            Note:
                These options are only available when calling this function directly
                in Python — they cannot be supplied via the command-line interface
                when using argparse.

    Raises:
        ValueError: when compare_type is not available

    Returns:
        pd.DataFrame: the synapse file converted to dataframe
    """

    if csv_kwargs is None:
        csv_kwargs = {}

    default_params = {
        "na_values": na_values,
        "keep_default_na": keep_default_na,
        "low_memory": False,
        "engine": "c",
    }
    # user args override defaults
    csv_params = {**default_params, **csv_kwargs}

    if compare_type == "table":
        csv_params = {**csv_params, "sep": ","}
        df = query(f"SELECT * FROM {syn_id}", **csv_params).convert_dtypes()
    elif compare_type == "file":
        csv_params = {**csv_params, "sep": "\t"}
        file_path = syn.get(syn_id).path
        df = pd.read_csv(file_path, **csv_params)
    else:
        raise ValueError("Compare type not valid. Only 'table' and 'file' supported.")
    return df


def generate_comparison_reports(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str,
    df2_name: str,
    join_keys: list = None,
) -> Dict[str, Any]:
    """This function will run comparison reports between two datasets
        and flag any differences. This uses datacompy and ydata-profiling.
        Please see those packages for more details on what is in the
        reports. This just uses the basic level reporting for both
        reports.

    Args:
        df1 (pd.DataFrame): 1st dataset in the comparison
        df2 (pd.DataFrame): 2nd dataset in the comparison
        df1_name (str): name for the 1st dataset in the comparison
        df2_name (str): name for the 2nd dataset in the comparison
        report_output_dir (str): output directory for the report(s)
        report_name_prefix (str): prefix for the name of the report(s)
        join_keys (list): List of the keys you want to merge the data on in the comparison. Defaults to None.

    Returns:
        Dict[str, Any]: dictionary of the two report objects:
            comparison_report: is a datacompy report object
            comparison_report_detailed: is a ydata-profiling report object
    """
    join_keys = resolve_join_keys(df1, df2, join_keys)
    # use datacompy for quick report
    compare = datacompy.Compare(
        df1,
        df2,
        join_columns=join_keys,
        df1_name=df1_name,
        df2_name=df2_name,
    )
    compare.matches(ignore_extra_columns=False)

    # use ydataprofiling for thorough report
    original_report = ProfileReport(
        df1,
        title=df1_name,
    )
    transformed_report = ProfileReport(
        df2,
        title=df2_name,
    )
    comparison_report_detailed = original_report.compare(transformed_report)
    logger.info("Report objects created.")

    return {
        "comparison_report": compare,
        "comparison_report_detailed": comparison_report_detailed,
    }


def save_reports(
    syn: synapseclient.Synapse,
    reports: Dict[str, Any],
    report_name_prefix: str,
    output_dir: str,
    output_synid: str = None,
    save_to_synapse: bool = False,
) -> None:
    """Saves the two reports locally. Also saves to synapse if specified.

    Args:
        syn (synapseclient.Synapse): synapse client connection
        reports (Dict[str, Any]): dictionary of the two report objects:
            comparison_report: is a datacompy report object
            comparison_report_detailed: is a ydata-profiling report object
        report_name_prefix (str): prefix for the name of the report(s)
        output_dir (str): local output directory for the report(s)
        output_synid (str): Synapse id of the output entity to save reports to. Defaults to None.
        save_to_synapse (bool, optional): Whether to save reports to Synapse or not. Defaults to False.
    """
    if save_to_synapse and not output_synid:
        raise Exception("Missing output_synid when save_to_synapse is True")

    compare_report_dir = os.path.join(
        output_dir, f"{report_name_prefix}_comparison_report.txt"
    )
    # save datacompy report
    with open(
        compare_report_dir,
        "w",
    ) as comparison_report:
        comparison_report.write(reports["comparison_report"].report())
    logger.info(f"Comparison report generated to {compare_report_dir}")

    # save ydataprofiling report
    compare_report_det_dir = os.path.join(
        output_dir, f"{report_name_prefix}_comparison_report_detailed.html"
    )
    reports["comparison_report_detailed"].to_file(compare_report_det_dir)
    logger.info(f"Detailed comparison report generated to {compare_report_det_dir}")

    # saves to synapse if specified
    if save_to_synapse:
        syn.store(synapseclient.File(compare_report_dir, parent=output_synid))
        syn.store(synapseclient.File(compare_report_det_dir, parent=output_synid))
        logger.info(f"Reports are saved to Synapse under entity {output_synid}.")


def run_compare(
    syn_id_1: str,
    syn_id_2: str,
    version1: str,
    version2: str,
    compare_type: str,
    filter_on_version: bool = False,
    entity_name: str = "",
    main_download_directory: str = None,
    join_keys: list = None,
    na_values: list = DEFAULT_NA_VALUES,
    keep_default_na: bool = False,
    csv_kwargs : Dict[str, Any] = None,
    output_synid: str = None,
    save_to_synapse: bool = False,

) -> None:
    """Runs the main comparison function

    Args:
        syn_id_1 (str): Synapse id of first entity to compare
        syn_id_2 (str): Synapse id of second entity to compare
        version1 (str): Name of first version of entity to use in the comparison.. This will also be part of the reports' output name.
        version2 (str): Name of second version of entity to use in the comparison.. This will also be part of the reports' output name.
        compare_type (str): Comparison type
        filter_on_version (bool): Whether to filter using version comment on the version arguments or not.
            Defaults to False.
        entity_name (str): Name of the entity used in comparison. This will be part of the reports' output name. Optional. Defaults to "".
        main_download_directory (str): Directory to download the reports. Defaults to None.
        join_keys (list): List of the keys you want to merge the data on in the comparison. Defaults to None.
        na_values (list): List of na values to convert from str to na when reading in the data to pandas.
            See docs for pandas.read_csv for more info. Defaults to DEFAULT_NA_VALUES.
        keep_default_na (bool): Whether to use default NaN values when parsing the data.
            See docs for pandas.read_csv for more info. Defaults to False.
        csv_kwargs (dict, optional): Passed through to
            `get_synapse_file_or_table_as_dataframe()` for use with `pandas.read_csv`.
            See that function's documentation for details.
        output_synid (str): Synapse id of the output entity to save reports to. Defaults to None.
        save_to_synapse (bool, optional): Whether to save reports to Synapse or not. Defaults to False.
    """

    if not os.path.exists(main_download_directory):
        os.makedirs(main_download_directory)

    # update version args if filtering on version comment
    if filter_on_version and not is_synapse_id_version_format(syn_id_1):
        version1 = get_version_to_compare(
            syn, synid=syn_id_1, version_comment_filter=version1
        )

    if filter_on_version and not is_synapse_id_version_format(syn_id_2):
        version2 = get_version_to_compare(
            syn, synid=syn_id_2, version_comment_filter=version2
        )

    # filter on version args
    if filter_on_version:
        syn_id_1 = resolve_synapse_id_with_version(syn_id_1, version1)
        syn_id_2 = resolve_synapse_id_with_version(syn_id_2, version2)

    df1 = get_synapse_file_or_table_as_dataframe(
        syn,
        compare_type=compare_type,
        syn_id=syn_id_1,
        na_values=na_values,
        keep_default_na=keep_default_na,
        csv_kwargs=csv_kwargs,
    )
    df2 = get_synapse_file_or_table_as_dataframe(
        syn,
        compare_type=compare_type,
        syn_id=syn_id_2,
        na_values=na_values,
        keep_default_na=keep_default_na,
        csv_kwargs=csv_kwargs,
    )
    # quick check
    try:
        assert_frame_equal(df1, df2)
        logger.info("No differences found!")
    except AssertionError:
        reports = generate_comparison_reports(
            df1=df1,
            df2=df2,
            df1_name=f"df1_{version1}",
            df2_name=f"df2_{version2}",
            join_keys=join_keys,
        )
        save_reports(
            syn = syn,
            reports = reports,
            report_name_prefix = f"{entity_name}_{version1}_vs_{version2}",
            output_dir=main_download_directory,
            output_synid=output_synid,
            save_to_synapse=save_to_synapse,
        )


def read_args():
    parser = argparse.ArgumentParser(
        description="Get comparison of files run on different versions of the repo"
    )
    parser.add_argument(
        "--main-download-directory",
        default=os.getcwd(),
        help="directory to save files in e.g: /home/user/folder",
    )
    parser.add_argument(
        "--syn-id-1",
        help=("Synapse id of first entity to use in the comparison."),
    )
    parser.add_argument(
        "--syn-id-2",
        help=("Synapse id of second entity to use in the comparison."),
    )
    parser.add_argument(
        "--version-name1",
        default="v1",
        help=("Name of first version of entity to use in the comparison."),
    )
    parser.add_argument(
        "--version-name2",
        default="v2",
        help=("Name of second version of entity to use in the comparison."),
    )
    parser.add_argument(
        "--compare-type",
        default="table",
        help=("Name of comparison type. Available: file, table"),
    )
    parser.add_argument(
        "--filter-on-version",
        action="store_true",
        help=(
            "Whether to use the version arguments to filter on version comment or not."
        ),
    )
    parser.add_argument(
        "--entity-name",
        default="",
        help=(
            "Name for the entity you are comparing. This will be the report' output name. Optional."
        ),
    )
    parser.add_argument(
        "--join-keys",
        default=None,
        nargs="+",
        help=(
            "List of column names to join on for comparison. Optional. Default: Uses the columns in common."
        ),
    )
    parser.add_argument(
        "--na-values",
        default=DEFAULT_NA_VALUES,
        nargs="+",
        help=(
            "List of na values to convert from str to na when reading in the data to pandas. "
            "See docs for pandas.read_csv for more info. Default: DEFAULT_NA_VALUES"
        ),
    )
    parser.add_argument(
        "--keep-default-na",
        default=DEFAULT_KEEP_DEFAULT_NA,
        action="store_true",
        help=(
            "Whether to use default NaN values when parsing the data."
            "See docs for pandas.read_csv for more info."
        ),
    )
    parser.add_argument(
        "--save-to-synapse",
        default=False,
        action="store_true",
        help=("Whether to save reports to Synapse on top of saving locally. Optional."),
    )
    parser.add_argument(
        "--output-synid",
        default=None,
        help=("Synapse id of the output entity to store the reports to. Optional."),
    )
    args = parser.parse_args()
    return args


def main():
    args = read_args()
    run_compare(
        syn_id_1=args.syn_id_1,
        syn_id_2=args.syn_id_2,
        version1=args.version_name1,
        version2=args.version_name2,
        compare_type=args.compare_type,
        filter_on_version=args.filter_on_version,
        entity_name=args.entity_name,
        main_download_directory=args.main_download_directory,
        join_keys=args.join_keys,
        na_values=args.na_values,
        keep_default_na=args.keep_default_na,
        output_synid=args.output_synid,
        save_to_synapse=args.save_to_synapse,
    )



if __name__ == "__main__":
    main()
