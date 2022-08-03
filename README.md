# nf-genie
Nextflow workflow for main GENIE processing.  This follows the SOP outlined in the GENIE confluence page.


## Command

* Execution of test pipeline

    ```
    nextflow run main.nf
    ```

* Only validate files (remove the `--production` flag to run the test pipeline)

    ```
    nextflow run main.nf --only_validate --production
    ```

* Consortium release (remove the `--production` flag to run the test pipeline)

    ```
    nextflow run main.nf --production --release 13.1-consortium --create_new_maf_db
    ```

* Public release (remove the `--production` flag to run the test pipeline)

    ```
    nextflow run main.nf --production --release 13.0-public
    ```