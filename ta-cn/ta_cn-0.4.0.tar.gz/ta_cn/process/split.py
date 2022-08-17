import numpy as np
import pandas as pd
from pandas.core.arrays.categorical import factorize_from_iterables


def array2d_split(shape, section=1, axis=0, offset=-20):
    """2维array水平切分或垂直切分。每组数量基本接近，最多差1个

    Parameters
    ----------
    shape: tuple
        数据形状
    section: int
        切分成几块
    axis: int
        切块方向
            0-切成N行。用于横截面计算。
            1-切成N列。用于时序计算。
        单元格计算时，有以下考虑方向：
            1. 数据量大时，按axis=0切更好，因为axis=1的切分方式需要将文件全加载到内存才切片
            2. 数据量少时，建议以for循环次数少为优先。
                - 例如5000支股票一年日线，按天切更优，即axis=0合适
                - 例如5000支股票一年一分钟，按股票切更优，即axis=0合适
    offset: int
        预加载数据偏移量，一般取0或负数。用于时序计算时额外加载计算数据


    Returns
    -------
    slc_curr: slice
        切片
    slc_pre: slice
        多加载所需切片

    Examples
    --------
    >>> arr = np.random.randint(0, 10, [30, 4])
    >>> g = array2d_split(arr.shape, 4, axis=0)
    >>> for _ in g:
    >>>     print(arr[_]) # (slice(8, 16, None), slice(None, None, None))

    """
    curr = [slice(None)] * len(shape)
    pre = curr[:]
    n = shape[axis]
    if n == 0:
        return tuple(curr), tuple(pre)
    section = max(min(n, section), 1)

    # 取位置信息
    arr = np.array_split(np.arange(n), section, axis=0)
    p = [_[0] for _ in arr] + [n]  # 加上哨兵

    for start, end in zip(p[:-1], p[1:]):
        curr[axis] = slice(start, end)  # tuple(0,25)
        pre[axis] = slice(max(start + offset, 0), end)
        yield tuple(curr), tuple(pre)


def array1d_groupby_sorted(by):
    """对提前排好序的一维数组进行分组，得到slice。

    Parameters
    ----------
    by:
        分组信息

    Returns
    -------
    slice迭代

    Notes
    -----
    传slice信息，要求分组信息要提前排好序，否则切片混乱

    Examples
    --------
    >>> df = pd.DataFrame({'A': range(100)})
    >>> df['B'] = df['A'] // 10
    >>> df['C'] = df['A'] // 5
    >>> df['D'] = df['A'] % 4

    >>> g = array1d_groupby_sorted(df[['B', 'C']])
    >>> for _ in g:
    >>>     print(df[_])

    """
    # 通过by得到codes
    if isinstance(by, pd.MultiIndex):
        codes, levels = by.codes, by.levels
    elif isinstance(by, pd.Index):
        codes, levels = factorize_from_iterables([by])
    elif isinstance(by, np.ndarray):
        codes, levels = factorize_from_iterables(by.T)
    elif isinstance(by, pd.DataFrame):
        codes, levels = factorize_from_iterables(by.to_dict(orient='list').values())

    # 核心
    codes = np.array(codes)
    flag = np.diff(codes, axis=1).astype(bool).any(axis=0)
    p = np.where(np.concatenate(([True], flag, [True])))[0]

    for _ in zip(p[:-1], p[1:]):
        yield slice(*_)


def array1d_groupby_unsorted(by):
    """1维数组分组，未排序。全加载，然后比较其实也很慢

    Parameters
    ----------
    by:
        分组信息

    Returns
    -------
    tuple(ndarray,)迭代

    """
    if isinstance(by, (pd.DataFrame, pd.Series)):
        arr = by.values
    elif isinstance(by, pd.Index):
        arr = pd.DataFrame(index=by).reset_index().values
    elif isinstance(by, np.ndarray):
        arr = by

    # 得到唯一值
    u = np.unique(arr, axis=0)
    for r in u:
        if arr.ndim == 1:
            yield np.where(arr == r)
        if arr.ndim == 2:
            yield np.where((arr == r).all(axis=1))
