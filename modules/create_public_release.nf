process create_public_release {
    debug true
    container "$main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release
    val seq
    val production
    val main_pipeline_docker

    output:
    stdout

    script:
    if (production) {
        """
        # Fixes renv issue
        cd /root/Genie
        python3 bin/consortium_to_public.py \
        $seq \
        /root/cbioportal \
        $release
        """
    }
    else {
        """
        # Fixes renv issue
        cd /root/Genie
        python3 bin/consortium_to_public.py \
        $seq \
        /root/cbioportal \
        $release \
        --test
        """
    }
}
