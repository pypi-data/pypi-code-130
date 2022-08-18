from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_timedelta64_dtype


datadir = Path(__file__).parent / 'data'

GLOBAL_MSSS_TABLE_FILES = {
    'original': datadir / 'Original-MSSS.tsv',
    'updated': datadir / 'Updated-MSSS.tsv',
}


def _load_msss_table(path):
    df = pd.read_csv(path, sep='\t')
    df = df.rename(columns={'dd': 'Duration'})
    df.Duration = df.Duration.str.replace('dd', '').astype('Int32')
    df = df.rename(columns=lambda x: x.replace('EDSS', 'MSSS'))
    df = pd.wide_to_long(df, 'MSSS', i='Duration', j='EDSS', sep='.', suffix=r'\d\.\d')
    df.MSSS = df.MSSS.astype('Float32')
    return df


def global_msss(df, table='original', edss='edss', duration='dd'):
    if isinstance(table, str) and table in GLOBAL_MSSS_TABLE_FILES:
        table = _load_msss_table(GLOBAL_MSSS_TABLE_FILES.get(table))

    df = df[[duration, edss]].copy()
    if is_timedelta64_dtype(df[duration]):
        df[duration] = df[duration].dt.days / 365.25
    df[duration] = np.floor(df[duration]).clip(upper=30).astype('Int32')
    results = df.merge(table, left_on=[duration, edss], right_index=True, how='left')
    return results.MSSS
