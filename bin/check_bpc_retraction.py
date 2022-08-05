"""
Check if samples from the BPC need to be retracted by
comparing the retraction list from the first three consortium releases
after each public release.
"""
import synapseclient


def main():
    syn = synapseclient.login()

    # Pull table with full redcap clinical export
    bpc_samples = syn.tableQuery(
        "SELECT cpt_genie_sample_id FROM syn23285889"
    )
    bpc_samples_df = bpc_samples.asDataFrame()

    # Main GENIE clinical database
    sample_db = syn.tableQuery("select SAMPLE_ID from syn7517674")
    sample_df = sample_db.asDataFrame()

    # Retract these samples from BPC samples
    retract_idx = ~bpc_samples_df['cpt_genie_sample_id'].isin(
        sample_df['SAMPLE_ID']
    )
    retract_from_bpc = bpc_samples_df['cpt_genie_sample_id'][retract_idx]
    if retract_from_bpc.any():
        print(retract_from_bpc)


if __name__ == "__main__":
    main()
