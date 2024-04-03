process check_for_retractions {
    container "$main_release_utils_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val main_release_utils_docker

    output:
    stdout

    script:
    """
    python3 /release_utils/check_bpc_retraction.py
    """
}