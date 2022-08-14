def preprocess_data(df):
    """
                     Data Science Library
     method name: preprocess_data
     desc: Here my main aim is to convert the cat into con and merge into the standardized data
     author name: TinCharlie
    :param df: Data Frame
    :return: It will return the processed columns of the Cat and COn Standardized
    """

    import pandas as pd
    cat = []
    con = []
    for i in df.columns:
        if df[i].dtypes == "object":
            cat.append(i)
        else:
            con.append(i)
    X1 = pd.get_dummies(df[cat])
    from sklearn.preprocessing import StandardScaler
    ss = StandardScaler()
    X2 = pd.DataFrame(ss.fit_transform(df[con]), columns=con)
    X3 = X2.join(X1)
    return X3