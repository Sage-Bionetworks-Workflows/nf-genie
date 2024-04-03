
// Add consortium or public release flag
process create_consortium_release {
    debug true
    container "$main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val production
    val seq
    val main_pipeline_docker

    output:
    stdout

    script:
    if (production) {
        """
        # Fixes renv issue
        cd /root/Genie
        python3 bin/database_to_staging.py \
        $seq \
        /root/cbioportal \
        $release
        """
    }
    else {
        """
        # Fixes renv issue
        cd /root/Genie
        python3 bin/database_to_staging.py \
        $seq \
        /root/cbioportal \
        $release \
        --test
        """
    }
}