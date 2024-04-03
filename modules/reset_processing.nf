process reset_processing {
    debug true
    container "$main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val center_map_synid
    val main_pipeline_docker

    output:
    stdout

    script:
    """
    synapse set-annotations --id $center_map_synid --annotations '{"isProcessing": "False"}'
    """
}
