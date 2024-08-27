// Compares two GENIE releases given two synapse ids
process compare_releases {
    container "$params.patch_release_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    val release_synid
    val new_release_synid

    output:
    stdout

    script:
    """
    python3 /patch_release/compare_patch.py \
        --original_synid $release_synid \
        --new_synid $new_release_synid
    """
}
