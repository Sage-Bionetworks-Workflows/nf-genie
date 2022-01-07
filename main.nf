#!/usr/bin/env nextflow


/*
========================================================================================
    SETUP PARAMS
========================================================================================
*/

params.synapse_config = false  // Default
ch_synapse_config = params.synapse_config ? Channel.value(file(params.synapse_config)) : "null"

/*
========================================================================================
    SETUP PROCESSES
========================================================================================
*/


// Main processing for GENIE
process genie_main_process {

  secret 'SYNAPSE_AUTH_TOKEN'

  script:
  """
  process.py \
  main \
  --project_id syn7208886 \
  --onlyValidate
  """
}
