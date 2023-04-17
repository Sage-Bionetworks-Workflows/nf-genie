process check_for_retractions {
    container 'sagebionetworks/main-genie-release-utils'
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