process process_maf {
    debug true
    container "$main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val proj_id
    val center
    val create_new_maf_db
    val main_pipeline_docker

    output:
    stdout

    script:
    // TODO Abstract out create new maf fb function
    if (create_new_maf_db) {
        if (center == "ALL") {
            """
            python3 /root/Genie/bin/input_to_database.py \
            mutation \
            --project_id $proj_id \
            --genie_annotation_pkg \
            /root/annotation-tools \
            --createNewMafDatabase
            """
        } else {
            """
            python3 /root/Genie/bin/input_to_database.py \
            mutation \
            --project_id $proj_id \
            --genie_annotation_pkg \
            /root/annotation-tools \
            --createNewMafDatabase \
            --center $center
            """
        }
    }
    else {
        if (center == "ALL") {
            """
            python3 /root/Genie/bin/input_to_database.py \
            mutation \
            --project_id $proj_id \
            --genie_annotation_pkg \
            /root/annotation-tools
            """
        } else {
            """
            python3 /root/Genie/bin/input_to_database.py \
            mutation \
            --project_id $proj_id \
            --genie_annotation_pkg \
            /root/annotation-tools \
            --center $center
            """
        }
    }
}