import apalib.apalibExceptions
import apalib.apalibExceptions as apaExcept
from apalib.Atom import Atom
from apalib.HETATM import *
from apalib.AminoAcid import *
import sys
from apalib import *
from apalib.Data import data as data

class PDB:
    def __init__(self):
        self.container = Container()
        # print(apalib.j_data.GetJson())

    def Contents(self):
        return self.container

    def Fetch(self, prot, crash = True):
        # print("Fetching ", prot)
        import urllib.request
        url = r'https://files.rcsb.org/download/' + prot.strip() + '.pdb'
        try:
            with urllib.request.urlopen(url) as f:
                self.container.SetFetch(f.read().decode('utf-8'))
                self._Parse()
                return True
        except urllib.error.URLError:
            sys.stderr.write("The requested pdb code could not be retrieved or does not exist\n")
            if crash:
                exit()
            return False

    def Read(self, path):
        with open(path, 'r') as fp:
            self.container.SetFetch(fp.read())
            self._Parse()

    # Wrapper for the ParsePDB file to allow functionality with a fetched protein
    def _Parse(self):
        try:
            if self.container.GetFetch() is None:
                raise apaExcept.NoFetchError
            return self._ParsePDB(self.container.GetFetch())
            # return self._ParsePDB(self.container.GetFetch().splitlines())
        except apaExcept.NoFetchError as e:
            sys.stderr.write(e.message)


    #PDB standard described here: https://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html
    def _ParsePDB(self, raw_pdb):
        self.container.ClearAll()
        for line in raw_pdb.splitlines():
            if line[0:6] == 'ATOM  ' or line[0:6] == 'HETATM':
                self._ParseAtomHETATM(line)
            #TODO Parse REMARK 350 to get symmetry information

        self.container._PostParseEvaluations()

    def _ParseAtomHETATM(self, line):
        serial = line[6:11].strip()
        name = line[12:16].strip()
        altLoc = line[16].strip()
        resName = line[17:20].strip()
        chainID = line[21].strip()
        resSeq = line[22:26].strip()
        iCode = line[26].strip()
        x = line[30:38].strip()
        y = line[38:46].strip()
        z = line[46:54].strip()
        occupancy = line[54:60].strip()
        tempFactor = line[60:66].strip()
        element = line[76:78].strip()
        charge = line[78:80].strip()
        atom = Atom.Atom(serial=serial, name=name, altLoc=altLoc, resName=resName, chainID=chainID, resSeq=resSeq,
                         iCode=iCode, x=x, y=y, z=z, occupancy=occupancy, tempFactor=tempFactor, element=element,
                         charge=charge)
        resType = self.DetermineResType(resName)
        residue = self.container.AddResidue(resType, resSeq, resName, chainID)
        residue.InsertAtom(atom)

    def DetermineResType(self, resName):
        if data.ValidateRNA(resName):
            return 'RNA'
        elif data.ValidateDNA(resName):
            return 'DNA'
        elif data.ValidateAA(resName):
            return "AA"
        else:
            return "HETATM"

    #Remove all of the waters from the current fetch. Probably make this more general for any HETATM group. Make a wrapper?
    def RemoveWater(self):
        h_chains = self.container.GetHETATMChains()
        for chain in h_chains.keys():
            h_chains[chain] = {key: value for (key, value) in h_chains[chain].items() if value.GetResName().upper() != 'HOH'}

    # def Validate(self, **kwargs):
    #     for key in kwargs:
    #         if key != 'pdb' or (key == 'pdb' and not isinstance(kwargs['pdb'], str)):
    #             raise apalib.apalibExceptions.BadKwarg('pdb=<pdb_to_validate>')

    #Write contents to a PDB file
    def WritePDB(self, fp):
        wr = ""
        s = sorted(self.container.DumpResidues(), key=lambda x: x.seqNum)
        with open(fp, "w") as f:
            for res in s:
                f.write(res.WriteForPDB())
