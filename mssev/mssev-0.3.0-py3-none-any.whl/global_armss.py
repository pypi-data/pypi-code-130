from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_timedelta64_dtype


datadir = Path(__file__).parent / 'data'

GLOBAL_ARMSS_TABLE_FILES = {
    'original': datadir / 'Original-ARMSS.tsv',
}


def _load_armss_table(path):
    df = pd.read_csv(path, sep='\t')
    df = df.rename(columns=lambda x: x.replace('EDSS', 'ARMSS'))
    df = pd.wide_to_long(df, 'ARMSS', i='Age', j='EDSS', sep='.', suffix=r'\d\.\d')
    df.ARMSS = df.ARMSS.astype('Float32')
    return df


def global_armss(df, table='original', edss='edss', age='ageatedss'):
    if isinstance(table, str) and table in GLOBAL_ARMSS_TABLE_FILES:
        table = _load_armss_table(GLOBAL_ARMSS_TABLE_FILES.get(table))

    df = df[[edss, age]].copy()
    if is_timedelta64_dtype(df[age]):
        df[age] = df[age].dt.days / 365.25
    df[age] = np.floor(df[age]).clip(upper=75).astype('Int32')
    results = df.merge(table, left_on=[age, edss], right_index=True, how='left')
    return results.ARMSS
