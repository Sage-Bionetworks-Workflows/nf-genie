# Synapse Compare

## Comparisons between two Synapse entities

### Purpose

This helper script does comparisons for any
two data based synapse entities in Synapse whether it's different versions within the same entity or two different entities. We currently support the following entities:

- Synapse Tables
- Synapse Files (structured data files that can be read into pandas like csv, txt, tsv)

There will be two reports outputted. One using the `datacompy` package and one using the `y-dataprofiling` package.

### Setting up your environment

#### Dependencies

- `python` >= 3.10, <=3.11

- `synapseclient`
- `pandas`
- [datacompy](https://github.com/capitalone/datacompy)
- [ydata-profiling](https://github.com/ydataai/ydata-profiling)
- `.synapseConfig` located in your local home directory
- READ/DOWNLOAD access to the synapse projects you want to compare entities from

You can use your favorite python environment manager like `pipenv`, `conda`, `uv` or just python virtual environment and install the dependencies from `requirements.txt`

#### Installation

Install the tool using the following command

```bash
pip install .
```

If you want to run tests:

```bash
pip install -e ".[dev]"
```

### How to Run
Use `syncompare --help` for more information on the arguments and what to specify.

You can also import in the `run_compare()` or `generate_comparison_reports()` function for custom code you want to use. The `generate_comparison_reports` function is especially useful if the default method of reading the data doesn't work and you need to use your own custom code to read in the data you want to compare.

**Here are some sample workflow run examples:**

#### Using local imports

```python
from synapse_compare.compare import run_compare

run_compare(
    syn_id_1="syn123",
    syn_id_2="syn456",
    version1="v1",
    version2="v2",
    compare_type="table",
    main_download_directory="output"
)
```

#### Using the cli

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
           --version-name1 v1 \
           --version-name2 v2 \
           --entity-name BPC_compare \
           --compare-type file \
           --join-keys id cohort
```

You can use the version arguments to filter on the version comments within a Synapse entity
by specifying `version_name1`, `version_name2` and `--filter-on-version`
Here we filter on "v1" vs "v2" in the version comment of the same table for the comparison.

```bash
syncompare --syn_id-1 syn1241249 \
           --syn_id-2 syn1241249 \
           --version-name1 v1 \
           --version-name2 v2 \
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

### Outputs

- A file named `<entity_name>_<version1>_vs_<version2>_comparison_report.txt"`
![alt text](img/datacompy-example.png) See [datacompy's pandas usage docs](https://capitalone.github.io/datacompy/pandas_usage.html) for more details on the fields provided in this report.

- A file named `<entity_name>_<version1>_vs_<version2>_comparison_report_detailed.html"`
![alt text](img/ydata-profiling-example.png) See [ydata-profiling's getting started page](https://docs.profiling.ydata.ai/latest/getting-started/concepts/) for more details on the sections provided in this report.
