// Create data guide
process create_dashboard_html {
    debug true
    container "$params.main_pipeline_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val production

    output:
    stdout
    // path "data_guide.pdf"

    script:
    if (production) {
        """
        Rscript ./R/dashboard_markdown_generator.R" $release \
            --template_path ./templates/dashboardTemplate.Rmd
        """
    } else {
        """
        Rscript ./R/dashboard_markdown_generator.R" $release \
            --template_path ./templates/dashboardTemplate.Rmd \
            --staging
        """
    }
}
