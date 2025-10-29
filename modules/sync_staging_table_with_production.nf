// Create data guide
process sync_staging_table_with_production {
    debug true
    container "$params.sync_table_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val is_staging
    val sync_staging_table_with_production

    output:
    stdout

    script:
    if (is_staging && sync_staging_table_with_production) {
        """ 
        python3 /sync_tables/sync_staging_table_with_production.py

        echo "Sync staging table with production complete"
        """
    }
    else {
        """
        echo "Skipping sync staging table with production"
        """
    }
}
