"""
This script syncs specific tables from the production database to the staging database in Synapse.

Usage: python sync_staging_table_with_prod.py
"""

from datetime import date

import synapseclient
from genie import load, process_functions
from synapseclient.models import query, Table, SchemaStorageStrategy
import pandas as pd

syn = synapseclient.login()
syn.table_query_timeout = 50000

tables_to_copy = [
    # "vcf2maf",
    "bed",
    "seg",
    "sample",
    "patient",
    "mutationsInCis",
    "sampleRetraction",
    "patientRetraction",
    "sv",
    "assayinfo",
    "validationStatus",
    "errorTracker",
]

db_to_synid_mapping = {"production": "syn10967259", "staging": "syn12094210"}

def download_table(table_key: str) -> pd.DataFrame:
    """
    Downloads the production table from Synapse.
    Args:
        table_key: The table name key of the table to download.
    Returns:
        data: A pandas DataFrame containing the data from the production table.
    """
    # download production tables
    db_table = syn.query(
        f"SELECT * FROM {db_to_synid_mapping['production']}"
    ).convert_dtypes()
    syn_id = db_table[db_table["Database"] == table_key].Id.values[0]
    data = query(f"SELECT * FROM {syn_id}").convert_dtypes()
    return data


def replace_table(data_to_replace_with: pd.DataFrame, table_key: str) -> None:
    """
    Replaces the staging table with the production table.
    Args:
        data_to_replace_with: The data to replace the staging table with.
        table_key: The key of the table to replace.
    Returns:
        None
    """
    table_to_replace = query(
        f"SELECT * FROM {db_to_synid_mapping['staging']}"
    ).convert_dtypes()
    table_to_replace_syn_id = table_to_replace[
        table_to_replace["Database"] == table_key
    ].Id.values[0]
    data_to_replace = query(
        f"SELECT * FROM {table_to_replace_syn_id}"
    ).convert_dtypes()

    # create new table for maf tables
    if table_key == "vcf2maf":
        today = date.today()
        table_name = f"Narrow MAF Database - {today}"
        new_tables = process_functions.create_new_fileformat_table(
            syn,
            file_format="vcf2maf",
            newdb_name=table_name,
            projectid="syn22033066",
            archive_projectid="syn22033066",
        )
        syn.setPermissions(new_tables["newdb_ent"].id, 3326313, [])
        table_to_replace_syn_id = new_tables["newdb_ent"].id
        Table(id=table_to_replace_syn_id).store_rows(data_to_replace_with)
    else:
        databaseEnt = syn.get(table_to_replace_syn_id)
        primary_key = (
            databaseEnt.primaryKey
            if table_key not in ["validationStatus", "errorTracker"]
            else ["id"]
        )
        load._update_table(
            syn,
            database=data_to_replace,
            new_dataset=data_to_replace_with,
            database_synid=table_to_replace_syn_id,
            primary_key_cols=primary_key,
            to_delete=True,
        )


for table in tables_to_copy:
    print(table)
    data_replace = download_table(table_key=table)
    replace_table(data_to_replace_with=data_replace, table_key=table)
    print(f"Successfully synced {table} from production to staging")
