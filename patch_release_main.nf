#!/usr/bin/env nextflow
// Ensure DSL2
nextflow.enable.dsl = 2

// IMPORT MODULES
include { patch_release } from './modules/patch_release'

params.release_synid = null
params.new_release_synid = null
params.retracted_sample_synid = null

workflow {
    patch_release(params.release_synid, params.new_release_synid, params.retracted_sample_synid)
}
