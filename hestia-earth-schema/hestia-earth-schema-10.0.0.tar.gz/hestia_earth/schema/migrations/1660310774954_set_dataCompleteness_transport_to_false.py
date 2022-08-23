import pandas as pd


def migrate(df: pd.DataFrame):
    # migrate data
    # migrate only if cycle.dataCompleteness is specified in upload
    if 'cycle.dataCompleteness' in df.columns:
        df['cycle.dataCompleteness.transport'] = 'false'

    # make sure to return the DataFrame so it can be uploaded
    return df
