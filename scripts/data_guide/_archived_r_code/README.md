# R data guide

> [!CAUTION]
> As of April 2025, we are shifting towards using a Python-based version of the data guide instead of having to install the R dependencies.

This folder contains the legacy code for the old data guide and will most likely not run as is due to pathing issues.


## Running via Service Catalog
Sometimes the nextflow step for the `create_data_guide.nf` will fail due to an issue with the docker image. Since troubleshooting for the docker image can easily take over a few days to resolve, try the manual approach to generate the data guide:

[Follow instructions here](https://sagebionetworks.jira.com/wiki/spaces/APGD/pages/2590244872/Service+Catalog+Instance+Setup#Starting-EC2-instance-from-the-Service-Catalog) for using the Service catalog

### Instructions

1. Create instance under EC2 with Notebook Software and wait for creation. Open up your Notebook via the `NotebookConnectionURI` under `Outputs` tab
2. In the terminal, clone [nf-genie](https://github.com/Sage-Bionetworks-Workflows/nf-genie) and checkout `main` branch

```git
git clone https://github.com/Sage-Bionetworks-Workflows/nf-genie.git
git checkout main
```

3. Create new project on `nf-genie` directory in your R notebook
4. Open up the `generate_data_guide_cli.R` and `data_guide.qmd` files under `scripts/data_guide` on your notebook UI. You should be prompted to install required packages for each file you view, proceed to install.
5. Run the following in the terminal to install the latest version of `tinytex`

```bash
quarto install tinytex
```

6. If you don't have quarto installed, run the following to install it

```bash
wget -qO quarto.deb https://quarto.org/download/latest/quarto-linux-amd64.deb
```

7. Run the following command on the terminal to generate and save your data guide

```bash
Rscript generate_data_guide_cli.R <consortium_release> <project_id>
```

8. [Optional] Sometimes depending on the rendering, you may have the front page genie banner be cut off/too big like the below example ![alt text](/img/cut_off_genie_banner.png) To resolve, you will need to adjust [this width in the data_guide.qmd file](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/df3796dce8431fc2a86e297a7350058241c1321c/scripts/data_guide/data_guide.qmd#L11) (e.g: used `15cm` instead of `20cm` for the example below)

### Example command

This will generate the data_guide for TEST.consortium in the [TEST release folder](https://www.synapse.org/Synapse:syn21895009)

```bash
Rscript generate_data_guide_cli.R TEST.consortium syn7208886
```
