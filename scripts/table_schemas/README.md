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

### Input

The input data model expects a format like the following:

![data_model_picture.png](/img/data_model_picture.png)

With the following required columns:

- Attribute
- Valid Values
- Validation Rules

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

Run with these settings to create a table from a different input
data model that is not the default

```shell
python create_patient_sample_tracking_table_schema.py \
    --data-model-synid syn1241241
```

### Output

The output will look like the following:

![schema_output_picture.png](/img/schema_output_picture.png)

Default settings are 250 characters for `STRING` columns.
