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


## Processing

1. Please create a [IBCDPE help desk](https://sagebionetworks.jira.com/servicedesk/customer/portal/5) request to gain access to the genie-bpc-project on [Sage nextflow tower](https://tower.sagebionetworks.org/login).
1. After you have acess, you will want to head to the [launchpad](https://tower.sagebionetworks.org/orgs/Sage-Bionetworks/workspaces/genie-bpc-project/launchpad)
1. Click on main_genie
1. Fill out the parameters like the image below - Make sure you update the release parameter! ![launch_nf.png](img/launch_nf.png)
