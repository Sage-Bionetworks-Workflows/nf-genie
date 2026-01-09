"""
Simple script to create the Patient Sample Tracking table.
This can spin up the table if it ever gets deleted/easy to track
the original column settings and automate the schema generation from an input
data model file
"""

import argparse
from typing import List

import synapseclient
from synapseclient.models import Column, Table


STRING_COLS = [
    "SAMPLE_ID",
    "PATIENT_ID",
    "MAIN_GENIE_RELEASE",
    "BPC_CRC2_RELEASE",
    "BPC_PANC_RELEASE",
    "BPC_RENAL_RELEASE",
    "BPC_BLADDER_RELEASE",
    "BPC_BRCA_RELEASE",
    "BPC_NSCLC_RELEASE",
    "BPC_PROSTATE_RELEASE",
]

BOOLEAN_COLS = [
    "IN_LATEST_MAIN_GENIE",
    "IN_AKT1_PROJECT",
    "IN_BRCA_DDR_PROJECT",
    "IN_ERBB2_PROJECT",
    "IN_FGFE4_PROJECT",
    "IN_KRAS_PROJECT",
    "IN_NTRK_PROJECT",
    "IN_BPC_CRC_RELEASE",
    "IN_BPC_CRC2_RELEASE",
    "IN_BPC_PANC_RELEASE",
    "IN_BPC_RENAL_RELEASE",
    "IN_BPC_BLADDER_RELEASE",
    "IN_BPC_BRCA_RELEASE",
    "IN_BPC_NSCLC_RELEASE",
    "IN_BPC_PROSTATE_RELEASE",
]


def create_columns() -> List[Column]:
    """
    Creates the columns of the schema.
    Build Synapse Column objects in the desired order:
      SAMPLE_ID, PATIENT_ID, then IN_* booleans, then release-name strings.

    Returns:
        List[Column]: list of the column schemas in the table
    """
    columns: List[Column] = []

    # strings first
    for name in ["SAMPLE_ID", "PATIENT_ID"]:
        columns.append(
            Column(
                name=name,
                column_type="STRING",
                maximum_size=250,
            )
        )

    # boolean flags
    for name in BOOLEAN_COLS:
        # SAMPLE_ID and PATIENT_ID are already added; skip if present by mistake
        if name in ("SAMPLE_ID", "PATIENT_ID"):
            continue
        columns.append(
            Column(
                name=name,
                column_type="BOOLEAN",
            )
        )

    # release-name strings (and any other non-boolean strings)
    # NOTE: STRING_COLS already includes SAMPLE_ID/PATIENT_ID; skip duplicates
    for name in STRING_COLS:
        if name in ("SAMPLE_ID", "PATIENT_ID"):
            continue
        columns.append(
            Column(
                name=name,
                column_type="STRING",
                maximum_size=250,
            )
        )

    return columns


def create_table(project_synid: str, table_name: str) -> None:
    """Create and initializes the empty Synapse Table
        using the table schema generated from the data model

    Args:
        syn (synapseclient.Synapse): synapse client connection
        data_model_synid (str): synapse id of the input data model to parse
        project_synid (str): synapse if of the synapse project to create table in
        table_name (str): name of the table to create
    """
    columns = create_columns()

    table = Table(
        name=table_name,
        columns=columns,
        parent_id=project_synid,
    )
    table = table.store()
    print(f"Created table: {table.name} ({table.id})")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Synapse table schema from a data model."
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
    syn = synapseclient.login()
    create_table(project_synid=args.project_synid, table_name=args.table_name)


if __name__ == "__main__":
    main()
