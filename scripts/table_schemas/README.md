# Table Schemas

## Overview

This module contains the scripts that spin up any Synapse Tables in genie

## Setup

Build docker image:
```
cd scripts/table_schemas
docker build -f Dockerfile -t <docker_image_name> .
```

Run docker image in interactive mode:
```
docker run -it -e SYNAPSE_AUTH_TOKEN=<insert_synapse_token> <docker_image_name>
```

## Create Patient and Sample Tracking Table Script

### Updating the Table Schema

Here are a few scenarios where you might want to update the table:

- When there are new BPC cohort or SP projects that get released, the `STRING_COLS` and `BOOLEAN_COLS` will need to be updated. Please create a PR with the updated values.

- When there are Table Wiki changes - please update directly in the Synapse Table Wiki but also add a PR to include it here so that if the table ever gets spun up, it will have the new changes

### How to Run

Run with default settings to create an empty table called
`STAGING Patient and Sample Tracking Table` in the staging project

```shell
python create_patient_sample_tracking_table_schema.py
```

Run with these settings to create an empty table called
`TEST Patient and Sample Tracking Table` in the test project

```shell
python create_patient_sample_tracking_table_schema.py \
    --table-name "TEST Patient and Sample Tracking Table" \
    --project-synid syn7208886
```

### Output

The output will look like the following:

![schema_output_picture.png](/img/schema_output_picture.png)

Default settings are 250 characters for `STRING` columns.
