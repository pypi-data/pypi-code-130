def replace_mmr(df):
    """
    Data Science Library
    method name: Mean_mode_replacer
    desc: It replace the missing value by using of the mean and mode.
            We need the data which does contains to the known data
    author name: TinCharlie
    :param df: df stands for DataFrame
    :return: replace data nan or null values
    """
    try:
        import pandas as pd
        Q = pd.DataFrame(df.isna().sum(), columns=["ct"])
        ## ct is for just to give the name of missing columns head
        for i in Q[Q.ct > 0].index:
            if df[i].dtypes == "object":
                x = df[i].mode()[0]
                df[i] = df[i].fillna(x)
            else:
                x = df[i].mean()
                df[i] = df[i].fillna(x)
        return df
    except TypeError:
        print("Data Contains unknown data dtypes")
        return df
