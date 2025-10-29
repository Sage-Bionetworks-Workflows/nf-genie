#!/usr/bin/env nextflow
// Ensure DSL2
nextflow.enable.dsl = 2

// IMPORT MODULES
include { check_for_retractions } from './modules/check_for_retractions'
include { create_consortium_release } from './modules/create_consortium_release'
include { create_data_guide } from './modules/create_data_guide'
include { create_public_release } from './modules/create_public_release'
include { find_maf_artifacts } from './modules/find_maf_artifacts'
// include { generate_tmb } from './modules/generate_tmb'
include { load_to_bpc } from './modules/load_to_bpc'
include { reset_processing } from './modules/reset_processing'
include { validate_data } from './modules/validate_data'
include { process_main } from './modules/process_main'
include { process_maf } from './modules/process_maf'
include { process_maf as process_maf_remaining_centers} from './modules/process_maf'
include {sync_staging_table_with_production} from './modules/sync_staging_table_with_production'

// SET PARAMETERS

// TODO: centers to process / exclude
// force start the pipeline, by resetting the center
// mapping annotation
// params.force = false
// Different process types (only_validate, main_process, maf_process, consortium_release, public_release)
params.process_type = "only_validate"
// Specify center
params.center = "ALL"
// to create new maf database
params.create_new_maf_db = false
// release name (pass in TEST.public to test the public release scripts)
params.release = "TEST.consortium"
// List all centers to be processed for maf_process
params.maf_centers = "ALL"
// List of centers to be processed converted from params.maf_centers
maf_center_list = params.maf_centers?.split(",").toList()
// whether to sync staging table with prod table at the start of the run
params.sync_staging_table_with_production = false
// Validate input parameters
WorkflowMain.initialise(workflow, params, log)

/*
release, seq
11-consortium, Jul-2021
12-consortium, Jan-2022
13-consortium, Jul-2022

11-public, Jan-2022
12-public, Jul-2022
13-public, Jan-2023
*/
def public_map = [
  "TEST": "Jan-2022",
  "STAGING": "Jul-2025",
  "11": "Jan-2022",
  "12": "Jul-2022",
  "13": "Jan-2023",
  "14": "Jul-2023",
  "15": "Jan-2024",
  "16": "Jul-2024",
  "17": "Jan-2025",
  "18": "Jul-2025",
  "19": "Jan-2026",
  "20": "Jul-2026"
]
def consortium_map = [
  "TEST": "Jul-2022",
  "STAGING": "Jan-2025",
  "11": "Jul-2021",
  "12": "Jan-2022",
  "13": "Jul-2022",
  "14": "Jan-2023",
  "15": "Jul-2023",
  "16": "Jan-2024",
  "17": "Jul-2024",
  "18": "Jan-2025",
  "19": "Jul-2025",
  "20": "Jan-2026"
]
release_split = params.release.tokenize('.')
major_release = release_split[0]

if (params.release.contains("public")) {
  seq_date = public_map[major_release]
}
else {
  seq_date = consortium_map[major_release]
}
if (!seq_date) {
  throw new Exception("${major_release} release not supported in map variables in nf code.")
}

// define whether to run TEST, STAGING or PRODUCTION
if (major_release == "TEST") {
  project_id = "syn7208886"
  center_map_synid = "syn11601248"
  is_prod = false
  is_staging = false
  
} else if (major_release == "STAGING"){
  project_id = "syn22033066"
  center_map_synid = "syn22089188"
  is_prod = false
  is_staging = true
}
else {
  // production project
  project_id = "syn3380222"
  center_map_synid = "syn10061452"
  is_prod = true
  is_staging = false
}

// Extract center list for MAF processing
if (major_release == "TEST"){
  all_centers = ["SAGE", "TEST", "GOLD"]
} else {
  all_centers = ["JHU","DFCI","GRCC","NKI","MSK","UHN","VICC","MDA","WAKE","YALE","UCSF","CRUK","CHOP","VHIO","SCI","PROV","COLU","UCHI","DUKE","UMIAMI"]
}
if (params.maf_centers == "ALL") {
  maf_center_list = all_centers
}

def process_maf_helper(ch_sync_done, maf_centers, ch_project_id, maf_center_list, create_new_maf_db) {
    /**
  * Processes MAF files for a given center list.
  *
  * @param ch_sync_done         Channel indicating sync table completion
  * @param maf_centers          Parameter containing the centers to be processed, can be "ALL" or a comma-separated list
  * @param ch_project_id        Channel with project ID
  * @param maf_center_list      List of centers to be processed converted from params.maf_centers
  * @param create_new_maf_db    Boolean flag to create new DB
  * @return                     A collect output of the MAF process
  */

  // Create a channel from the list of centers
  ch_maf_centers = Channel.fromList(maf_center_list)
  // placeholder for previous output
  previous = "default"
  // If maf_centers is "ALL", we will process all centers in the maf_center_list
  if (maf_centers == "ALL") {
    // Create a channel to indicate whether it's the first center or not
    ch_maf_centers = ch_maf_centers.branch { v ->
        first: v == maf_center_list[0]
        remaining: v != maf_center_list[0]
    }
    // Process the first center with createNewMafDb as true
    process_maf_first_center = process_maf(previous, ch_project_id, ch_maf_centers.first, true).collect()
    // Process the rest with createNewMafDb as false
    return process_maf_remaining_centers(process_maf_first_center, ch_project_id, ch_maf_centers.remaining, false).collect()

  } else {
    // Process centers as the specified maf center list
    return process_maf(previous, ch_project_id, ch_maf_centers, create_new_maf_db).collect()
  }
}

workflow  {
  ch_release = Channel.value(params.release)
  ch_project_id = Channel.value(project_id)
  ch_seq_date = Channel.value(seq_date)
  ch_center = Channel.value(params.center)
  ch_is_prod = Channel.value(is_prod)
  ch_is_staging = Channel.value(is_staging)

  if (params.sync_staging_table_with_production == true && is_staging) {
    sync_done = sync_staging_table_with_production()
    ch_sync_done =  sync_done.out.ifEmpty { Channel.value("skip_sync_table") }
  // if (params.force) {
  //   reset_processing(center_map_synid)]
  //   reset_processing.out.view()
  // }
  if (params.process_type == "only_validate") {
    validate_data(ch_project_id, ch_center)
    // validate_data.out.view()
  } else if (params.process_type == "maf_process") {
    // Call the function
    process_maf_helper(ch_sync_done.out, params.maf_centers, ch_project_id, maf_center_list, params.create_new_maf_db)
    // process_maf.out.view()
  } else if (params.process_type == "main_process") {
    process_main("default", ch_project_id, ch_center)
  } else if (params.process_type == "consortium_release") {
    process_maf_col = process_maf_helper(ch_sync_done.out, params.maf_centers, ch_project_id, maf_center_list, params.create_new_maf_db)
    process_main(process_maf_col, ch_project_id, ch_center)
    create_consortium_release(process_main.out, ch_release, ch_is_prod, ch_seq_date, ch_is_staging)
    create_data_guide(create_consortium_release.out, ch_release, ch_project_id)
    if (!is_staging) {
      load_to_bpc(create_data_guide.out, ch_release, ch_is_prod)
    }
    if (is_prod) {
      find_maf_artifacts(create_consortium_release.out, ch_release)
      check_for_retractions(create_consortium_release.out)
    }
  } else if (params.process_type == "consortium_release_step_only") {
    create_consortium_release("default", ch_release, ch_is_prod, ch_seq_date, ch_is_staging)
    create_data_guide(create_consortium_release.out, ch_release, ch_project_id)
    if (!is_staging) {
      load_to_bpc(create_data_guide.out, ch_release, ch_is_prod)
    }
    if (is_prod) {
      find_maf_artifacts(create_consortium_release.out, ch_release)
      check_for_retractions(create_consortium_release.out)
    }
  } else if (params.process_type == "public_release_step_only") {
    create_public_release(ch_release, ch_seq_date, ch_is_prod, ch_is_staging)
  } else if (params.process_type == "data_guide_only") {
    create_data_guide("default", ch_release, ch_project_id)
  } else if (params.process_type == "public_release") {
    create_public_release(ch_release, ch_seq_date, ch_is_prod, ch_is_staging)
    create_data_guide(create_public_release.out, ch_release, ch_project_id)
  } else {
    throw new Exception("process_type can only be 'only_validate', 'maf_process', 'main_process', 'consortium_release', 'public_release', 'consortium_release_step_only', data_guide_only', 'public_release_step_only'")
  }
}
