process reset_processing {
    debug true
    container "$params.main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val center_map_synid

    output:
    stdout

    script:
    """
    synapse set-annotations --id $center_map_synid --annotations '{"isProcessing": "False"}'
    """
}
