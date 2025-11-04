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

The commands under [Commands](#commands) run on the test pipeline. To run on production pipeline, specify a specific value to the `release` parameter, e.g:

- 13.1-public (for public releases)
- 13.1-consortium (for consortium releases)

#### Parameters

You can run the following command to get a list of the current available
parameters, their defaults and descriptions.

```
nextflow run main.nf --help
```

See [nextflow_schema.json](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/main/nextflow_schema.json) for the same thing.

#### Config Profiles

We use two profiles for the pipeline which contains the docker container defaults and resource specifications for running the pipeline:

- **aws_prod** - used for production pipeline runs
- **aws_test** - used for test pipeline runs


See [nextflow.config](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/main/nextflow.config) for more details on the profiles' content. Read more about config profiles and how to call them here: [Config Profiles](https://www.nextflow.io/docs/latest/config.html#config-profiles)

#### Running with docker locally

Add `-with-docker <docker_image_name>` and specify the docker image parameter to every nextflow command to invoke docker in general to be used. See [docker-containers](https://www.nextflow.io/docs/latest/docker.html#docker-containers) for more details.

See [nextflow.config](/nextflow_schema.json) for the docker parameters available.

Note that all the docker parameters have set default docker containers based on the **profile** you select. If you want to use a different default from what is available in the profiles, you must:

1. Docker pull the container(s) you want to use in your local / ec2 instance
2. Specify the parameter(s) in your command call below to be the container(s) you pulled

#### Commands

* **Only validate** files on test pipeline

    ```
    nextflow run main.nf -profile aws_test \
            --process_type only_validate \
            -with-docker ghcr.io/sage-bionetworks/genie:develop
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

* Processes **non-mutation** files on test pipeline

    ```
    nextflow run main.nf -profile aws_test \
            --process_type main_process \
            -with-docker ghcr.io/sage-bionetworks/genie:develop
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

* Processes **mutation** files on test pipeline
1. To execute the MAF process for all centers, you can either specify the `maf_centers` as "ALL" or leave it blank.
    ```
    nextflow run main.nf -profile aws_test \
            --process_type maf_process \
            --create_new_maf_db \
            -with-docker ghcr.io/sage-bionetworks/genie:develop
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```
    Or
    ```
    nextflow run main.nf -profile aws_test \
            --process_type maf_process \
            --maf_centers ALL \
            --create_new_maf_db \
            -with-docker ghcr.io/sage-bionetworks/genie:develop \
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```
2. To execute the MAF process for a single center, you can specify the `maf_centers` parameter using the name of that center.
    ```
    nextflow run main.nf -profile aws_test \
            --process_type maf_process \
            --maf_centers TEST \
            --create_new_maf_db \
            -with-docker ghcr.io/sage-bionetworks/genie:develop \
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

3. To execute the MAF process for multiple centers, you can specify the `maf_centers` as a comma-separated list of center names and **append** results to the MAF table.
    ```
    nextflow run main.nf -profile aws_test \
            --process_type maf_process \
            --maf_centers TEST,SAGE \
            --create_new_maf_db false \
            -with-docker ghcr.io/sage-bionetworks/genie:develop \
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

* Runs **processing** and **consortium** release (including data guide creation) on test pipeline
    ```
    nextflow run main.nf -profile aws_test \
            --process_type consortium_release \
            --create_new_maf_db \
            -with-docker ghcr.io/sage-bionetworks/genie:develop
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

* Runs **public** release (including data guide creation) on test pipeline

    ```
    nextflow run main.nf -profile aws_test \
            --process_type public_release \
            -with-docker ghcr.io/sage-bionetworks/genie:develop
            --main_pipeline_docker ghcr.io/sage-bionetworks/genie:develop
    ```

### Testing

Run unit tests from the root of the repo. These unit tests cover the code in the `scripts/` directory.

```
python3 -m pytest tests
```

Unit tests have to be run manually for now. You will need
`pandas` and `synapseclient` to run them. See [Dockerfile](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/main/scripts/release_utils/Dockerfile) for the version of `synapseclient` to use.

## Processing on Seqera Platform

Follow instructions here for running the main GENIE processing directly on Seqera Platform:

1. Please create a [IBCDPE help desk](https://sagebionetworks.jira.com/servicedesk/customer/portal/5) request to gain access to the `genie-bpc-project` on [Seqera Platform](https://tower.sagebionetworks.org/login).
1. After you have access, you will want to head to the [launchpad](https://tower.sagebionetworks.org/orgs/Sage-Bionetworks/workspaces/genie-bpc-project/launchpad)
1. Click on the `test_main_genie` pipeline
1. Fill out the parameters for launching the specific parts of the pipeline. ![launch_nf.png](/img/launch_nf.png)
1. If you need to modify any of the underlying default launch settings like config profiles or run a pipeline on a feature branch rather than `develop` or `main`, navigate back to the **Launchpad** and click on **Add pipeline**. ![add_pipeline.png](/img/add_pipeline.png) Typically, the relevant settings you would need to modify would be the following:
    - **Config profiles** - profile to launch with, see [Config profiles](#config-profiles) for more details
    - **Revision number** - branch of `nf-genie` that you're launching the pipeline on

Visit the [Nextflow Tower docs for more info/training](https://docs.seqera.io/platform/)
