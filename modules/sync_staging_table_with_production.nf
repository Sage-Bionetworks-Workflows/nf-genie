// Create data guide
process sync_staging_table_with_production {
    debug true
    container "$params.main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous

    output:
    stdout

    script:
    """
    python sync_staging_table_with_production.py
    """

    stub:
    """
    echo "sync_staging_table_with_production"
    """


}
