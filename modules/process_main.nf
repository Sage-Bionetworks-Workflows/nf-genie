process process_main {
    debug true
    container "$main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val proj_id
    val center
    val main_pipeline_docker

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
