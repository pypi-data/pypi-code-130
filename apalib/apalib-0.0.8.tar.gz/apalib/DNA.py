# global ONE_LETTER
# global TWO_LETTER
# global FULL_NAME
from apalib.Data import data as data
global FLAGS
FLAGS = {}


class DNA:
    def __init__(self, seqNum=None, atoms=None, resName=None, set_name=True, chainID=None):
        # self.seqNum = number
        # self.atoms = atoms
        # self.resName = name
        self.SetResName(resName, set_name)
        self.SetSeqNum(seqNum)
        self.SetAtoms(atoms)
        self.SetChainID(chainID)

    def DeepCopy(self):
        return DNA(seqNum=self.seqNum,
                   atoms=self.atoms,
                   resName=self.resName,
                   set_name=True)

    def AddAttribute(self, attr, var):
        self.__dict__[attr] = var

    def SetSeqNum(self, num):
        self.seqNum = num

    def SetAtoms(self, atoms):
        self.atoms = atoms
        self.CalculateCentroid(atoms)

    def GetAtoms(self):
        return self.atoms

    def CalculateCentroid(self, atoms):
        print("DNA PRESENT! FILL THIS STUB")

    def InsertAtom(self, atom):
        if self.atoms is None:
            self.atoms = list()
        self.atoms.append(atom)

    def SetResName(self, name, set_name):
        if not set_name:
            self.resName = name
            self.RaiseFlag('NO_NAME_CHECK')
            return
        else:
            self.CheckFlag('NO_NAME_CHECK')
        if data.ValidateDNA(name):
            self.resName = data.SetDNAName(name)
        # elif name in self.FULL_NAME:
        #     self.resName = self.FULL_NAME[name]
        # elif name in self.ONE_LETTER:
        #     self.resName = 'D' + name
        else:
            self.resName = None
            self.RaiseFlag('BAD_NAME')
            return
        self.CheckFlag('BAD_NAME')
        return

    def GetResName(self):
        return self.resName

    def SetChainID(self, c):
        self.chainID = c

    def WriteForPDB(self):
        retstr = ""
        for atom in self.atoms:
            retstr += atom.WritePDB(intro="ATOM  ")
        return retstr


    @staticmethod
    def CheckFlag(f):
        global FLAGS
        if f in FLAGS:
            return FLAGS[f]
        return False

    @staticmethod
    def RaiseFlag(flag):
        global FLAGS
        FLAGS[flag] = True

    @staticmethod
    def ClearFlag(flag):
        global FLAGS
        FLAGS[flag] = False

    def __lt__(self, other):
        return self.seqNum < other.number

    def __repr__(self):
        return f"RESIDUE: {self.resName}, NUMBER: {self.seqNum}"

    def __str__(self):
        return f"{self.resName} {self.seqNum}"


global ONE_LETTER
ONE_LETTER = {
    'A': 'ADENINE',
    'C': 'CYTOSINE',
    'G': 'GUANINE',
    'T': 'THYMINE',
    'U': 'URACIL',
    'I': 'INOSINE'
}
global TWO_LETTER
TWO_LETTER = {
    'DA': 'ADENINE',
    'DC': 'CYTOSINE',
    'DG': 'GUANINE',
    'DT': 'THYMINE',
    'DU': 'URACIL',
    'DI': 'INOSINE'
}
global FULL_NAME
FULL_NAME = {
    'ADENINE': 'DA',
    'CYTOSINE': 'DC',
    'GUANINE': 'DG',
    'THYMINE': 'DT',
    'URACIL': 'DU',
    'INOSINE': 'DI'
}
