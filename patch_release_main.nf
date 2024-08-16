#!/usr/bin/env nextflow
// Ensure DSL2
nextflow.enable.dsl = 2

// IMPORT MODULES
include { patch_release } from './modules/patch_release'
include { create_dashboard_html } from './modules/create_dashboard_html'



params.release_synid = "syn53170398"  // 15.4-consortium
params.new_release_synid = "syn62069187" // 15.6-consortium (in staging)
params.retracted_sample_synid = "syn54082015"  // 16.3-consortium samples_to_retract.csv
params.release = "15.6-consortium"
// project_id = "syn7208886"
params.project_id = "syn22033066" // staging project
params.production = false // production is false

workflow {
    patch_release(params.release_synid, params.new_release_synid, params.retracted_sample_synid)
    create_dashboard_html(patch_release.out, params.release, params.production)
    create_data_guide(patch_release.out, params.release, params.project_id)
}
