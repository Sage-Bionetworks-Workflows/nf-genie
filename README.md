# nf-genie

Nextflow workflow for main GENIE processing.  This follows the SOP outlined in the GENIE confluence page.

## Process and developing locally

Follow instructions here for running the main GENIE processing locally. 

It's recommended to use an EC2 instance with docker to run processing and develop locally. Follow instructions using [Service-Catalog-Provisioning](https://help.sc.sageit.org/sc/Service-Catalog-Provisioning.938836322.html) to create an ec2 on service catalog. You will also want to follow the section [SSM with SSH](https://help.sc.sageit.org/sc/Service-Catalog-Provisioning.938836322.html#ServiceCatalogProvisioning-SSMwithSSH) if you want to use VS code to run/develop.

### Dependencies

1. Install nextflow and any dependencies (e.g: Java) by following instructions here: [Get started — Nextflow](https://www.nextflow.io/docs/latest/getstarted.html#get-started)
2. Be sure to pull the latest version of the main GENIE docker image into your environment, see here for more details: [GENIE Dockerhub](https://github.com/Sage-Bionetworks/Genie/blob/develop/CONTRIBUTING.md#dockerhub)

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

### Running the pipeline

The following commands run on the test pipeline. To run on production pipeline, specify a specific value to the `release` parameter, e.g:

- 13.1-public (for public releases)
- 13.1-consortium (for consortium releases)

#### Parameters

See `nextflow_schema.json` to see the list of currently available parameters/flags and their default values if you don't specify any.

#### Running with docker

Add `-with-docker <docker_image_name>` to every nextflow command to invoke the specified docker container(s) in your modules. See [docker-containers](https://www.nextflow.io/docs/latest/docker.html#docker-containers) for more details.

#### Commands
* **Only validate** files on test pipeline

    ```
    nextflow run main.nf --process_type only_validate -with-docker sagebionetworks/genie:latest
    ```

* Processes **non-mutation** files on test pipeline

    ```
    nextflow run main.nf --process_type main_process -with-docker sagebionetworks/genie:latest
    ```

* Processes **mutation** files on test pipeline

    ```
    nextflow run main.nf --process_type maf_process --create_new_maf_db -with-docker sagebionetworks/genie:latest
    ```

* Runs **processing** and **consortium** release (including data guide creation) on test pipeline
    ```
    nextflow run main.nf --process_type consortium_release --create_new_maf_db -with-docker sagebionetworks/genie:latest
    ```

* Runs **public** release (including data guide creation) on test pipeline

    ```
    nextflow run main.nf --process_type public_release -with-docker sagebionetworks/genie:latest
    ```

## Processing on Nextflow Tower

Follow instructions here for running the main GENIE processing directly on Nextflow tower

1. Please create a [IBCDPE help desk](https://sagebionetworks.jira.com/servicedesk/customer/portal/5) request to gain access to the genie-bpc-project on [Sage nextflow tower](https://tower.sagebionetworks.org/login).
1. After you have access, you will want to head to the [launchpad](https://tower.sagebionetworks.org/orgs/Sage-Bionetworks/workspaces/genie-bpc-project/launchpad)
1. Click on `main_genie`
1. Fill out the parameters for launching the specific parts of the pipeline.[launch_image](img/launch_nf.png)
