#!/bin/bash

release_folder_synapse_id=$1

synapse get -r --followLink "$release_folder_synapse_id"
mv data_mutations_extended.txt data_mutations.txt
python calc_nonsyn_tmb.py -i . -p .
synapse store tmb_output_data_clinical_sample.txt --parentId "$release_folder_synapse_id"
