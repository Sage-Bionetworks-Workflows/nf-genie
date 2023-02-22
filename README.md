# nf-genie

Nextflow workflow for main GENIE processing.  This follows the SOP outlined in the GENIE confluence page.

## Process and developing locally

Follow instructions here for running the main GENIE processing locally. 

It's recommended to use an EC2 instance to run processing and develop locally. Follow instructions using [Service-Catalog-Provisioning](https://help.sc.sageit.org/sc/Service-Catalog-Provisioning.938836322.html) to create an ec2 on service catalog. You will also want to follow the section [SSM with SSH](https://help.sc.sageit.org/sc/Service-Catalog-Provisioning.938836322.html#ServiceCatalogProvisioning-SSMwithSSH) if you want to use VS code to run/develop.

### Dependencies

Install nextflow and any dependencies (e.g: Java) by following instructions here: [Get started — Nextflow](https://www.nextflow.io/docs/latest/getstarted.html#get-started)

#### Using an EC2

For an EC2 instance with Linux and docker, see here for installing JAVA 11: [How do I install a software package from the Extras Library on an EC2 instance running Amazon Linux 2?](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-install-extras-library-software/)

### Configuration

Prior to running the test pipeline, you will need to create a Nextflow secret called `SYNAPSE_AUTH_TOKEN`
with a Synapse personal access token ([docs](#authentication)).

### Authentication

This workflow takes care of transferring files to and from Synapse. Hence, it requires a secret with a personal access token for authentication. To configure Nextflow with such a token, follow these steps:

1. Generate a personal access token (PAT) on Synapse using [this dashboard](https://www.synapse.org/#!PersonalAccessTokens:). Make sure to enable the `view`, `download`, and `modify` scopes since this workflow both downloads and uploads to Synapse.
2. Create a secret called `SYNAPSE_AUTH_TOKEN` containing a Synapse personal access token using the [Nextflow CLI](https://nextflow.io/docs/latest/secrets.html) or [Nextflow Tower](https://help.tower.nf/latest/secrets/overview/).
3. (Tower only) When launching the workflow, include the `SYNAPSE_AUTH_TOKEN` as a pipeline secret from either your user or workspace secrets.

### Commands

You can visit [parameters](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/main/main.nf#L8-L16) to see the list of currently available parameters/flags and their default values if you don't specify any.

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

## Processing on Nextflow Tower

Follow instructions here for running the main GENIE processing directly on Nextflow tower

1. Please create a [IBCDPE help desk](https://sagebionetworks.jira.com/servicedesk/customer/portal/5) request to gain access to the genie-bpc-project on [Sage nextflow tower](https://tower.sagebionetworks.org/login).
1. After you have access, you will want to head to the [launchpad](https://tower.sagebionetworks.org/orgs/Sage-Bionetworks/workspaces/genie-bpc-project/launchpad)
1. Click on `main_genie`
1. Fill out the parameters like the image below - Make sure you update the release parameter! ![launch_nf.png](img/launch_nf.png)
