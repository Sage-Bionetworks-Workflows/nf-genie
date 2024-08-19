"""
Patch releases occur when samples need to be retracted due to
patients withdrawing consent.

Patches should always occur on the latest consortium release for
the specific public release. Due to the GENIE retraction policy,
it is best to retract data on the 3rd consortium release of the
subsequent release series.
"""
import argparse
import os
import shutil
import tempfile

import pandas as pd
import synapseclient

from genie import (
    create_case_lists,
    dashboard_table_updater,
    process_functions
)

# Run time functions
def revise_meta_file(meta_file_path: str, old_version: str, new_version: str) -> None:
    """
    Replaces the old version with the new version in the meta file.

    Args:
        meta_file_path (str): The path to the meta file.
        old_version (str): The old version to be replaced.
        new_version (str): The new version to replace the old version.

    Returns:
        None
    """
    with open(meta_file_path, "r") as meta:
        meta_text = meta.read()
    with open(meta_file_path, "w") as meta:
        meta_text = meta_text.replace(old_version, new_version)
        meta.write(meta_text)

def _filter_tsv(filepath: str, keep_values: pd.Series, column: str) -> pd.DataFrame: 
    """
    Patches a tsv in Synapse by filtering out rows based on the provided keep values.

    Args:
        syn (synapseclient.Synapse): The Synapse client object.
        synid (str): The Synapse ID of the entity to be patched.
        keep_values (pd.Series): The values to keep in the dataframe.
        column (str): The column name to filter on.

    Returns:
        pd.DataFrame: The patched dataframe.
    """
    df = pd.read_csv(filepath, sep="\t", comment="#")
    # if not segdf.ID.isin(keep_samples).all():
    df = df[df[column].isin(keep_values)]
    return df

# TODO remove new_release parameter soon
def store_file(
    syn: synapseclient.Synapse, new_path: str, new_release_synid: str
) -> None:
    """
    Stores a file into Synapse.

    Args:
        syn (synapseclient.Synapse): The Synapse client object.
        new_path (str): The path to the file to be stored.
        new_release_synid (str): The Synapse ID of the release folder where the file will be stored.

    Returns:
        None
    """
    new_ent = synapseclient.File(new_path, parentId=new_release_synid)
    new_ent = syn.store(new_ent)
    return new_ent


def patch_file(syn: synapseclient.Synapse, synid: str, tempdir: str, new_release_synid: str, keep_values: pd.Series, column: str) -> str:
    """
    Patches a file in Synapse by filtering out rows based on the provided keep values.

    Args:
        syn (synapseclient.Synapse): The Synapse client object.
        synid (str): The Synapse ID of the entity to be patched.
        tempdir (str): The temporary directory to store the patched file.
        new_release_synid (str): The Synapse ID of the release folder where the patched file will be stored.
        keep_values (pd.Series): The values to keep in the dataframe.
        column (str): The column name to filter on.

    Returns:
        None
    """
    entity = syn.get(synid, followLink=True)
    df = _filter_tsv(filepath=entity.path, keep_values=keep_values, column=column)
    # Specific filtering fro the data gene matrix file because the string NA must
    # replace the blank values
    if entity.name == "data_gene_matrix.txt":
        df[df.isnull()] = "NA"
    # df = pd.read_csv(entity.path, sep="\t", comment="#")
    # df = df[df[column].isin(keep_values)]
    dftext = process_functions.removePandasDfFloat(df)
    new_path = os.path.join(tempdir, os.path.basename(entity.path))
    with open(new_path, "w") as o_file:
        o_file.write(dftext)
    store_file(syn, new_path, new_release_synid)
    # TODO: return a named tuple so its not just returning the path
    return new_path


def patch_cna_file(syn: synapseclient.Synapse, cna_synid: str, tempdir: str, new_release_synid: str, keep_samples: pd.Series) -> None:
    """
    Patches the CNA file in Synapse by filtering out columns based on the provided keep samples.

    Args:
        syn (synapseclient.Synapse): The Synapse client object.
        cna_synid (str): The Synapse ID of the CNA file to be patched.
        tempdir (str): The temporary directory to store the patched file.
        new_release_synid (str): The Synapse ID of the release folder where the patched file will be stored.
        keep_samples (pd.Series): The samples to keep in the CNA file.

    Returns:
        None
    """
    cna_ent = syn.get(cna_synid, followLink=True)
    cnadf = pd.read_csv(cna_ent.path, sep="\t", comment="#")
    cna_cols = ["Hugo_Symbol"]
    cna_cols.extend(keep_samples.tolist())
    cna_cols_idx = cnadf.columns.isin(cna_cols)
    if not cna_cols_idx.all():
        cnadf = cnadf[cnadf.columns[cna_cols_idx]]
        cnatext = process_functions.removePandasDfFloat(cnadf)
        cna_path = os.path.join(tempdir, os.path.basename(cna_ent.path))
        with open(cna_path, "w") as cna_file:
            cna_file.write(cnatext)
        store_file(syn, cna_path, new_release_synid)


def patch_release_workflow(
    release_synid: str, new_release_synid: str, retracted_sample_synid: str, production: bool = False
):
    """
    These need to be modified per retraction.
    The release_synid, new_release_synid, and retracted_sample_synid
    variables need to be changed to reflect different Synapse ids per release.
    """
    syn = synapseclient.login()

    # TODO: Add ability to provide list of centers / seq assay ids to remove
    # remove_centers = []
    # remove_seqassays = []
    old_release = syn.get(release_synid).name
    new_release = syn.get(new_release_synid).name

    retracted_samples_ent = syn.get(retracted_sample_synid)
    retracted_samplesdf = pd.read_csv(retracted_samples_ent.path)
    release_files = syn.getChildren(release_synid)

    # Get file mapping
    file_mapping = {
        release_file["name"]: release_file["id"] for release_file in release_files
    }
    sample_synid = file_mapping["data_clinical_sample.txt"]
    patient_synid = file_mapping["data_clinical_patient.txt"]
    cna_synid = file_mapping["data_CNA.txt"]
    fusion_synid = file_mapping["data_sv.txt"]
    gene_synid = file_mapping["data_gene_matrix.txt"]
    maf_synid = file_mapping["data_mutations_extended.txt"]
    genomic_info_synid = file_mapping.get("genie_combined.bed")
    if genomic_info_synid is None:
        genomic_info_synid = file_mapping["genomic_information.txt"]
    seg_synid = file_mapping.get("data_cna_hg19.seg")
    assay_info_synid = file_mapping["assay_information.txt"]

    # Sample and patient column to cBioPortal mappings
    mapping_table = syn.tableQuery("SELECT * FROM syn9621600")
    mapping = mapping_table.asDataFrame()

    # Create temporary directory to download files
    tempdir_o = tempfile.TemporaryDirectory()
    tempdir = tempdir_o.name
    # Create clinical file

    # Obtain samples retracted
    sample_ent = syn.get(sample_synid, followLink=True)
    sampledf = pd.read_csv(sample_ent.path, sep="\t", comment="#")
    centers = [patient.split("-")[1] for patient in sampledf.PATIENT_ID]
    sampledf["CENTER"] = centers
    # Retract samples from SEQ_ASSAY_ID, CENTER and retract samples list
    # to_remove_seqassay_rows = sampledf["SEQ_ASSAY_ID"].isin(remove_seqassays)
    # sampledf = sampledf[~to_remove_seqassay_rows]
    # to_remove_center_rows = sampledf["CENTER"].isin(remove_centers)
    # sampledf = sampledf[~to_remove_center_rows]
    to_remove_samples = sampledf["SAMPLE_ID"].isin(retracted_samplesdf.SAMPLE_ID)
    final_sampledf = sampledf[~to_remove_samples]
    # Check number of seq assay ids is the same after removal of samples
    # Must add to removal of seq assay list for gene panel removal
    # seq_assay_after = final_sampledf["SEQ_ASSAY_ID"].unique()
    # seq_assay_before = sampledf["SEQ_ASSAY_ID"].unique()
    # if len(seq_assay_after) != len(seq_assay_before):
    #     remove_seqassays.extend(
    #         seq_assay_before[~seq_assay_before.isin(seq_assay_after)].tolist()
    #     )
    # Check number of centers is the same after removal of samples
    # Must add to removal of seq assay list for gene panel removal
    # center_after = final_sampledf["CENTER"].unique()
    # center_before = sampledf["CENTER"].unique()
    # if len(center_after) != len(center_before):
    #     remove_centers.extend(center_before[~center_before.isin(center_after)].tolist())

    del final_sampledf["CENTER"]

    keep_samples = final_sampledf["SAMPLE_ID"].drop_duplicates()
    keep_patients = final_sampledf["PATIENT_ID"].drop_duplicates()
    keep_seq_assay_id = final_sampledf["SEQ_ASSAY_ID"].drop_duplicates()

    patient_ent = syn.get(patient_synid, followLink=True)
    patientdf = pd.read_csv(patient_ent.path, sep="\t", comment="#")
    patientdf = patientdf[patientdf["PATIENT_ID"].isin(keep_patients)]

    clinicaldf = final_sampledf.merge(patientdf, on="PATIENT_ID", how="outer")

    clin_ent = syn.get(file_mapping.get("data_clinical.txt"), followLink=True)
    full_clin_df = pd.read_csv(clin_ent.path, sep="\t", comment="#")
    clinical_path = os.path.join(tempdir, os.path.basename(clin_ent.path))
    # GEN-646: Make sure to subset the clinical dataframe or else
    # There will be issues downstream. The dashboard code along with
    # public release code rely on the merged clinical file.
    full_clin_df = full_clin_df[full_clin_df["SAMPLE_ID"].isin(keep_samples)]
    full_clin_df.to_csv(clinical_path, sep="\t", index=False)
    full_clinical_entity = store_file(syn, clinical_path, new_release_synid)
    # Revoke access to general GENIE consortium on data_clinical.txt file
    # Because it has more data than the consortium should see.
    syn.setPermissions(full_clinical_entity, principalId=3326313, accessType=[])

    sample_path = os.path.join(tempdir, os.path.basename(sample_ent.path))
    patient_path = os.path.join(tempdir, os.path.basename(patient_ent.path))

    process_functions.addClinicalHeaders(
        clinicaldf,
        mapping,
        patientdf.columns,
        sampledf.columns,
        sample_path,
        patient_path,
    )
    store_file(syn, sample_path, new_release_synid)
    store_file(syn, patient_path, new_release_synid)
    # Patch CNA file
    patch_cna_file(syn, cna_synid, tempdir, new_release_synid, keep_samples)

    # Patch Fusion file
    patch_file(syn, fusion_synid, tempdir, new_release_synid, keep_samples, "Sample_Id")

    # Patch SEG file
    patch_file(syn, seg_synid, tempdir, new_release_synid, keep_samples, "ID")

    # Patch gene matrix file
    patch_file(syn, gene_synid, tempdir, new_release_synid, keep_samples, "SAMPLE_ID")

    # Patch maf file
    patch_file(syn, maf_synid, tempdir, new_release_synid, keep_samples, "Tumor_Sample_Barcode")

    # Patch genomic information file
    patch_file(syn, genomic_info_synid, tempdir, new_release_synid, keep_seq_assay_id, "SEQ_ASSAY_ID")

    # Patch assay information file
    assay_path = patch_file(syn, assay_info_synid, tempdir, new_release_synid, keep_seq_assay_id, "SEQ_ASSAY_ID")

    # Create cBioPortal case lists
    case_list_path = os.path.join(tempdir, "case_lists")
    if not os.path.exists(case_list_path):
        os.mkdir(case_list_path)
    create_case_lists.main(clinical_path, assay_path, case_list_path, "genie_private")

    case_list_files = os.listdir(case_list_path)
    case_list_folder_synid = syn.store(
        synapseclient.Folder("case_lists", parentId=new_release_synid)
    ).id
    for case_filename in case_list_files:
        # if case_filename in case_file_synids:
        case_path = os.path.join(case_list_path, case_filename)
        store_file(syn, case_path, case_list_folder_synid)

    # Create cBioPortal gene panel and meta files
    for name in file_mapping:
        if name.startswith("data_gene_panel"):
            seq_name = name.replace("data_gene_panel_", "").replace(".txt", "")
            if seq_name not in keep_seq_assay_id:
                continue
            gene_panel_ent = syn.get(file_mapping[name], followLink=True)
            new_panel_path = os.path.join(tempdir, os.path.basename(gene_panel_ent.path))
            shutil.copyfile(gene_panel_ent.path, new_panel_path)
            store_file(syn, new_panel_path, new_release_synid)
        elif name.startswith("meta") or "_meta_" in name:
            meta_ent = syn.get(file_mapping[name], followLink=True)
            new_meta_path = os.path.join(tempdir, os.path.basename(meta_ent.path))
            shutil.copyfile(meta_ent.path, new_meta_path)
            revise_meta_file(new_meta_path, old_release, new_release)
            store_file(syn, new_meta_path, new_release_synid)

    tempdir_o.cleanup()
    # Update dashboard tables
    # Data base mapping synid
    if production:
        database_mapping_synid = "syn10967259"
    else:
        database_mapping_synid = "syn12094210"
    database_mapping = syn.tableQuery(f"select * from {database_mapping_synid}")
    database_mappingdf = database_mapping.asDataFrame()
    # You may have to execute this twice in case the file view isn't updated
    dashboard_table_updater.run_dashboard(syn, database_mappingdf, new_release, staging=not production)


def main():
    parser = argparse.ArgumentParser(description="Store a file in Synapse.")

    parser.add_argument(
        "release_synid",
        type=str,
        help="The Synapse Id of the consortium release folder",
    )
    parser.add_argument(
        "new_release_synid",
        type=str,
        help="The Synapse Id of the new release folder (has to be created)",
    )
    parser.add_argument(
        "retracted_sample_synid",
        type=str,
        help="The Synapse Id of the samples_to_retract.csv file generated in the current 3rd consortium release.",
    )
    # this parameter is mainly for the dashboard upload step
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run production workload or it will default to the staging workload"
    )
    args = parser.parse_args()

    patch_release_workflow(
        release_synid=args.release_synid,
        new_release_synid=args.new_release_synid,
        retracted_sample_synid=args.retracted_sample_synid,
        production=args.production
    )


if __name__ == "__main__":
    main()
