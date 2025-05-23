"""Most current consortium release cBioPortal files to BPC Synapse Project
Consortium releases to internal BPC page"""

import argparse
from typing import Dict

import synapseclient
from synapseclient import Folder, Project, File, Link, Schema, Entity
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


def _copyRecursive(
    syn: synapseclient.Synapse,
    entity: str,
    destinationId: str,
    mapping: Dict[str, str] = None,
    skipCopyAnnotations: bool = False,
    **kwargs,
) -> Dict[str, str]:
    """
    NOTE: This is a copy of the function found here: https://github.com/Sage-Bionetworks/synapsePythonClient/blob/develop/synapseutils/copy_functions.py#L409
    This was copied because there is a restriction that doesn't allow for copying entities with access requirements

    Recursively copies synapse entites, but does not copy the wikis

    Arguments:
        syn: A Synapse object with user's login
        entity: A synapse entity ID
        destinationId: Synapse ID of a folder/project that the copied entity is being copied to
        mapping: A mapping of the old entities to the new entities
        skipCopyAnnotations: Skips copying the annotations
                                Default is False

    Returns:
        a mapping between the original and copied entity: {'syn1234':'syn33455'}
    """

    version = kwargs.get("version", None)
    setProvenance = kwargs.get("setProvenance", "traceback")
    excludeTypes = kwargs.get("excludeTypes", [])
    updateExisting = kwargs.get("updateExisting", False)
    if mapping is None:
        mapping = dict()
    # Check that passed in excludeTypes is file, table, and link
    if not isinstance(excludeTypes, list):
        raise ValueError("Excluded types must be a list")
    elif not all([i in ["file", "link", "table"] for i in excludeTypes]):
        raise ValueError(
            "Excluded types can only be a list of these values: file, table, and link"
        )

    ent = syn.get(entity, downloadFile=False)
    if ent.id == destinationId:
        raise ValueError("destinationId cannot be the same as entity id")

    if (isinstance(ent, Project) or isinstance(ent, Folder)) and version is not None:
        raise ValueError("Cannot specify version when copying a project of folder")

    if not isinstance(ent, (Project, Folder, File, Link, Schema, Entity)):
        raise ValueError("Not able to copy this type of file")

    permissions = syn.restGET("/entity/{}/permissions".format(ent.id))
    # Don't copy entities without DOWNLOAD permissions
    if not permissions["canDownload"]:
        syn.logger.warning(
            "%s not copied - this file lacks download permission" % ent.id
        )
        return mapping

    # HACK: These lines of code were removed to allow for data with access requirements to be copied
    # https://github.com/Sage-Bionetworks/synapsePythonClient/blob/2909fa778e814f62f6fe6ce2d951ce58c0080a4e/synapseutils/copy_functions.py#L464-L470

    copiedId = None

    if isinstance(ent, Project):
        project = syn.get(destinationId)
        if not isinstance(project, Project):
            raise ValueError(
                "You must give a destinationId of a new project to copy projects"
            )
        copiedId = destinationId
        # Projects include Docker repos, and Docker repos cannot be copied
        # with the Synapse rest API. Entity views currently also aren't
        # supported
        entities = syn.getChildren(
            entity, includeTypes=["folder", "file", "table", "link"]
        )
        for i in entities:
            mapping = _copyRecursive(
                syn,
                i["id"],
                destinationId,
                mapping=mapping,
                skipCopyAnnotations=skipCopyAnnotations,
                **kwargs,
            )

        if not skipCopyAnnotations:
            project.annotations = ent.annotations
            syn.store(project)
    elif isinstance(ent, Folder):
        copiedId = synu.copy_functions._copyFolder(
            syn,
            ent.id,
            destinationId,
            mapping=mapping,
            skipCopyAnnotations=skipCopyAnnotations,
            **kwargs,
        )
    elif isinstance(ent, File) and "file" not in excludeTypes:
        copiedId = synu.copy_functions._copyFile(
            syn,
            ent.id,
            destinationId,
            version=version,
            updateExisting=updateExisting,
            setProvenance=setProvenance,
            skipCopyAnnotations=skipCopyAnnotations,
        )
    elif isinstance(ent, Link) and "link" not in excludeTypes:
        copiedId = synu.copy_functions._copyLink(
            syn, ent.id, destinationId, updateExisting=updateExisting
        )
    elif isinstance(ent, Schema) and "table" not in excludeTypes:
        copiedId = synu.copy_functions._copyTable(
            syn, ent.id, destinationId, updateExisting=updateExisting
        )
    # This is currently done because copyLink returns None sometimes
    if copiedId is not None:
        mapping[ent.id] = copiedId
        syn.logger.info("Copied %s to %s" % (ent.id, copiedId))
    else:
        syn.logger.info("%s not copied" % ent.id)
    return mapping


def main(release: str, test: bool) -> None:
    """Updated BPC project
    Args:
        release (str): name of the release
        test (bool): testing or not
    """
    # if release.endswith("1-consortium"):
    #     raise ValueError("First consortium release are not released")

    syn = synapseclient.login()

    ent_synids = get_release_synids(test)

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

    #HACK: Copy functions from synapseutils won't work because files have access restrictions
    synu.copy_functions._copyRecursive = _copyRecursive

    # Copy gene panel files
    for name in synid_map:
        if name.startswith("data_gene_panel_"):
            ent = syn.get(synid_map[name], followLink=True, downloadFile=False)
            synu.copy(
                syn,
                ent,
                genepanel_folder_ent.id,
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
