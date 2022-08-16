#!/usr/bin/env python3

from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_timedelta64_dtype


def _load_global_msss_table(path):
    df = pd.read_csv(path, sep='\t')
    df = df.rename(columns={'dd': 'Duration'})
    df.Duration = df.Duration.str.replace('dd', '').astype('Int32')
    df = df.rename(columns=lambda x: x.replace('EDSS', 'MSSS'))
    df = pd.wide_to_long(df, 'MSSS', i='Duration', j='EDSS', sep='.', suffix=r'\d\.\d')
    df.MSSS = df.MSSS.astype('Float32')
    return df


def _load_global_armss_table(path):
    df = pd.read_csv(path, sep='\t')
    df = df.rename(columns=lambda x: x.replace('EDSS', 'ARMSS'))
    df = pd.wide_to_long(df, 'ARMSS', i='Age', j='EDSS', sep='.', suffix=r'\d\.\d')
    df.ARMSS = df.ARMSS.astype('Float32')
    return df


GLOBAL_MSSS = None
GLOBAL_ARMSS = None


def global_msss(df, edss='edss', duration='dd'):
    global GLOBAL_MSSS
    if GLOBAL_MSSS is None:
        path = Path(__file__).parent / 'Global-MSSS.tsv'
        GLOBAL_MSSS = _load_global_msss_table(path)

    df = df[[duration, edss]].copy()
    if is_timedelta64_dtype(df[duration]):
        df[duration] = df[duration].dt.days / 365.25
    df[duration] = np.floor(df[duration]).clip(upper=30).astype('Int32')
    results = df.merge(GLOBAL_MSSS, left_on=[duration, edss], right_index=True, how='left')
    return results.MSSS


def global_armss(df, edss='edss', age='ageataedss'):
    global GLOBAL_ARMSS
    if GLOBAL_ARMSS is None:
        path = Path(__file__).parent / 'Global-ARMSS.tsv'
        GLOBAL_ARMSS = _load_global_armss_table(path)

    df = df[[edss, age]].copy()
    if is_timedelta64_dtype(df[age]):
        df[age] = df[age].dt.days / 365.25
    df[age] = np.floor(df[age]).clip(upper=75).astype('Int32')
    results = df.merge(GLOBAL_ARMSS, left_on=[age, edss], right_index=True, how='left')
    return results.ARMSS
