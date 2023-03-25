process load_to_bpc {
    container 'sagebionetworks/main-genie-release-utils'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release

    output:
    stdout

    script:
    """
    python3 /release_utils/consortium_to_bpc.py $release
    """
}