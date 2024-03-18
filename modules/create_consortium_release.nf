
// Add consortium or public release flag
process create_consortium_release {
    debug true
    container 'rxu153/update_texlive_genie:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val production
    val seq

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