
params.release_folder_synid = 'syn62069187'

process generate_tmb {
    // container 'sagebionetworks/genie-tmb'
    container 'test'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous
    // val release
    val release_folder_synid
    val production

    output:
    stdout

    script:
    """
    /tmb/generate_tmb.sh $release_folder_synid
    """
}

workflow {
    generate_tmb('test', params.release_folder_synid, 'test')
}