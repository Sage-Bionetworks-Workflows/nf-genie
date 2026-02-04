"""
Simple script to create the Patient Sample Tracking table.
This can spin up the table if it ever gets deleted/easy to track
the original column settings and automate the schema generation from an input
data model file
"""

import argparse
from typing import List

import synapseclient
from synapseclient import Wiki
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


def create_table(project_synid: str, table_name: str) -> Table:
    """Create and initializes the empty Synapse Table
        using the table schema generated from the data model

    Args:
        syn (synapseclient.Synapse): synapse client connection
        data_model_synid (str): synapse id of the input data model to parse
        project_synid (str): synapse if of the synapse project to create table in
        table_name (str): name of the table to create

    Returns:
        Table: Synapse table entity that was created
    """
    columns = create_columns()

    table = Table(
        name=table_name,
        columns=columns,
        parent_id=project_synid,
    )
    table = table.store()
    print(f"Created table: {table.name} ({table.id})")
    return table


def add_table_wiki(syn : synapseclient.Synapse, table: Table) -> None:
    """Adds the wiki with instructions and examples for the table
        and how to use it

    Args:
        syn (synapseclient.Synapse): synapse client connection
        table (Table): synapse table entity
    """

    content = """${toc}
    ##Overview
    This Patient-Sample tracking table contains ALL of the `SAMPLE_ID`, `PATIENT_ID` across all of the **latest** versions of each project type: BPC, MAIN Genie and SP. There will be just one unique record per patient id-sample-id in this table.

    Here is the data dictionary for the table and its attributes
    | ATTRIBUTE                 | DESCRIPTION                                                                                                                                                                                                    | REQUIRED | CAN HAVE MISSING VALUES |
    | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------ |
    | `SAMPLE_ID`               | Sample identifier for the given sample-patient pair.                                                                                                                                                           | YES      | NO                       |
    | `PATIENT_ID`              | Patient identifier for the given sample-patient pair.                                                                                                                                                          | YES      | NO                       |
    | `IN_LATEST_MAIN_GENIE`    | Whether the sample-patient pair is present in the latest MAIN GENIE release.                                                                                                                                   | YES      | NO                       |
    | `IN_AKT1_PROJECT`         | Whether the sample-patient pair exists in the AKT1 sponsored project dataset (regardless of MAIN GENIE membership).                                                                                            | YES      | NO                       |
    | `IN_BRCA_DDR_PROJECT`     | Whether the sample-patient pair exists in the BRCA_DDR sponsored project dataset (regardless of MAIN GENIE membership).                                                                                        | YES      | NO                       |
    | `IN_ERBB2_PROJECT`        | Whether the sample-patient pair exists in the ERBB2 sponsored project dataset (regardless of MAIN GENIE membership).                                                                                           | YES      | NO                       |
    | `IN_FGFE4_PROJECT`        | Whether the sample-patient pair exists in the FGFE4 sponsored project dataset (regardless of MAIN GENIE membership).                                                                                           | YES      | NO                       |
    | `IN_KRAS_PROJECT`         | Whether the sample-patient pair exists in the KRAS sponsored project dataset (regardless of MAIN GENIE membership).                                                                                            | YES      | NO                       |
    | `IN_NTRK_PROJECT`         | Whether the sample-patient pair exists in the NTRK sponsored project dataset (regardless of MAIN GENIE membership).                                                                                            | YES      | NO                       |
    | `IN_BPC_CRC_RELEASE`      | Whether the sample-patient pair exists in the latest CRC BPC cohort release slice used for tracking (latest-per-cohort).                                                                                       | YES      | NO                       |
    | `IN_BPC_CRC2_RELEASE`     | Whether the sample-patient pair exists in the latest CRC2 BPC cohort release slice used for tracking (latest-per-cohort).                                                                                      | YES      | NO                       |
    | `IN_BPC_PANC_RELEASE`     | Whether the sample-patient pair exists in the latest PANC BPC cohort release slice used for tracking (latest-per-cohort).                                                                                      | YES      | NO                       |
    | `IN_BPC_RENAL_RELEASE`    | Whether the sample-patient pair exists in the latest RENAL BPC cohort release slice used for tracking (latest-per-cohort).                                                                                     | YES      | NO                       |
    | `IN_BPC_BLADDER_RELEASE`  | Whether the sample-patient pair exists in the latest BLADDER BPC cohort release slice used for tracking (latest-per-cohort).                                                                                   | YES      | NO                       |
    | `IN_BPC_BRCA_RELEASE`     | Whether the sample-patient pair exists in the latest BRCA BPC cohort release slice used for tracking (latest-per-cohort).                                                                                      | YES      | NO                       |
    | `IN_BPC_NSCLC_RELEASE`    | Whether the sample-patient pair exists in the latest NSCLC BPC cohort release slice used for tracking (latest-per-cohort).                                                                                     | YES      | NO                       |
    | `IN_BPC_PROSTATE_RELEASE` | Whether the sample-patient pair exists in the latest PROSTATE BPC cohort release slice used for tracking (latest-per-cohort).                                                                                  | YES      | NO                       |
    | `MAIN_GENIE_RELEASE`      | Release identifier for the latest MAIN GENIE release used for tracking (e.g., `NN.N-public`). Populated for pairs where `IN_LATEST_MAIN_GENIE` is true; otherwise may be null/blank.                           | YES      | YES                      |
    | `BPC_CRC2_RELEASE`        | Release identifier for the latest CRC2 BPC cohort release used for tracking (e.g., `CRC2_17.0-consortium` or similar). Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank. | YES      | YES                      |
    | `BPC_PANC_RELEASE`        | Release identifier for the latest PANC BPC cohort release used for tracking (e.g., `PANC_17.0-consortium` or similar). Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank. | YES      | YES                      |
    | `BPC_RENAL_RELEASE`       | Release identifier for the latest RENAL BPC cohort release used for tracking. Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank.                                          | YES      | YES                      |
    | `BPC_BLADDER_RELEASE`     | Release identifier for the latest BLADDER BPC cohort release used for tracking. Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank.                                        | YES      | YES                      |
    | `BPC_BRCA_RELEASE`        | Release identifier for the latest BRCA BPC cohort release used for tracking. Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank.                                           | YES      | YES                      |
    | `BPC_NSCLC_RELEASE`       | Release identifier for the latest NSCLC BPC cohort release used for tracking. Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank.                                          | YES      | YES                      |
    | `BPC_PROSTATE_RELEASE`    | Release identifier for the latest PROSTATE BPC cohort release used for tracking. Populated for pairs present in that cohort’s latest slice; otherwise may be null/blank.                                       | YES      | YES                      |

    **Note**: Fields ending in _RELEASE (excluding IN_* flags) may be null/blank when the sample–patient pair is not present in the corresponding cohort’s latest release.

    ##Getting Started


    ### Query templates

    #### Scenario 1
    You want to query which sample-patient pairs are in the latest main genie consortium release for a specific sponsored project (SP):
    ```sql
    SELECT
    SAMPLE_ID,
    PATIENT_ID,
    FROM <TABLE_SYNAPSE_ID>
    WHERE RELEASE_PROJECT_TYPE = <SPONSORED_PROJECT_NAME>
    AND IN_LATEST_MAIN_GENIE = TRUE;
    ```

    **Example**

    ```sql
    SELECT
    SAMPLE_ID,
    PATIENT_ID,
    FROM syn71708167
    WHERE RELEASE_PROJECT_TYPE = 'SP_KRAS'
    AND IN_LATEST_MAIN_GENIE = TRUE;
    ```

    *Sample Result*
    | SAMPLE_ID     | PATIENT_ID    |
    | ------------- | ------------- |
    | P-0001234-T01 | GENIE-0005678 |
    | P-0009876-T01 | GENIE-0009999 |


    #### Scenario 2
    You want to filter on which sample-patient pairs were not present in a specific project(s) but present in the latest main genie release
    ```sql
    SELECT SAMPLE_ID, PATIENT_ID
    FROM syn72246564
    WHERE IN_LATEST_MAIN_GENIE = TRUE
    AND <PROJECT_A_FLAG> = FALSE
    AND <PROJECT_B_FLAG> = FALSE;
    ```
    **Example**
    Here we filter on sample-patient ids that are not present in BPC's breast cancer cohort's latest release and not present in the AKT1 sponsored project
    ```sql
    SELECT SAMPLE_ID, PATIENT_ID
    FROM syn72246564
    WHERE IN_LATEST_MAIN_GENIE = TRUE
    AND IN_BPC_BRCA_RELEASE = FALSE
    AND IN_AKT1_PROJECT = FALSE;
    ```

    *Sample Result*
    | SAMPLE_ID     | PATIENT_ID    |
    | ------------- | ------------- |
    | P-0011111-T01 | GENIE-0002222 |
    | P-0033333-T02 | GENIE-0004444 |

    """

    wiki = Wiki(title='Patient and Sample Tracking Table',
                owner=table,
                markdown=content)
    print(f"Created wiki for table: {table.name} ({table.id})")
    syn.store(wiki)


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
    table = create_table(project_synid=args.project_synid, table_name=args.table_name)
    add_table_wiki(syn, table)


if __name__ == "__main__":
    main()
