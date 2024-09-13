// Patch release
process patch_release {
    container "$params.patch_release_docker"
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release_synid
    val new_release_synid
    val retracted_sample_synid
    val production

    output:
    stdout

    script:
    if (production) {
        """
        python3 /patch_release/patch.py \
            $release_synid \
            $new_release_synid \
            $retracted_sample_synid \
            --production
        """
    }
    else {
        """
        python3 /patch_release/patch.py \
            $release_synid \
            $new_release_synid \
            $retracted_sample_synid \
        """
    }
}
