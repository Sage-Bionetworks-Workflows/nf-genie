"""
Check if samples from the BPC need to be retracted by
comparing the main GENIE sample database against the
BPC clinical database
"""
import synapseclient

EMAIL_SUBJECT = "Review GENIE Retractions for BPC"

EMAIL_BODY = """
Dear Genie Team,

There are retractions in the most recent upload for main GENIE that may impact GENIE BPC data. Please review the retracted records.

{}

Best,

Sage Team
"""


def main():
    """Main function"""
    syn = synapseclient.login()

    # Pull table with full redcap clinical export
    bpc_samples = syn.tableQuery(
        "SELECT cpt_genie_sample_id FROM syn23285889 where cpt_genie_sample_id is not null"
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
        print(retract_from_bpc.unique())
        # Tom 3324230
        # Chelsea 3452608
        # Xindi 3334658
        # Mike 3423837
        # Jocelyn 3360218
        # Email users
        syn.sendMessage(
            userIds=[3324230, 3452608, 3334658, 3423837, 3360218],
            messageSubject=EMAIL_SUBJECT,
            messageBody=EMAIL_BODY.format(", ".join(retract_from_bpc.unique()))
        )


if __name__ == "__main__":
    main()
