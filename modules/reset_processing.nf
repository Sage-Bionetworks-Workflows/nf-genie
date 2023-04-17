process reset_processing {
    debug true
    container 'sagebionetworks/genie:latest'
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
