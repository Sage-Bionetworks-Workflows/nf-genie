process validate_data {
    debug true
    container "$params.main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val proj_id
    val center
    val main_pipeline_docker

    output:
    stdout

    script:
    if (center == "ALL") {
        """
        python3 /root/Genie/bin/input_to_database.py \
        mutation \
        --project_id $proj_id \
        --onlyValidate \
        --genie_annotation_pkg \
        /root/annotation-tools
        """
    } else {
        """
        python3 /root/Genie/bin/input_to_database.py \
        mutation \
        --project_id $proj_id \
        --center $center \
        --onlyValidate \
        --genie_annotation_pkg \
        /root/annotation-tools
        """
    }
}
