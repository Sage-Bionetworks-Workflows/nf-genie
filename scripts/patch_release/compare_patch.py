"""
The command ran: 
python patch.py syn53170398 syn62069187 syn54082015
In leu of lack of unit or integration tests, the above command replicates the 
this is to test 15.5-consortium (syn55146141) and 15.6-consortium (Staging syn62069187)

python compare_patch.py --original_synid syn55146141 --new_synid syn62069187
"""
import argparse

import synapseclient
import synapseutils as synu


def _get_file_dict(syn: synapseclient.Synapse, synid: str) -> dict[str, str]:
    """
    This function generates a dictionary of files from a Synapse ID.

    Args:
        syn (synapseclient.Synapse): A Synapse client object.
        synid (str): The Synapse ID of the files to retrieve.

    Returns:
        dict[str, str]: A dictionary mapping Synapse IDs to file names.
    """
    all_files = synu.walk(syn, synid)
    file_list = {}
    for _, _, files in all_files:
        files = {name: syn.get(synid, downloadFile=False) for name, synid in files}
        file_list.update(files)
    return file_list


def compare_releases(original_synid: str, new_synid: str):
    """
    This function compares two folders that should have identifical files
    with each file's MD5s

    Args:
        original_synid (str): The Synapse ID of the original release.
        new_synid (str): The Synapse ID of the new release.

    Returns:
        tuple: A tuple containing the original release entity, the new release entity,
        and a list of retracted entities.
    """

    # Log in to Synapse
    syn = synapseclient.login()

    # Get the entities for the original and new releases
    # original_ent = syn.get(original_synid)
    # original_files = synu.walk(original_synid)
    original_file_list = _get_file_dict(syn, original_synid)
    # new_ent = syn.get(new_synid)
    # new_files = synu.walk(new_synid)
    new_file_list = _get_file_dict(syn, new_synid)

    # Check that the two folders have the same number of files
    print("Number of files in old folder: ", len(original_file_list))
    print("Number of files in new folder: ", len(new_file_list))
    for filename in new_file_list.keys():
        if original_file_list.get(filename) is None:
            print("File not found in old folder: ", filename)

    for filename in original_file_list.keys():
        if new_file_list.get(filename) is None:
            print("File not found in new folder: ", filename)
        else:
            if original_file_list[filename].md5 != new_file_list[filename].md5:
                print("Files are different: ", filename)

def main():
    parser = argparse.ArgumentParser(description='Compare two Synapse releases.')
    parser.add_argument('--original_synid', type=str, help='The Synapse ID of the original release')
    parser.add_argument('--new_synid', type=str, help='The Synapse ID of the new release')

    args = parser.parse_args()

    compare_releases(args.original_synid, args.new_synid)

if __name__ == "__main__":
    main()
