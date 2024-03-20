process load_to_bpc {
    container 'sagebionetworks/main-genie-release-utils'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val production

    output:
    stdout

    script:
    if (production) {
        """
        python3 /release_utils/consortium_to_bpc.py $release
        """
    }
    else {
        """
        python3 /release_utils/consortium_to_bpc.py $release --test
        """
    }
}