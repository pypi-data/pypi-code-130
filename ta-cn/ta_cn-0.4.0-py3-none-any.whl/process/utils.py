"""
文件分组处理相关
"""
import os
import pathlib
from typing import Union, List

import pandas as pd
from loguru import logger


def load_parquet(path: Union[str, pathlib.Path], pattern: Union[str, List[str]]):
    """加载多个parquet文件

    Parameters
    ----------
    path: str
        目录
    pattern: str or list
        模式。如果是列表，将依次加载合并

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> load_parquet(path, f'{year}*')

    """
    if isinstance(pattern, str):
        # 一个过滤条件时，拼接一组
        return pd.concat([pd.read_parquet(_) for _ in pathlib.Path(path).glob(pattern)])
    if isinstance(pattern, list):
        # 多个过滤条件时，拼接多组
        return pd.concat([load_parquet(path, _) for _ in pattern])


def merge_parquet(left, right, how='left', **merge_kwargs):
    """

    Parameters
    ----------
    left: tuple
        path, pattern
    right: tuple
        path, pattern
    how: str
        合并方案
    merge_kwargs:
        pd.merge的参数

    Returns
    -------

    """
    l_ = load_parquet(*left)
    r_ = load_parquet(*right)
    return pd.merge(l_, r_, how=how, **merge_kwargs)


def _dataframe_make_key(df: pd.DataFrame, key='asset'):
    """创建股票分组，此为参考示例，实际使用需重新实现
    """
    # 过滤停牌。计算技术指标和和横截面时会剔除停牌，但计算板块和指数时，停牌也参与计算
    # JoinQuant中行情默认停牌也有记录，标记成停牌
    # TuShare没有停牌日的行情，只能通过unstack还原数据后再fillna
    df = df[df['paused'] == 0]  # .copy()
    df = df[~df[key].str.endswith('.BJ')]  # .copy()
    # [5: 6]一位用来当关键字，数据量大就用两位[4:6]
    df['key'] = df[key].str[5:6]
    return df


def split_by_symbol(df: pd.DataFrame, date: str, output: Union[str, pathlib.Path],
                    set_index_keys=['asset', 'date'], group_by=['key'], drop_columns=['key']):
    """按股票代码生成的关键字进行时序方向分割

    1. 直接按股票代码直接分割会因为产生的文件太多，反而处理慢
    2. 复合索引占空间，多一些字段才划算

    Parameters
    ----------
    df: pd.DataFrame
    date: str
        划分的起始日期
    output:str
        输出路径
    set_index_keys: list
        设置成索引的列。先合约代码后时间
    group_by: list
        分组列
    drop_columns: list
        放弃列

    Examples
    --------
    >>> split_by_symbol(df, year, output, set_index_keys=['code', 'time'], group_by=['key'], drop_columns=['key'])
    >>> split_by_symbol(df, year, output, set_index_keys=['ts_code', 'trade_date'], group_by=['key'], drop_columns=['key', 'change', 'pct_chg'])

    """
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)

    df = df.set_index(set_index_keys).sort_index()
    grouped = df.groupby(by=group_by)
    for key, group in grouped:
        logger.info('pid:{}, key:{}, date:{}', os.getpid(), key, date)
        # 删除没必要保存的字段
        group.drop(columns=drop_columns, inplace=True)
        group.to_parquet(output / f'{key}__{date}.parquet', compression='gzip')


def split_by_column(df: pd.DataFrame, date: str, output: Union[str, pathlib.Path],
                    set_index_keys=['date', 'asset'], drop_columns=['change', 'pct_chg']):
    """按字段进行分割

    1. 二维，一个字段一个文件
    2. 如果上市有先后，会导致大量的空白区域，占空间
    3. 停牌导致数据中断，部分计算指标函数会错误

    Parameters
    ----------
    df: pd.DataFrame
    date: str
        划分的起始日期
    output: str
        输出路径
    set_index_keys: list
        设置成索引的列。先时间后合约代码
    drop_columns: list
        放弃列

    """
    # 设置复合索引
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)

    df = df.set_index(set_index_keys).sort_index()
    for col in df.columns:
        # 跳过没有必要保存的字段
        if col in drop_columns:
            continue
        logger.info('pid:{}, col:{}, date:{}', os.getpid(), col, date)
        # 转换保存
        d = df[col].unstack()
        d.to_parquet(output / f'{col}__{date}.parquet', compression='gzip')


def dataframe_calc(df: pd.DataFrame, groupbys: List[str], funcs: List):
    """dataframe计算模板

    Parameters
    ----------
    df: pd.DataFrame
        复合索引的数据
    groupbys: list
        处理方向，None表示不用groupby,直接处理
    funcs:
        不分组，直接处理。如一列与另一列的处理
        分组，组内进行计算，比如算指标，算排序等

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> df = dataframe_calc(df, [None, 'asset', 'date'], [func_all, func_ts, func_cs])

    """
    for g, f in zip(groupbys, funcs):
        if g is None:
            # 不分组
            df = f(df)
        else:
            # 注意分组方向
            df = df.groupby(by=g).apply(f)

    return df
