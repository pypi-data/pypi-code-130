from xml.etree.ElementTree import VERSION
from briefstats.bstats import des
from briefstats.bstats import mode
from briefstats.bstats import low25
from briefstats.bstats import up75
from briefstats.bstats import ran
from briefstats.bstats import iqr
from briefstats.bstats import diff_mode_rate
from briefstats.bstats import mae
from briefstats.bstats import varia
from briefstats.bstats import skew
from briefstats.bstats import kurt

name = 'briefstats'

__version__ = '0.0.3'
__description__ = 'A brief statistics tool for Chinese.'
__author__ = 'Kang Zhou'
__author_email__ = 'zkSpongeBob@126.com'
VERSION = __version__

__all__ = [
    'des', 
    'mode', 
    'low25',
    'up75',
    'ran',
    'iqr',
    'diff_mode_rate',
    'mae',
    'varia',
    'skew',
    'kurt'
]