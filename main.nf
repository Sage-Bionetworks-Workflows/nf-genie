#!/usr/bin/env nextflow

//nextflow.enable.dsl=2

//parameters
// centers to process / exclude
// testing or production pipeline
params.production = false
// only run validation pipeline
params.only_validate = false
// consortium or public release
// pass in TESTpublic to test the public release scripts
// release name
params.release = "TESTconsortium"
// to create new maf database
params.create_new_maf_db = false

// Determine which synapse id to pass into processing
if (params.production) {
  project_id = "syn3380222"
}
else {
  project_id = "syn7208886"
}
/*
release, seq
11-consortium, Jul-2021
12-consortium, Jan-2022
13-consortium, Jul-2022

11-public, Jan-2022
12-public, Jul-2022
13-public, Jan-2023
*/

/*
========================================================================================
    SETUP PROCESSES
========================================================================================
*/
if (params.only_validate) {

  // Main processing for GENIE
  process validation {
    container 'sagebionetworks/genie:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    when:
    params.only_validate

    output:
    stdout into validation_out

    script:
    """
    python3 /root/Genie/bin/input_to_database.py \
    mutation \
    --project_id $project_id \
    --onlyValidate \
    --genie_annotation_pkg \
    /root/annotation-tools
    """
  }
  validation_out.view()
}
else if (params.release.contains("public")) {
  // Only run consortium to public when not validate only and public
  process public_release {
    echo true
    container 'sagebionetworks/genie:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val release from params.release

    output:
    stdout into public_release_out

    script:
    if (params.production) {
      """
      python3 /root/Genie/bin/consortium_to_public.py \
      Jul-2022 \
      /root/cbioportal \
      $release
      """
    }
    else {
      """
      python3 /root/Genie/bin/consortium_to_public.py \
      Jul-2022 \
      /root/cbioportal \
      $release \
      --test
      """
    }
  }
  public_release_out.view()

} else {
  // Only run processing pipline if not only validate and not public release
  // Split off creation of maf database
  // (This will simplify the genie pipeline)
  process maf_process {
    echo true
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
    echo true
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
  process consortium_release {
    echo true
    container 'sagebionetworks/genie:latest'
    secret 'SYNAPSE_AUTH_TOKEN'

    input:
    val previous from main_process_out
    val release from params.release

    output:
    stdout into consortium_release_out

    script:
    if (params.production) {
      """
      python3 /root/Genie/bin/database_to_staging.py \
      Jan-2023 \
      /root/cbioportal \
      $release
      """
    }
    else {
      """
      python3 /root/Genie/bin/database_to_staging.py \
      Jan-2023 \
      /root/cbioportal \
      $release \
      --test
      """
    }
  }
  consortium_release_out.view()

  // Create release dashboard

  // Create data guide

  // Create skeleton release notes

  // run artifact finder
  // https://github.com/Sage-Bionetworks/GENIE-ArtifactFinder
  // TODO: Need to add staging ability for artifact finder
  process artifact_finder {
    container 'sagebionetworks/genie-artifact-finder'
    secret 'SYNAPSE_AUTH_TOKEN'

    when:
    params.production

    input:
    val previous from consortium_release_out
    val release from params.release

    output:
    stdout into artifact_finder_out

    script:
    """
    python /artifact/artifact_finder.py $release
    """
  }
  artifact_finder_out.view()

  // copy consortium to BPC
  process consortium_to_bpc {
    container 'sagebionetworks/synapsepythonclient:v2.6.0'
    secret 'SYNAPSE_AUTH_TOKEN'

    when:
    params.production

    input:
    val previous from release_out
    val release from params.release

    output:
    stdout into consortium_to_bpc_out

    script:
    """
    python3 $PWD/bin/consortium_to_bpc.py $release
    """
  }
  consortium_to_bpc_out.view()

  // check for any retractions in BPC
  process check_retraction {
    container 'sagebionetworks/synapsepythonclient:v2.6.0'
    secret 'SYNAPSE_AUTH_TOKEN'

    when:
    params.production

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
}
