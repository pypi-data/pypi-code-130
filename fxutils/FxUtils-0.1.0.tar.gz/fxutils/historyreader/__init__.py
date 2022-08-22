"""

This package contains various functions for reading trade history from different sources.
The main wrapper class `HistoryReader` unifies the input and output.

"""

from .reader import HistoryReader
from .mql5 import read_mql5
from .backtest_report import read_btreport
from .myfxbook import read_myfxbook

