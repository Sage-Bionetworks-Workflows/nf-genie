process create_public_release {
    debug true
    container 'sagebionetworks/genie:develop'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release
    val seq
    val production

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
