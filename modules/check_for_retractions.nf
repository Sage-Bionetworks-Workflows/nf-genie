process check_for_retractions {
    container "$params.main_release_utils_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous

    output:
    stdout

    script:
    """
    python3 /release_utils/check_bpc_retraction.py
    """
}
