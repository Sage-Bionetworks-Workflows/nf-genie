process load_to_bpc {
    container "$params.main_release_utils_docker"
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
