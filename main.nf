#!/usr/bin/env nextflow

//nextflow.enable.dsl=2

//parameters
// genie project id
// release name
// to create new maf database
// centers to process / exclude
// consortium or public release
params.production = false
params.release = "TESTrelease"
params.create_new_maf_db = false

if (params.production) {
  project_id = "syn3380222"
}
else {
  project_id = "syn7208886"
}
/*
========================================================================================
    SETUP PROCESSES
========================================================================================
*/

// Main processing for GENIE
// process validation {
//   container 'sagebionetworks/genie:latest'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   output:
//   stdout into validation_out

//   script:
//   """
//   python3 /root/Genie/bin/input_to_database.py \
//   mutation \
//   --project_id syn7208886 \
//   --onlyValidate \
//   --genie_annotation_pkg \
//   /root/annotation-tools
//   """
// }
// validation_out.view()

// Split off creation of maf database
// (This will simplify the genie pipeline)
process maf_process {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val proj_id from project_id

  output:
  stdout into maf_process_out

  script:
  if (params.create_new_maf_db) {
    """
    python3 /root/Genie/bin/input_to_database.py \
    mutation \
    --project_id $proj_id \
    --genie_annotation_pkg \
    /root/annotation-tools \
    --createNewMafDatabase
    """
  }
  else {
    """
    python3 /root/Genie/bin/input_to_database.py \
    mutation \
    --project_id $proj_id \
    --genie_annotation_pkg \
    /root/annotation-tools
    """
  }

}
maf_process_out.view()

process main_process {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val proj_id from project_id
  val previous from maf_process_out

  output:
  stdout into main_process_out

  script:
  """
  python3 /root/Genie/bin/input_to_database.py \
  main \
  --project_id $proj_id
  """
}
main_process_out.view()

// Add consortium or public release flag
process release {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val previous from main_process_out

  output:
  stdout into release_out

  script:
  if (params.production) {
    """
    python3 /root/Genie/bin/database_to_staging.py \
    Jul-2022 \
    /root/cbioportal \
    13.1-consortium \
    --test
    """
  }
  else {
    """
    python3 /root/Genie/bin/database_to_staging.py \
    Jul-2022 \
    /root/cbioportal \
    13.1-consortium \
    --test
    """
  }
}
release_out.view()

// process public_release {
//   container 'sagebionetworks/genie:latest'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val previous from main_process_out

//   output:
//   stdout into public_release_out

//   script:
//   """
//   python3 /root/Genie/bin/consortium_to_public.py \
//   Jul-2022 \
//   /root/cbioportal \
//   13.1-consortium \
//   --test
//   """
// }
// public_release_out.view()

// Create release dashboard
// process dashboard {

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
// https://github.com/Sage-Bionetworks/GENIE-ArtifactFinder
// TODO: Need to add staging ability for artifact finder
// process artifact_finder {
//   container 'sagebionetworks/genie-artifact-finder'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val previous from release_out

//   output:
//   stdout into artifact_finder_out

//   script:
//   """
//   python /artifact/artifact_finder.py \
//   13.1-consortium
//   """
// }
// artifact_finder_out.view()

// copy consortium to BPC
// process consortium_to_bpc {
//   container 'sagebionetworks/synapsepythonclient:v2.6.0'
//   secret 'SYNAPSE_AUTH_TOKEN'

//   input:
//   val previous from release_out

//   output:
//   stdout into consortium_to_bpc_out

//   script:
//   """
//   python3 $PWD/bin/consortium_to_bpc.py 13.1-consortium
//   """
// }
// consortium_to_bpc_out.view()

// check for any retractions in BPC
process check_retraction {
  container 'sagebionetworks/synapsepythonclient:v2.6.0'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val previous from release_out

  output:
  stdout into check_retraction_out

  script:
  """
  python3 $PWD/bin/check_bpc_retraction.py
  """
}
check_retraction_out.view()


// TMB code