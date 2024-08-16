// Patch release
process patch_release {
    container "$params.patch_release_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release_synid
    val new_release_synid
    val retracted_sample_synid

    output:
    stdout

    script:
    """
    python3 /patch_release/patch.py \
        --release_synid $release_synid \
        --new_release_synid $new_release_synid \
        --retracted-sample_synid $retracted_sample_synid
    """
}
