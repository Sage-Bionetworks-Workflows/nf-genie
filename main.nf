#!/usr/bin/env nextflow

//nextflow.enable.dsl=2

//parameters
// genie project id
// release name
// to create new maf database
// centers to process / exclude
// consortium or public release

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

process maf_process {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val previous from validation_out

  output:
  stdout into maf_process_out

  script:
  """
  python3 /root/Genie/bin/input_to_database.py \
  mutation \
  --project_id syn7208886 \
  --genie_annotation_pkg \
  /root/annotation-tools \
  --createNewMafDatabase
  """
}
maf_process_out.view()

process main_process {
  container 'sagebionetworks/genie:latest'
  secret 'SYNAPSE_AUTH_TOKEN'

  input:
  val previous from maf_process_out

  output:
  stdout into main_process_out

  script:
  """
  python3 /root/Genie/bin/input_to_database.py \
  main \
  --project_id syn7208886
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
  """
  python3 /root/Genie/bin/database_to_staging.py \
  Jul-2022 \
  /root/cbioportal \
  13.1-consortium \
  --test
  """
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

// copy to BPC

// copy consortium to BPC

// check for any retractions in BPC


// TMB code