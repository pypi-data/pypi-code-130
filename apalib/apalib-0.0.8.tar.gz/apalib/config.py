from apalib.Container import Container as Container
# import apalib.Container
# from apalib.AminoAcid import AminoAcid
# from apalib.Atom import Atom
# from apalib.DNA import DNA
# from apalib.RNA import RNA
# from apalib.HETATM import HETATM
from apalib.Data import Data
Container = Container()
data = Data()


def ToStringLen(val, l, left_justify = True):
    if val is None:
        val = ''
    retstr = str(val)
    if len(retstr) < l and left_justify:
        return retstr + " " * (l - len(retstr))
    elif len(retstr) < l and not left_justify:
        return " " * (l - len(retstr)) + retstr
    else:
        return retstr