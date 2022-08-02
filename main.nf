#!/usr/bin/env nextflow

//nextflow.enable.dsl=2

/*
========================================================================================
    SETUP PROCESSES
========================================================================================
*/

// Main processing for GENIE
process validation {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  output:
  stdout into validation_out

  script:
  """
  python3 /root/Genie/bin/input_to_database.py \
  mutation \
  --project_id syn7208886 \
  --onlyValidate \
  --genie_annotation_pkg \
  /root/annotation-tools
  """
}
validation_out.view()

// process maf_process {
//   container 'sagebionetworks/genie:latest'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val previous from validation_out

//   output:
//   stdout into maf_process_out

//   script:
//   """
//   python3 /root/Genie/bin/input_to_database.py \
//   mutation \
//   --project_id syn7208886 \
//   --genie_annotation_pkg \
//   /root/annotation-tools \
//   --createNewMafDatabase
//   """
// }

// process main_process {
//   container 'sagebionetworks/genie:latest'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   output:
//   stdout ch

//   script:
//   """
//   python3 /root/Genie/bin/input_to_database.py \
//   main \
//   --project_id syn7208886
//   """
// }

// // Public release
// process public_release {

//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val fake from ch

//   script:
//   """
//   public_release.py \
//   Jan-2017 \
//   /root/cbioportal \
//   test \
//   --test
//   """
// }

// Create release dashboard
// process public_release {

//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val fake from ch

//   script:
//   """
//   public_release.py \
//   Jan-2017 \
//   /root/cbioportal \
//   test \
//   --test
//   """
// }

// Create data guide


// Create skeleton release notes


// run artifact finder

// copy to BPC

// copy consortium to BPC

// check for any retractions in BPC


// TMB code