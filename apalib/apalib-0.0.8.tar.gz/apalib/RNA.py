# global FULL_NAME
# global ONE_LETTER
from apalib.Data import data as data
global FLAGS
FLAGS = {}

#-w
#
class RNA:
    def __init__(self, seqNum=None, atoms=None, resName=None, set_name=True, chainID=None):
        self.SetResName(resName, set_name)
        self.SetSeqNum(seqNum)
        self.SetAtoms(atoms)
        self.SetChainID(chainID)

    def DeepCopy(self):
        return RNA(seqNum=self.seqNum,
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
        print("RNA CENTROID")

    def InsertAtom(self, atom):
        if self.atoms is None:
            self.atoms = list()
        self.atoms.append(atom)

    def SetResName(self, name, set_name):
        if not set_name:
            self.resName = name
            self.RaiseFlag('NO_NAME_CHECK')
            self.ClearFlag('BAD_NAME')
            return
        else:
            self.ClearFlag('NO_NAME_CHECK')
        global ONE_LETTER
        if data.ValidateRNA(name):
            self.resName = data.SetRNAName(name)
        # elif name in FULL_NAME:
        #     self.name = FULL_NAME[name]
        # else:
        #     self.RaiseFlag('BAD_NAME')
        #     return
        self.ClearFlag('BAD_NAME')
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
global FULL_NAME
FULL_NAME = {
    'ADENINE': 'A',
    'CYTOSINE': 'C',
    'GUANINE': 'G',
    'THYMINE': 'T',
    'URACIL': 'U',
    'INOSINE': 'I'
}
