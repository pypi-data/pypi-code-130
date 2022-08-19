import pandas as pd
import re


def custompivot(in_info):
    """Summarize series or dataframe. Returns count and percent distribution

    Args:
        in_info (Series or DataFrame): [description]

    Returns:
        [type]: [description]
    """
    if type(in_info) == pd.core.series.Series:
        if (type(in_info.iloc[0]) == int or type(in_info.iloc[0]) == float) and len(in_info.index) > 10:
            counts = in_info.value_counts(dropna=False, bins=10)
        else:
            counts = in_info.value_counts(dropna=False)
    elif type(in_info) == pd.core.frame.DataFrame:
        counts = in_info.groupby(list(in_info.columns)).size()
    else:
        counts = 0
    percent = counts / counts.sum()
    fmt = '{:.2%}'.format
    output = pd.DataFrame({'counts': counts, 'percent': percent.map(fmt)})
    return output


def check_column(df, col, bins=4):
    """Provides some metrics and distribution info with the column provided

    Args:
        df (Pandas Dataframe): Input pandas dataframe
        col (str): Dataframe column name that should be analyzed
        bins (int): Number of bins to calculate column distribution. Defaults to 4 bins.

    Returns:
        dict: column length, null value count, duplicate value count, word count distribution (if column contains mostly strings), numeric distribution (if column contains mostly numeric data), and the first 3 values
    """
    len_df = len(df.index)
    not_null_column = [str(x) for x in list(df[col]) if str(x).lower() != 'nan']
    not_null_count = len(not_null_column)
    duplicate_values = df[col].duplicated().any()
    unique_values_count = df[col].nunique()
    null_values_count = df[col].isna().sum()
    outdict = {
        'column_header_name': col,
        'len_df': len_df,
        'null_values_count': null_values_count,
        'null_values_percent': round(null_values_count / len_df * 100, 2),
        'not_null_values_count': not_null_count,
        'duplicate_values_bool': duplicate_values,
        'unique_values_count': unique_values_count,
    }
    try:
        if pd.api.types.is_string_dtype(df[col]):
            df['__word_count'] = df[col].apply(lambda x: len(re.findall(r'\w+', x)) if pd.notna(x) else 0)
            distro_count = pd.Series(pd.cut(df['__word_count'], bins=bins, precision=0)).value_counts().to_frame().reset_index()
            distro_col_name = 'word_count_distribution_percent'
            col_type = 'string'
        elif pd.api.types.is_numeric_dtype(df[col]):
            distro_count = pd.Series(pd.cut(df[col], bins=bins, precision=0)).value_counts().to_frame().reset_index()
            distro_col_name = 'count_distribution_percent'
            col_type = 'numeric'
        else:
            pass
        distro_count.rename(columns={'index': 'range'}, inplace=True)
        distro_count['range'] = distro_count['range'].astype(str)
        distro_count = distro_count.to_dict('records')
        for d in distro_count:
            if col_type == 'string':
                d['__word_count'] = round(d['__word_count'] / len_df * 100, 2)
            else:
                d[col] = round(d[col] / len_df * 100, 2)
        outdict.update({distro_col_name: distro_count})
    except:
        pass

    try:
        outdict.update({'first_3_values': '|'.join(not_null_column[:3])})
    except:
        pass
    return outdict


def df_check_columns(df):
    result = []
    for col in df.columns:
        result.append(check_column(df, col))
    result_df = pd.DataFrame(result)
    return result_df
