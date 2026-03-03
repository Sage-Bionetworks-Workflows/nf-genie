# Synapse Compare

## Table of Contents

- [Purpose](#purpose)
- [Data Requirements](#data-requirements)
  - [Supported Synapse Entities](#supported-synapse-entities)
  - [Supported File Formats](#supported-file-formats)
  - [Schema Expectations](#schema-expectations)
- [Setting up your environment](#setting-up-your-environment)
  - [Dependencies](#dependencies)
  - [Configuration](#configuration)
  - [Installation](#installation)
- [Usage](#usage)
  - [Using local imports](#using-local-imports)
    - [Demo](#demo)
  - [Using the CLI](#using-the-cli)
- [Outputs](#outputs)
  - [datacompy compare report](#datacompy-compare-report)
  - [ydata-profiling report](#ydata-profiling-report)

## Purpose

This tool does comparisons for any
two data based synapse entities in Synapse whether it's different versions within the same entity or two different entities.

There will be two reports outputted. One using the `datacompy` package and one using the `y-dataprofiling` package.

## Data Requirements

This tool is designed for **tabular data only**.

### Supported Synapse Entities

- **Synapse Tables**
- **Synapse Files containing structured tabular data**

### Supported File Formats

For Synapse Files (`--compare-type file`), the file must:

- Be readable by `pandas.read_csv`
- Be comma-separated (e.g: `.csv`) **OR**
- Be tab-separated (e.g: `.tsv`, `.txt`, `\t` delimited)

If your data is not already in the above format, you must convert it to a tabular text format before running the comparison.

### Schema Expectations

- Both datasets must contain at **least one column in common**.
- Large datasets may result in slower profiling report generation.

## Setting up your environment

### Dependencies

- python >=3.10,<=3.11
- pandas >=2.0.0,<3.0.0
- synapseclient >=4.5.1,<4.10.0
- [datacompy](https://github.com/capitalone/datacompy)
- [ydata-profiling](https://github.com/ydataai/ydata-profiling)

### Configuration

Follow the [Synapse client configuration setup](https://docs.synapse.org/synapse-docs/client-configuration) to use Synapse programmatically.

You will also need **READ/DOWNLOAD** access to the synapse entities you want to compare. [OPTIONAL] You will need **READ/WRITE** access to the synapse entity you want to save reports to IF you plan to save reports to Synapse.

### Installation

1. `git clone` the [nf-genie repo](https://github.com/Sage-Bionetworks-Workflows/nf-genie)

1. Create a virtual python environment and activate it

    ```bash
    python3 -m venv <my_venv_name>
    source <my_venv_name>/bin/activate
    ```

1. Navigate to the synapse compare directory

    ```bash
    cd nf-genie/scripts/synapse_compare
    ```

1. Install the compare tool using the following command

    ```bash
    pip install .
    ```

    [OPTIONAL] If you want to run the tests

    ```bash
    pip install -e ".[dev]"
    pytest
    ```

## Usage

You can locally import in the functions or use the command line interface (cli)

### Using local imports

For local imports, you can import in the `run_compare()` or `generate_comparison_reports()` functions for custom code you want to use. The `generate_comparison_reports` function is especially useful if the method of reading the data doesn't work and you need to use your own custom code to read in the data you want to compare or you've already transformed/read in your data in your workflow.

Basic Synapse Table comparison

```python
from synapse_compare.compare_between_two_synapse_entities import run_compare

run_compare(
    syn_id_1="syn123",
    syn_id_2="syn456",
    version1="v1",
    version2="v2",
    compare_type="table",
    main_download_directory="output"
)
```

Using custom pandas `read_csv` parameters. This is only available when you import the functions locally and not via the cli.

```python
from synapse_compare.compare_between_two_synapse_entities import run_compare

run_compare(
    syn_id_1="syn12345678",
    syn_id_2="syn87654321",
    version1="v1",
    version2="v2",
    compare_type="file",
    entity_name="custom_csv_test",
    main_download_directory="comparison_output_csv",
    csv_kwargs={
        "sep": "\t",
        "dtype": {"sample_id": "string"},
        "low_memory": False,
    }
)
```

#### Demo

There is a demo notebook that uses local imports of the functions in the synapse compare tool that you can work from (will have to supply your own synapse ids) [available here](/scripts/synapse_compare/synapse_compare_demo.ipynb)

You will need to install `juypter notebook` in your environment and then you can launch the demo like:

```bash
jupyter notebook synapse_compare_demo.ipynb
```

### Using the cli

Use `syncompare --help` for more information on the arguments and what to specify.

To run a comparison between two different Synapse Tables on their latest versions
on the common columns (keys) id and cohort

```bash
syncompare --syn-id-1 syn1241249 \
           --syn-id-2 syn2423523 \
           --compare-type table \
           --join-keys id cohort
```

To run a comparison between two different versions within a Synapse File
on the common columns (keys) id and cohort.

```bash
syncompare --syn-id-1 syn1241249.23 \
           --syn-id-2 syn1241249.35 \
           --entity-name BPC_compare \
           --compare-type file \
           --join-keys id cohort
```

You can use the version arguments to filter on the version comments within a Synapse entity
by specifying `version_name1`, `version_name2` and `--filter-on-version`
Here we filter on "v1" vs "v2" in the version comment of the same table for the comparison. It is best to enclose the value in "" in case you have spaces / other characters.

```bash
syncompare --syn_id-1 syn1241249 \
           --syn_id-2 syn1241249 \
           --version-name1 "v1" \
           --version-name2 "v2" \
           --filter-on-version \
           --compare-type table \
           --join-keys id cohort \
```

Save your output reports to a synapse entity by specifying
`--save-to-synapse` and a synapse entity synapse id for `--output-synid`

```bash
syncompare --syn_id-1 syn1241249 \
           --syn_id-2 syn1241249 \
           --version-name1 v1 \
           --version-name2 v2 \
           --filter-on-version \
           --compare-type table \
           --join-keys id cohort \
           --save-to-synapse \
           --output-synid syn218418 \
```

## Outputs

You will get two reports outputted IF there are differences between your two datasets:

- `<entity_name>_<version1>_vs_<version2>_comparison_report.txt`
- `<entity_name>_<version1>_vs_<version2>_comparison_report_detailed.html`

### datacompy compare report

`<entity_name>_<version1>_vs_<version2>_comparison_report.txt`

![alt text](img/datacompy-example.png) See [datacompy's pandas usage docs](https://capitalone.github.io/datacompy/pandas_usage.html) for more details on the fields provided in this report.

---

### ydata-profiling report

`<entity_name>_<version1>_vs_<version2>_comparison_report_detailed.html`

![alt text](img/ydata-profiling-example.png) See [ydata-profiling's getting started page](https://docs.profiling.ydata.ai/latest/getting-started/concepts/) for more details on the sections provided in this report.

## Troubleshooting

This section is always in development

### Data types differences

The second tool `ydata-profiling` that is used to generate the second more detailed report `<entity_name>_<version1>_vs_<version2>_comparison_report_detailed.html` tends to be more sensitive to data type differences between columns that are used as the `join-keys` / columns in common. You would need to do additional tweaking of the data to have the second report be generated at times.

Some common error messages:

```
ValueError: Types for variant_classification are not compatible: {'Unsupported', 'Text'}
```

```
ValueError: You are trying to merge on object and float64 columns for key 'variant_classification'. If you wish to proceed you should use pd.concat
```

### Generating report freezes

Since the second report also also shows summary details per column, often times when a dataset has tens of thousands of rows / lots of unique values per column, the second report will just freeze at the summarize dataset step. Would try to see if you can break your data into partitions (e.g: by cohort or cancer) to do the comparison until more optimization is done for the second report tool.

![alt text](/scripts/synapse_compare/img/loading_times.png)
