process process_main {
    debug true
    container 'rxu153/update_texlive_genie:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val proj_id
    val center

    output:
    stdout

    script:
    if (center == "ALL") {
        """
        python3 /root/Genie/bin/input_to_database.py \
        main \
        --project_id $proj_id
        """
    } else {
        """
        python3 /root/Genie/bin/input_to_database.py \
        main \
        --project_id $proj_id \
        --center $center
        """
    }
}
