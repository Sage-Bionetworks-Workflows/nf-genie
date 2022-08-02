#!/usr/bin/env nextflow

//nextflow.enable.dsl=2

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
process main_process {

  secret 'SYNAPSE_AUTH_TOKEN'

  output:
  stdout ch

  script:
  """
  process.py \
  main \
  --project_id syn7208886 \
  --onlyValidate
  """
}


// Public release
process public_release {

  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val fake from ch

  script:
  """
  public_release.py \
  Jan-2017 \
  /root/cbioportal \
  test \
  --test
  """
}

// Create release dashboard
process public_release {

  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val fake from ch

  script:
  """
  public_release.py \
  Jan-2017 \
  /root/cbioportal \
  test \
  --test
  """
}

// Create data guide


// Create skeleton release notes


// run artifact finder

// copy to BPC

// copy consortium to BPC

// check for any retractions in BPC


// TMB code