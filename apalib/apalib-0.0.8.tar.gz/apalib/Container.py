from apalib.AminoAcid import AminoAcid
from apalib.Atom import Atom
from apalib.DNA import DNA
from apalib.RNA import RNA
from apalib.HETATM import HETATM
from apalib.Data import data as data

class Container:
    def __init__(self):
        self.current_fetch = None
        self.PeptideChains = None
        self.DNAChains = None
        self.RNAChains = None
        self.HETATMChains = None

    def ClearAll(self, initialize = True):
        self.__init__()
        if initialize:
            self.HETATMChains = {}
            self.PeptideChains = {}
            self.DNAChains = {}
            self.RNAChains = {}

    def AddChain(self, key):
        self.HETATMChains[key] = {}
        self.PeptideChains[key] = {}
        self.DNAChains[key] = {}
        self.RNAChains[key] = {}

    #Create a new residue if missing. Otherwise return the designated residue
    def AddResidue(self, resType, index, resName, chainID):
        if chainID not in self.HETATMChains.keys():
            self.AddChain(chainID)
        index = int(index.strip())
        if resType == 'HETATM':
            if index in self.HETATMChains[chainID].keys():
                return self.HETATMChains[chainID][index]
            self.HETATMChains[chainID][index] = HETATM(seqNum=index, resName=resName, chainID=chainID)
            return self.HETATMChains[chainID][index]

        elif resType == 'RNA':
            if index in self.RNAChains[chainID].keys():
                return self.RNAChains[chainID][index]
            self.RNAChains[chainID][index] = RNA(seqNum=index, resName=resName, chainID=chainID)
            return self.RNAChains[chainID][index]

        elif resType == 'DNA':
            if index in self.DNAChains[chainID].keys():
                return self.DNAChains[chainID][index]
            self.DNAChains[chainID][index] = DNA(seqNum=index, resName=resName, chainID=chainID)
            return self.DNAChains[chainID][index]

        elif resType == 'AA':
            if index in self.PeptideChains[chainID].keys():
                return self.PeptideChains[chainID][index]
            self.PeptideChains[chainID][index] = AminoAcid(seqNum=index, resName=resName, chainID=chainID)
            return self.PeptideChains[chainID][index]
        else:
            import sys
            sys.stderr.write("Something went wrong in adding a residue")


    def SetFetch(self, fetch):
        self.current_fetch = fetch

    def GetFetch(self):
        return self.current_fetch

    def ClearFetch(self):
        self.current_fetch = None

    def SetProteinChains(self, pchain):
        self.PeptideChains = pchain

    def GetPeptideChains(self):
        return self.PeptideChains

    def ClearPeptideChains(self):
        self.PeptideChains = None

    def SetDNAChains(self,dchain):
        self.DNAChains = dchain

    def GetDNAChains(self):
        return self.DNAChains

    def ClearDNAChains(self):
        self.DNAChains = None

    def GetRNAChains(self):
        return self.RNAChains

    def SetRNAChains(self, rchain):
        self.RNAChains = rchain

    def ClearRNAChains(self):
        self.RNAChains = None

    def GetHETATMChains(self):
        return self.HETATMChains

    def SetHETATMChains(self, hchain):
        self.HETATMChains = hchain

    def ClearHEETATMChains(self):
        self.HETATMChains = None

    #Perform calculations, etc. to be done after a full parse
    def _PostParseEvaluations(self):
        #Fill in variables
        for chain in self.PeptideChains.keys():
            for res in self.PeptideChains[chain].values():
                res.CalculateCentroid()
        pass



    #Returns all residues from all children of CONTAINER as a list
    #Nasty list comprehension goes faster than a for-loop
    def DumpResidues(self):
        return [val for sublist in (list(res.values()) for res in list(self.PeptideChains.values()) + list(self.HETATMChains.values()) + list(self.DNAChains.values()) + list(self.RNAChains.values())) for val in sublist]
        # lst =  list(self.PeptideChains.values()) + list(self.HETATMChains.values()) + list(self.DNAChains.values()) + list(self.RNAChains.values())
        # retlst = []
        # for d in lst:
        #     retlst += list(d.values())
        # return retlst

    #Return all atoms from all children of CONTAINER as a list
    #Virtually human-unreadable, but its efficient and pythonic
    def DumpAtoms(self):
        return [atom for sublist in (group.GetAtoms() for group in (val for sublist in (list(res.values()) for res in list(self.PeptideChains.values()) + list(self.HETATMChains.values()) + list(self.DNAChains.values()) + list(self.RNAChains.values())) for val in sublist)) for atom in sublist]
        # return [atom for sublist in (group.GetAtoms() for group in self.DumpResidues()) for atom in sublist]




        # retLst = []
        # val = self.DumpResidues()
        # for key in self.PeptideChains.keys():
        #     print(self.PeptideChains.values())
        #     # retLst += self.PeptideChains[key].GetAtoms()
        # for key in self.HETATMChains.keys():
        #     pass
        #     # retLst += self.HETATMChains[key].GetAtoms()
        # for key in self.DNAChains.keys():
        #     pass
        #     # retLst += self.DNAChains[key].GetAtoms()
        # for key in self.RNAChains.keys():
        #     pass
        #     # retLst += self.RNAChains[key].GetAtoms()
        # return retLst

    #Return all residues from all chains as a single list
    def AsList(self, ordered=True):
        fullLst = []
        retLst = []
        lst = [self.PeptideChains, self.DNAChains, self.RNAChains, self.HETATMChains]
        for val in lst:
            if val is not None and len(val.keys()) != 0:
                fullLst = fullLst + list(val.values())
        for val in fullLst:
            retLst = retLst + list(val.values())
        return sorted(retLst, key=lambda val : val.number) if ordered else retLst
