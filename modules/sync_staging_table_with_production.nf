// Create data guide
process sync_staging_table_with_production {
    debug true
    container "$params.sync_table_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val is_staging

    output:
    stdout

    script:
    """
    python3 /sync_tables/sync_staging_table_with_production.py
    """

}
