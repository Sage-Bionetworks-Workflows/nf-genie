from jinja2 import Template
import sys
import os
import subprocess
import pandas as pd
from synapseclient import Synapse, File

# Login to Synapse
syn = Synapse()
syn.login()

# Parse command-line arguments
release = sys.argv[1]
project_id = sys.argv[2]

# Function to get the release folder Synapse ID
def get_release_folder_synid(database_synid_mappingid, release):
    mapping_df = syn.tableQuery(f"SELECT * FROM {database_synid_mappingid}").asDataFrame()
    release_folder_id = mapping_df[mapping_df["Database"] == "releaseFolder"]["Id"].values[0]

    release_df = syn.tableQuery(
        f"""
        SELECT DISTINCT(name) AS releases FROM {release_folder_id}
        WHERE name NOT LIKE 'Release%' AND name <> 'case_lists'
        """
    ).asDataFrame()

    if release == "TEST.consortium":
        release = "TESTING"
    elif release == "TEST.public":
        release = "TESTpublic"

    if release not in release_df["releases"].values:
        all_releases = ", ".join(release_df["releases"])
        raise ValueError(f"Must choose correct release: {all_releases}")

    result = syn.tableQuery(
        f"SELECT id FROM {release_folder_id} WHERE name = '{release}'",
        includeRowIdAndRowVersion=False
    ).asDataFrame()

    return result["id"].values[0]

# Load template from file
with open("data_guide.qmd.j2") as f:
    template = Template(f.read())

# Substitute parameters
filled_qmd = template.render(release=release, project_id=project_id)

# Save output
with open("genie_output.qmd", "w") as f:
    f.write(filled_qmd)

# Render the Quarto PDF with execute parameters
subprocess.run([
    "quarto", "render", "genie_output.qmd"
], check=True)

# Get the release folder Synapse ID
project_ent = syn.get(project_id)
database_synid_mappingid = project_ent.annotations["dbMapping"][0]
release_folder_synid = get_release_folder_synid(database_synid_mappingid, release)
print(release_folder_synid)
# Upload the generated PDF back to Synapse
pdf_file = File("genie_output.pdf", parent=release_folder_synid)
syn.store(pdf_file, executed="https://github.com/Sage-Bionetworks-Workflows/nf-genie")

