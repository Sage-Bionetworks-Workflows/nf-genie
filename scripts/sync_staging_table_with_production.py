"""
This script syncs specific tables from the production database to the staging database in Synapse.

Usage: python sync_staging_table_with_prod.py
"""

from datetime import date

import synapseclient
from genie import load, process_functions
from synapseclient.models import Table, SchemaStorageStrategy

syn = synapseclient.login()
syn.table_query_timeout = 50000

tables_to_copy = [
    #"vcf2maf",
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
    "errorTracker"
]

db_to_synid_mapping = {
    "production":"syn10967259",
    "staging":"syn12094210"
}

def download_table(table_key):
    # download production tables
    db_table = syn.tableQuery(f"SELECT * FROM {db_to_synid_mapping['production']}").asDataFrame()
    syn_id = db_table[db_table["Database"] == table_key].Id.values[0]
    data = syn.tableQuery(f"SELECT * FROM {syn_id}").asDataFrame()
    return(data)
    

def replace_table(data_to_replace_with, table_key):
    # replace staging tables with production tables
    table_to_replace = syn.tableQuery(f"SELECT * FROM {db_to_synid_mapping['staging']}").asDataFrame()
    table_to_replace_syn_id = table_to_replace[table_to_replace["Database"] == table_key].Id.values[0]
    data_to_replace = syn.tableQuery(f"SELECT * FROM {table_to_replace_syn_id}").asDataFrame()
    
    # create new table for maf tables
    if table_key == "vcf2maf":
        today = date.today()
        table_name = f"Narrow MAF Database - {today}"
        new_tables = process_functions.create_new_fileformat_table(
            syn, 
            file_format="vcf2maf", 
            newdb_name=table_name, 
            projectid="syn22033066",  
            archive_projectid="syn22033066"
        )
        syn.setPermissions(new_tables["newdb_ent"].id, 3326313, [])
        table_to_replace_syn_id = new_tables["newdb_ent"].id
        syn.store(synapseclient.Table(table_to_replace_syn_id, data_to_replace_with))
    else:
        databaseEnt = syn.get(table_to_replace_syn_id)
        primary_key = databaseEnt.primaryKey if table_key not in ["validationStatus", "errorTracker"] else ["id"]


        load._update_table(
            syn,
            database = data_to_replace,
            new_dataset = data_to_replace_with,
            database_synid=table_to_replace_syn_id,
            primary_key_cols = primary_key,
            to_delete=True,
        )
    
        changes = load.check_database_changes(data_to_replace, data_to_replace_with, primary_key, to_delete = True)
        # store the changed and new rows
        col_order = changes["col_order"]
        if not changes["allupdates"].empty:
            import pdb; pdb.set_trace()
            Table(id = table_to_replace_syn_id).store_rows(
                values = changes["allupdates"][col_order], to_csv_kwargs= {"float_format": "%.12g"}, schema_storage_strategy=SchemaStorageStrategy.INFER_FROM_DATA)
        if not changes["to_delete_rows"].empty:
            print(f"Deleting {len(changes['to_delete_rows'])} rows from {table_key} table")


for table in tables_to_copy:
    print(table)
    data_replace = download_table(table_key = table)
    replace_table(data_to_replace_with = data_replace, table_key = table)
