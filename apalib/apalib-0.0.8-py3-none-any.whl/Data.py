import pkg_resources
import json
import apalib.apalibExceptions

class Data:
    def __init__(self):
        _stream = pkg_resources.resource_stream(__name__, 'json/chemistry.json')
        self._jData = json.load(_stream)

    class MutationError(Exception):
        pass

    def __setattr__(self, key, value):
        if key == '_jdata' and self._jData is not None:
            raise self.MutationError(f"Attempt to mutate or reassign a protected variable: {key}")
        else:
            self.__dict__[key] = value

    def GetJson(self):
        return self._jData

    def Map(self, dtype, val):
        return self._jData["Map"][dtype][val]

    def ValidateAA(self, res):
        check_res = self.Standardize(res)
        if len(res) != 3:
            return False
        if check_res in self._jData["Map"]["Amino Acids"].keys():
            return True
        return False

    def ValidateDNA(self, res, no_u = False):
        check_res = self.Standardize(res)
        if len(res) != 2:
            return False
        if check_res == "-" or check_res == ".":
            return False
        if no_u and (check_res == "U" or check_res == "DU"):
            return False
        if check_res in self._jData["Map"]["DNA Nucleotides"].keys():
            return True
        return False

    def SetDNAName(self, name):
        return "D" + self.Map("DNA Nucleotides", name)[0]

    def ValidateRNA(self, res, no_t = False):
        check_res = self.Standardize(res)
        if len(res) != 1:
            return False
        if check_res == "-" or res == ".":
            return False
        if no_t and check_res == "T":
            return False
        if check_res in self._jData["Map"]["DNA Nucleotides"].keys():
            return True
        return False

    def SetRNAName(self, name):
        return self.Map("RNA Nucleotides", name)[0]

    def Standardize(self, res):
        ret_str = ""
        for i in range(len(res)):
            if i == 0:
                ret_str += res[i].upper()
            elif i == 1 and len(res) == 2:
                ret_str += res[i].upper()
            else:
                ret_str += res[i].lower()
        return ret_str

    def _BuildConfiguration(self, element):
        ret = self._jData['Atoms'][element]["Ground Configuration"]
        while ret.find(']') != -1:
            next = ret[1:ret.find(']')]
            ret = ret[ret.find(']') + 1:]
            ret = self._jData['Atoms'][self.Map('Elements',next)]["Ground Configuration"] + " " + ret
        return ret


data = Data()
