"""Most current consortium release cBioPortal files to BPC Synapse Project
Consortium releases to internal BPC page"""

import argparse
from typing import Dict

import synapseclient
from synapseclient import Folder
import synapseutils as synu


def get_release_synids(test: bool = False) -> Dict[str, str]:
    """Retrieves the set of synapse ids associated with the
       test or production versions of the entities associated with the release

    Args:
        test (bool, optional): Whether this is using the test project or not
            Defaults to False.

    Returns:
        Dict[str, str]: mapping of the synapse entity name to the synapse id
    """
    if test:
        return {
            "data_folder_synid": "syn53879650",
            "release_table_synid": "syn12299959",
        }
    else:
        return {
            "data_folder_synid": "syn21574209",
            "release_table_synid": "syn16804261",
        }


def find_release(
    syn: synapseclient.Synapse, release: str, release_table_synid: str, test: bool
) -> str:
    """Finds the Synapse id of a private consortium release folder

    Args:
        syn (synapseclient.Synapse): synaspe client connection
        release (str): name of the consortium release
        release_table_synid (str): synapse id of the release table
        test (bool, optional): Whether this is using the test project or not

    Raises:
        ValueError: raised if no table record exists for the specified release

    Returns:
        str: the synapse id of the release folder
    """
    if test:
        # use the release folder directly
        return release_table_synid
    else:
        release_synid = syn.tableQuery(
            "select distinct(parentId) from {} where "
            "release = '{}'".format(release_table_synid, release)
        )
        releasedf = release_synid.asDataFrame()
        if releasedf.empty:
            raise ValueError("Please specify correct release value")
        return releasedf.iloc[0, 0]


def remove_gene_panels(syn, file_mapping, remove_seqassays, remove_centers):
    """ NOTE: Is this still needed?
        Removes gene panels that shouldn't be there
    """
    for name in file_mapping:
        gene_name = name.replace("data_gene_panel_", "").replace(".txt", "")
        if gene_name in remove_seqassays or gene_name.startswith(tuple(remove_centers)):
            print(name)
            print(file_mapping[name])
            syn.delete(file_mapping[name])


def main(release: str, test: bool) -> None:
    """Updated BPC project 

    Args:
        release (str): name of the release 
        test (bool): testing or not
    """
    # if release.endswith("1-consortium"):
    #     raise ValueError("First consortium release are not released")

    syn = synapseclient.login()

    ent_synids = get_genie_folder_synids(test)

    # Finds the synid of the release
    release_synid = find_release(
        syn,
        release=release,
        release_table_synid=ent_synids["release_table_synid"],
        test=test,
    )

    # Get existing BPC cBioPortal release files
    major_release = release.split(".")[0]
    release_folder_ent = syn.store(
        Folder(f"Release {major_release}", parent=ent_synids["data_folder_synid"])
    )
    bpc_folder_ent = syn.store(Folder(release, parent=release_folder_ent))
    caselist_folder_ent = syn.store(Folder("case_lists", parent=bpc_folder_ent))
    genepanel_folder_ent = syn.store(Folder("gene_panels", parent=bpc_folder_ent))

    # Get existing gene panels
    existing_gene_panels = syn.getChildren(genepanel_folder_ent)
    genepanel_map = {exist["name"]: exist["id"] for exist in existing_gene_panels}
    # Get existing case lists
    case_list = syn.getChildren(caselist_folder_ent)
    caselist_map = {case["name"]: case["id"] for case in case_list}

    # Get release files
    release_files = syn.getChildren(release_synid)
    synid_map = {release["name"]: release["id"] for release in release_files}

    # Copy gene panel files
    for name in synid_map:
        if name.startswith("data_gene_panel_"):
            ent = syn.get(synid_map[name], followLink=True, downloadFile=False)
            synu.copy(
                syn,
                ent,
                genepanel_folder_ent.id,
                setProvnance=None,
                updateExisting=True,
                skipCopyAnnotations=True,
            )
    # Remove gene panels
    for name in genepanel_map:
        if name not in synid_map:
            print("Removing: {}({})".format(name, genepanel_map[name]))
            syn.delete(genepanel_map[name])

    new_caselists = syn.getChildren(synid_map["case_lists"])
    new_caselist_map = {case["name"]: case["id"] for case in new_caselists}
    # Copy case lists
    for name in new_caselist_map:
        ent = syn.get(new_caselist_map[name], followLink=True, downloadFile=False)
        synu.copy(
            syn,
            ent,
            caselist_folder_ent.id,
            setProvnance=None,
            updateExisting=True,
            skipCopyAnnotations=True,
        )

    # Remove case lists
    for name in caselist_map:
        if name not in new_caselist_map:
            print("Removing: {}({})".format(name, caselist_map[name]))
            syn.delete(caselist_map[name])

    # Copy rest of the files
    for name in synid_map:
        # Do not copy over files with these patterns
        # exclude = name.startswith(("data_gene_panel_", "data_clinical.txt",
        #                            "case_lists")) or name.endswith(".html")
        if not name.startswith(("data_gene_panel_", "data_clinical.txt", "case_lists")):
            ent = syn.get(synid_map[name], followLink=True, downloadFile=False)
            synu.copy(
                syn,
                ent,
                bpc_folder_ent.id,
                setProvnance=None,
                updateExisting=True,
                skipCopyAnnotations=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consortium to BPC")
    parser.add_argument(
        "release", type=str, metavar="8.2-consortium", help="GENIE release version"
    )
    parser.add_argument("--test", action="store_true", help="Testing")
    args = parser.parse_args()
    main(args.release, args.test)
