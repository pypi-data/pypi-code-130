"""Pandas tools."""
import pandas as pd


def freq(values):
    """Compute value frequencies.

    Given a collection of values, calculate for each value:
     - the frequency (``n``),
     - the cumulative frequency (``N``),
     - the relative frequency (``r``), and
     - the cumulative relative frequency (``R``).

    Parameters
    ----------
    values : array_like
        Collection of values to evaluate.

    Returns
    -------
    pandas.DataFrame
        Frequencies of each distinct value.

    Examples
    --------
    >>> import pandas as pd
    >>> x = ["a", "c", "b", "g", "h", "a", "g", "a"]
    >>> frequency = freq(x)
    >>> isinstance(frequency, pd.DataFrame)
    True
    >>> frequency
       n  N      r      R
    a  3  3  0.375  0.375
    g  2  5  0.250  0.625
    c  1  6  0.125  0.750
    b  1  7  0.125  0.875
    h  1  8  0.125  1.000
    """
    s = pd.Series(values).value_counts(
        sort=True,
        ascending=False,
        bins=None,
        dropna=False,
    )

    df = pd.DataFrame(s, columns=["n"])
    df["N"] = df["n"].cumsum()
    df["r"] = df["n"] / df["n"].sum()
    df["R"] = df["r"].cumsum()

    return df
