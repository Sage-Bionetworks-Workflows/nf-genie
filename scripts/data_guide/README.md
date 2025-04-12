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

3. Create a new python virtual environment in your `nf-genie` directory. `pip install -r requirements.txt`
4. Run the following in the terminal to install the latest version of `tinytex`

    ```bash
    quarto install tinytex
    ```

5. If you don't have quarto installed, run the following to install it

    ```bash
    wget -qO quarto.deb https://quarto.org/download/latest/quarto-linux-amd64.deb
    ```

6. Run the following command on the terminal to generate and save your data guide

    ```bash
    python generate_data_guide.py <consortium_release> <project_id>
    ```

8. [Optional] Sometimes depending on the rendering, you may have the front page genie banner be cut off/too big like the below example ![alt text](/img/cut_off_genie_banner.png) To resolve, you will need to adjust [this width in the data_guide.qmd file](https://github.com/Sage-Bionetworks-Workflows/nf-genie/blob/df3796dce8431fc2a86e297a7350058241c1321c/scripts/data_guide/data_guide.qmd#L11) (e.g: used `15cm` instead of `20cm` for the example below)

### Example command

This will generate the data_guide for TEST.consortium in the [TEST release folder](https://www.synapse.org/Synapse:syn21895009)

```bash
python generate_data_guide.py TEST.consortium syn7208886
```
