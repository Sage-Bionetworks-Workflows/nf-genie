#!/usr/bin/env nextflow
// Ensure DSL2
nextflow.enable.dsl = 2

// IMPORT MODULES
include { patch_release } from './modules/patch_release'
include { create_data_guide } from './modules/create_data_guide'
include { create_dashboard_html } from './modules/create_dashboard_html'
include { compare_releases } from './modules/compare_releases'

params.release_synid = "syn53170398"  // 15.4-consortium
params.new_release_synid = "syn62069187" // 15.6-consortium (in staging)
params.retracted_sample_synid = "syn54082015"  // 16.3-consortium samples_to_retract.csv
params.release = "15.6-consortium"
// project_id = "syn7208886"
params.project_id = "syn22033066" // staging project
if (params.project_id == "syn22033066") {
    is_production = false
} else if (params.project_id == "syn3380222") {
    is_production = true
} else {
    exit 1, "project_id must be syn22033066 or syn3380222"
}

workflow {
    ch_release_synid = Channel.value(params.release_synid)
    ch_new_release_synid = Channel.value(params.new_release_synid)
    ch_retracted_sample_synid = Channel.value(params.retracted_sample_synid)
    ch_release = Channel.value(params.release)
    ch_project_id = Channel.value(params.project_id)
    patch_release(ch_release_synid, ch_new_release_synid, ch_retracted_sample_synid, is_production)
    create_dashboard_html(patch_release.out, ch_release, is_production)
    create_data_guide(patch_release.out, ch_release, ch_project_id)
    compare_releases(create_data_guide.out, ch_release_synid, ch_new_release_synid)
}
