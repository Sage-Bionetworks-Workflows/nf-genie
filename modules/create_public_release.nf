process create_public_release {
    debug true
    container "$params.main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release
    val seq
    val production
    val staging

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
    } else if (staging) {
        """
        # Fixes renv issue
        cd /root/Genie
        python3 bin/consortium_to_public.py \
        $seq \
        /root/cbioportal \
        $release \
        --staging
        """
    } else {
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
