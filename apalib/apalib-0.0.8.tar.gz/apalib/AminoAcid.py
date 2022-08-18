import sys
import apalib.config as config
global FLAGS
FLAGS = {}


class AminoAcid:
    def __init__(self, seqNum = None, atoms = None, resName = None, rotamer = None, vector = None, set_name = True,
                 heptad = None, centroid = None, chainID=None):
        self.rotamer = rotamer
        self.vector = vector
        self.heptad = heptad
        self.centroid = centroid
        self.SetResName(resName, set_name)
        self.SetSeqNum(seqNum)
        self.SetAtoms(atoms)
        self.SetChainID(chainID)

    def DeepCopy(self):
        return AminoAcid(number=self.seqNum,
                         atoms=self.atoms,
                         name=self.resName,
                         rotamer=self.rotamer,
                         vector=self.vector,
                         heptad=self.heptad,
                         centroid=self.centroid,
                         chainID=self.chainID,
                         set_name=True)

    def AddAttribute(self, attr, var):
        self.__dict__[attr] = var

    def SetSeqNum(self, num):
        self.seqNum = num

    def SetAtoms(self, atoms):
        self.atoms = atoms
        # self.CalculateCentroid()

    def InsertAtom(self, atom):
        if self.atoms is None:
            self.atoms = list()
        self.atoms.append(atom)

    def GetAtoms(self):
        return self.atoms

    def GetRotamers(self, **kwargs):
        accepted = ['unique']
        for key in kwargs.keys():
            if key not in accepted:
                raise apalib.apalibExceptions.BadKwarg(accepted)

        if self.rotamer is not None:
            return self.rotamer

        if 'unique' in kwargs.keys() and isinstance(kwargs['unique'], (bool)):
            unique = kwargs['unique']
        else:
            unique = False

        retDict = {'Common':[]}
        if self.atoms is not None:
            for atom in self.atoms:
                if atom.rotation is None or atom.rotation == '':
                    retDict['Common'].append(atom)
                    continue
                if atom.rotation not in retDict.keys():
                    retDict[atom.rotation] = []
                retDict[atom.rotation].append(atom)
        if unique is False:
            for lst in [retDict[key] for key in retDict.keys() if key != 'Common']:
                lst += retDict['Common']
        return retDict

    def GetCA(self):
        if self.atoms is None:
            return None
        for atom in self.atoms:
            if atom.GetName() == 'CA':
                return atom
        return None

    def SetResName(self, name, set_name):
        if name is None:
            self.resName = name
            return
        if not set_name:
            self.resName = name
            self.RaiseFlag('NO_NAME_CHECK')
            return
        else:
            self.ClearFlag('NO_NAME_CHECK')
        if len(name) == 3 and name in THREE_LETTER:
            self.resName = name
        elif len(name) == 3 and name not in THREE_LETTER:
            self.resName = None
        elif len(name) == 1:
            self.resName = self.OneToThree(name)
        elif len(name) <= 4:
            if name[-3:] in THREE_LETTER:
                self.resName = name[-3:]
                self.rotamer = name[:-3]
            else:
                self.resName = None
        elif len(name) == 2:
            self.resName = None
        if self.resName is not None:
            self.RaiseFlag('BAD_NAME')
        else:
            self.RaiseFlag('BAD_NAME')
        if self.resName is not None and self.rotamer is not None:
            self.RaiseFlag('MARKED')
        elif self.resName is not None and self.rotamer is None:
            self.ClearFlag('MARKED')

    def SetHeptad(self, heptad):
        self.heptad = heptad

    def CalculateCentroid(self):
        if 'atoms' not in self.__dict__:
            self.centroid = None
            return
        #TODO switch to using the JSON for this
        # *For Glycine, only the alpha carbon is considered
        # *For Alanine, only the beta carbon is considered
        AAs = {
            "SER": ['OG'],
            "CYS": ['SG'],
            "SEC": ['SE'],
            "GLY": ['CA'],
            "ALA": ['CB'],
            "THR": ['OG1', 'CG2'],
            "PRO": ['CG', 'CD'],
            "VAL": ['CG1', 'CG2'],
            "ASP": ['CG', 'OD1', 'OD2'],
            "ASN": ['CG', 'OD1', 'ND2'],
            "ILE": ['CG1', 'CG2', 'CD1'],
            "LEU": ['CG', 'CD1', 'CD2'],
            "MET": ['CG', 'SD', 'CE'],
            "LYS": ['CG', 'CD', 'CE', 'NZ'],
            "GLU": ['CG', 'CD', 'OE1', 'OE2'],
            "GLN": ['CG', 'CD', 'OE1', 'NE2'],
            "HIS": ['CG', 'ND1', 'CD2', 'CE1', 'NE2'],
            "ARG": ['CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2'],
            "PHE": ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
            "TYR": ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH'],
            "TRP": ['CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2']
        }
        # TODO Deal with non-1 occupancy
        if len(self.resName) == 3 and self.resName in AAs:
            # If residue is not specified
            x_coord = 0
            y_coord = 0
            z_coord = 0
            num_atoms = 0
            for atom in [atom for atom in self.atoms if atom.name in AAs[self.resName]]:
                if atom.element == 'H':
                    continue
                x_coord += atom.GetCoordinates()[0]
                y_coord += atom.GetCoordinates()[1]
                z_coord += atom.GetCoordinates()[2]
                num_atoms += 1
            self.centroid = list()
            try:
                self.centroid.append(x_coord / num_atoms)
                self.centroid.append(y_coord / num_atoms)
                self.centroid.append(z_coord / num_atoms)
            except ZeroDivisionError:
                self.centroid.clear()
                beta = [atom for atom in self.atoms if atom.name == 'CB']
                alpha = [atom for atom in self.atoms if atom.name == 'CA']
                if len(beta) != 0:
                    self.centroid.append(beta[0].coordinates[0])
                    self.centroid.append(beta[0].coordinates[1])
                    self.centroid.append(beta[0].coordinates[2])
                    self.RaiseFlag('B_CENTROID')
                elif len(alpha) != 0:
                    self.centroid.append(alpha[0].coordinates[0])
                    self.centroid.append(alpha[0].coordinates[1])
                    self.centroid.append(alpha[0].coordinates[2])
                    self.RaiseFlag('A_CENTROID')
                else:
                    self.centroid = None
                    self.vector = None
                    self.RaiseFlag('BAD_CENTROID')
                    return
            # After all that, set the centroidal vector
            self.vector = [self.centroid[0] - self.GetCA().GetCoordinates()[0],
                           self.centroid[1] - self.GetCA().GetCoordinates()[1],
                           self.centroid[2] - self.GetCA().GetCoordinates()[2]]

        elif len(self.resName) == 4 and self.resName[1:] in AAs:
            sys.stderr.write("ROTAMER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            sys.exit("UNKNOWN AMINO ACID YO. DO SOMETHING ABOUT THIS!!!!!")

    def GetCentroid(self):
        return self.centroid

    def GetVector(self):
        return self.vector

    def SetChainID(self, c):
        self.chainID = c

    def GetASA(self, form):
        d = config.data
        name = config.data.Map("Amino Acids", config.data.Standardize(self.resName))
        return config.data.GetJson()["Amino Acids"][name]["ASA"][form]

    def WriteForPDB(self):
        retstr = ""
        for atom in self.atoms:
            retstr += atom.WritePDB(intro="ATOM  ")
        return retstr

    @staticmethod
    def OneToThree(oln):
        if oln in ONE_LETTER:
            try:
                return ONE_LETTER[oln]
            except KeyError:
                return None

    @staticmethod
    def NameToThree(name):
        if name in FULL_NAME:
            try:
                return FULL_NAME[name]
            except KeyError:
                return None

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

    # TODO These would be pretty cool to implement if possible. Open and write to a new python file that these access?
    @staticmethod
    def Set_lt(str):
        print('stub')

    @staticmethod
    def Set_repr(str):
        print('stub')


    def Set_str(self, str):
        return

    def __lt__(self, other):
        return self.seqNum < other.number

    def __repr__(self):
        return f"RESIDUE: {self.resName}, NUMBER: {self.seqNum}"

    def __str__(self):
        return f"{self.resName} {self.seqNum}"


# Shoved down here for cleanliness
global ONE_LETTER
ONE_LETTER = {
    "R": 'ARG',
    "H": 'HIS',
    "K": 'LYS',
    "D": 'ASP',
    "E": 'GLU',
    "S": 'SER',
    "T": 'THR',
    "N": 'ASN',
    "Q": 'GLN',
    "C": 'CYS',
    "U": 'SEC',
    "G": 'GLY',
    "P": 'PRO',
    "A": 'ALA',
    "V": 'VAL',
    "I": 'ILE',
    "L": 'LEU',
    "M": 'MET',
    "F": 'PHE',
    "Y": 'TYR',
    "W": 'TRP',
    "O": 'PYL'
}

global THREE_LETTER
THREE_LETTER = {
    "ARG": 'R',
    "HIS": 'H',
    "LYS": 'K',
    "ASP": 'D',
    "GLU": 'E',
    "SER": 'S',
    "THR": 'T',
    "ASN": 'N',
    "GLN": 'G',
    "CYS": 'C',
    "SEC": 'U',
    "GLY": 'G',
    "PRO": 'P',
    "ALA": 'A',
    "VAL": 'V',
    "ILE": 'I',
    "LEU": 'L',
    "MET": 'M',
    "PHE": 'F',
    "TYR": 'Y',
    "TRP": 'W',
    "PYL": 'O'
}

global FULL_NAME
FULL_NAME = {
    "ALANINE": 'ALA',
    "CYSTEINE": 'CYS',
    "ASPARTIC ACID": 'ASP',
    "ASPARTATE": 'ASP',
    "GLUTAMIC ACID": 'GLU',
    "GLUTAMATE": 'GLU',
    "PHENYLALANINE": 'PHE',
    "GLYCINE": 'GLY',
    "HISTIDINE": 'HIS',
    "ISOLEUCINE": 'ILE',
    "LYSINE": 'LYS',
    "LEUCINE": 'LEU',
    "METHIONINE": 'MET',
    "ASPARAGINE": 'ASN',
    "PYRROLYSINE": 'PYL',
    "PROLINE": 'PRO',
    "GLUTAMINE": 'GLN',
    "ARGININE": 'ARG',
    "SERINE": 'SER',
    "THREONINE": 'THR',
    "SELENOCYSTEINE": 'SEC',
    "VALINE": 'VAL',
    "TRYPTOPHAN": 'TRP',
    "TYROSINE": 'TYR',
}
