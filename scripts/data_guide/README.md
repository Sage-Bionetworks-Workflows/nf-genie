# Updating the data guide

Add or update your information for your site into the dedicated field and then submit a pull request.



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

### Example command

This will generate the data_guide for TEST.consortium in the [TEST release folder](https://www.synapse.org/Synapse:syn21895009)

```bash
Rscript generate_data_guide_cli.R TEST.consortium syn7208886
```
