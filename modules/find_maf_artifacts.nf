// Find MAF artifacts
// https://github.com/Sage-Bionetworks/GENIE-ArtifactFinder
// TODO: Need to add staging ability for artifact finder
process find_maf_artifacts {
    container "$find_maf_artifacts_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release
    val find_maf_artifacts_docker

    output:
    stdout

    script:
    """
    python /artifact/artifact_finder.py $release
    """
}