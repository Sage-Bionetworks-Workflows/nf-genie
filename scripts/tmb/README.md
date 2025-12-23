# Calculate TMB

1. Follow readme here: https://github.com/cBioPortal/datahub-study-curation-tools/tree/master/tmb/calculate_tmb
1. download the script and setup environment

    ```
    wget https://raw.githubusercontent.com/cBioPortal/datahub-study-curation-tools/refs/heads/master/tmb/calculate_tmb/calc_nonsyn_tmb.py
    pip install -r requirements.txt
    ```

1. Download a GENIE release (Example 17.6)

    ```
    synapse get -r --followLink syn64386356
    ```

1. Rename files as needed

    ```
    mv data_mutations_extended.txt data_mutations.txt
    ```

1. Run code

    ```
    python calc_nonsyn_tmb.py -i . -p .
    ```

1. View `tmb_output_data_clincal_sample.txt`
