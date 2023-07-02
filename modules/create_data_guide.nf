
  // Create data guide
process create_data_guide {
    debug true
    container 'sagebionetworks/genie-data-guide:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val proj_id

    output:
    stdout
    // path "data_guide.pdf"

    script:
    """
    cd /data_guide
    # This is the quarto cli
    # quarto render data_guide.qmd -P release:$release -P project_id:$proj_id --to pdf
    Rscript generate_data_guide_cli.R $release $proj_id
    """
}
