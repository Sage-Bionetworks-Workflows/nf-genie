"""
Simple script to create the Patient Sample Tracking table.
This can spin up the table if it ever gets deleted/easy to track
the original column settings and automate the schema generation from an input
data model file
"""

import argparse
from typing import List

import pandas as pd
import synapseclient
from synapseclient.models import Column, Table

syn = synapseclient.login()

def get_data_model(synid: str) -> pd.DataFrame:
    """Converts the data model into pandas dataframe for
        parsing later

    Args:
        synid (str): synapse id of the data model file

    Returns:
        pd.DataFrame: data model as pandas dataframe
    """
    data_model = pd.read_csv(syn.get(synid).path, sep="\t")
    return data_model


def get_synapse_col_type(validation_rule: str) -> str:
    """Helper to map validation rules to
        Synapse column types

    Args:
        validation_rule (str): the value,
            current supported values are
            ['bool', 'int', 'float', 'date', 'str']

    Returns:
        str: string representation of the rule translated
        to synapse table column data types
    """
    rules_map = {
        "boolean": "BOOLEAN",
        "int": "INTEGER",
        "float": "DOUBLE",
        "date": "DATE",
        "str": "STRING",
    }
    if pd.isna(validation_rule):
        return "STRING"
    rule = validation_rule.lower()

    if rule in rules_map.keys():
        return rules_map[rule]
    else:
        raise ValueError(
            f"{rule} is not one of the supported rules: {rules_map.keys()}"
        )


def create_columns(data_model: pd.DataFrame) -> List[Column]:
    """Creates the columns of the schema with
        column type, valid values and enum values filled out
        where applicable

    Args:
        data_model (pd.DataFrame): table of the data model
            to parse for the schema values

    Returns:
        List[Column]: list of the column schemas in the table
    """
    # Build list of Columns (with Restrict Values)
    columns = []
    for _, row in data_model.iterrows():
        name = row["Attribute"].strip()
        col_type = get_synapse_col_type(row.get("Validation Rules", ""))
        valid_values = row.get("Valid Values")

        # Parse Restrict Values if available
        enum_values = None
        if isinstance(valid_values, str) and "," in valid_values:
            # Split on commas and strip whitespace
            enum_values = [v.strip() for v in valid_values.split(",") if v.strip()]

        col = Column(
            name=name,
            column_type=col_type,
            enum_values=enum_values,  # this is the "Restrict Values" list
            maximum_size=250 if col_type == "STRING" else None,
        )
        columns.append(col)
    return columns


def create_table(data_model_synid: str, project_synid: str, table_name: str) -> None:
    """Create and initializes the empty Synapse Table
        using the table schema generated from the data model

    Args:
        data_model_synid (str): synapse id of the input data model to parse
        project_synid (str): synapse if of the synapse project to create table in
        table_name (str): name of the table to create
    """
    data_model = get_data_model(synid=data_model_synid)
    columns = create_columns(data_model)
    # Create an empty table instance with the schema
    table = Table(
        name=table_name,
        columns=columns,
        parent_id=project_synid,
    )
    table = table.store()
    print(f"Created table: {table.name} ({table.id})")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Synapse table schema from a data model TSV."
    )
    parser.add_argument(
        "--data-model-synid",
        default="syn71411200",
        help="Synapse ID of the data model TSV (e.g. syn71411200).",
    )
    parser.add_argument(
        "--project-synid",
        default="syn22033066",  # staging project
        help="Synapse ID of the project to create the table in (e.g. syn22033066).",
    )
    parser.add_argument(
        "--table-name",
        default="STAGING Patient and Sample Tracking Table",
        help="Name of the patient tracking table to create.",
    )

    args = parser.parse_args()
    create_table(
        data_model_synid=args.data_model_synid,
        project_synid=args.project_synid,
        table_name=args.table_name,
    )


if __name__ == "__main__":
    main()
