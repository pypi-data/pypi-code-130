import scipy
from scipy import interpolate
import multiprocessing as mp
from scipy.fft import ifft
from scipy import linalg

import math

import csv
import os
import numpy as np
from multiprocessing import Process, Queue, Pool
import time


class InputData:

    def __init__(self):
        self.D = 3
        self.name_of_file = 0
        self.cores_amount = 1
        self.N = None
        self.L = None
        self.file_name = 0
        self.message = 0
        self.sum = 0
        self.host = 0
        self.user = 0
        self.password = 0
        self.remote = 0
        self.equilibrium_file = 0
        self.potential_energy_file = 0
        self.value_holder = 0
        self.EquilMolecule = 0
        self.PES = 0
        self.error = 0

        self.N1 = 0
        self.L1 = 0
        self.N2 = 0
        self.L2 = 0
        self.N3 = 0
        self.L3 = 0

    @classmethod
    def setN1(self, N1):
        self.N1 = N1
        return

    @classmethod
    def setL1(self, L1):
        self.L1 = L1
        return

    @classmethod
    def setN2(self, N2):
        self.N2 = N2
        return

    @classmethod
    def setL2(self, L2):
        self.L2 = L2
        return

    @classmethod
    def setN3(self, N3):
        self.N3 = N3
        return

    @classmethod
    def setL3(self, L3):
        self.L3 = L3
        return

    @classmethod
    def getN1(self):
        return self.N1

    @classmethod
    def getN2(self):
        return self.N2

    @classmethod
    def getN3(self):
        return self.N3

    @classmethod
    def getL1(self):
        return self.L1

    @classmethod
    def getL2(self):
        return self.L2

    @classmethod
    def getL3(self):
        return self.L3

    """
    The following methods are setters. These values get set in test1.py
    """

    @classmethod
    def seterror(self, error):
        self.error = error
        return

    @classmethod
    def setvalue_holder(self, value_holder):
        self.value_holder = value_holder
        return

    @classmethod
    def setcores_amount(self, cores):
        self.cores_amount = cores
        return

    @classmethod
    def setequilibrium_file(self, equilibrium_file):
        self.equilibrium_file = equilibrium_file
        return

    @classmethod
    def setpotential_energy(self, potential_energy):
        self.potential_energy_file = potential_energy
        return

    @classmethod
    def setname_of_file(self, name_of_file):
        self.name_of_file = name_of_file
        return

    @classmethod
    def setHmat(self, Hmat):
        self.Hmat = Hmat
        return

    @classmethod
    def setD(self, D):
        self.D = D
        return

    @classmethod
    def setNlist(self, N):
        self.N = N
        return

    @classmethod
    def setLlist(self, L):
        self.L = L
        return

    @classmethod
    def setFileName(self, file_name):
        self.file_name = file_name
        return

    @classmethod
    def setModelData(self, model_data):
        self.model_data = model_data
        return

    @classmethod
    def setMessage(self, message):
        self.message = message
        return

    @classmethod
    def set_sum(self, sum):
        self.sum = sum
        return

    @classmethod
    def set_host(self, host):
        self.host = host
        return

    @classmethod
    def set_user(self, user):
        self.user = user
        return

    @classmethod
    def set_password(self, password):
        self.password = password
        return

    @classmethod
    def set_remote(self, remote):
        self.remote = remote
        return

    @classmethod
    def set_name_of_file(self, name_of_file):
        self.name_of_file = name_of_file
        return

    @classmethod
    def setEquilMolecule(self, eq):
        self.EquilMolecule = eq
        return

    @classmethod
    def setPES(self, pes):
        self.PES = pes
        return

    @classmethod
    def getD(self):
        return self.D

    @classmethod
    def getNlist(self):
        return self.N

    @classmethod
    def getLlist(self):
        return self.L

    @classmethod
    def getEquilMolecule(self):
        return self.EquilMolecule

    @classmethod
    def getPES(self):
        return self.PES

    @classmethod
    def getError(self):
        return self.error

    @classmethod
    def getequilibrium_file(self):
        return self.equilibrium_file

    @classmethod
    def getpotential_energy(self):
        return self.potential_energy_file


# TODO take the values in Eignevalues and Eigenvectos and write them to a CSV file in main on line 104.
class OutputData:
    eigenvalues = []
    eigenvectors = []

    def __init__(self):
        self.eigenvalues = []
        self.eigenvectors = []

    @classmethod
    def setEigenvalues(self, evalues):
        self.eigenvalues = evalues
        return

    @classmethod
    def setEigenvectors(self, evectors):
        self.eigenvectors = evectors
        return

    @classmethod
    def getEigenvalues(self):
        return self.eigenvalues

    @classmethod
    def getEigenvectors(self):
        return self.eigenvectors


Models_List = []


class Harmonic_Oscillator:
    def __init__(self):
        self.type = 0
        self.name = "Harmonic Oscillator"
        self.nparam = 2
        self.label = ["\u03BC", "k"]
        self.param = np.zeros(self.nparam, float)
        Models_List.append(self)

    @classmethod
    def set_param(self, param_list):
        for i in range(self.nparam):
            self.param[i] = param_list[i]
        return


class Morse_Oscillator:
    def __init__(self):
        self.type = 1
        self.name = "Morse Oscillator"
        self.nparam = 3
        self.label = ["\u03BC", "De", "a"]
        self.param = np.zeros(self.nparam, float)
        Models_List.append(self)

    @classmethod
    def set_param(self, param_list):
        for i in range(self.nparam):
            self.param[i] = param_list[i]
        return


class Test_Oscillator:
    def __init__(self):
        self.type = 2
        self.name = "Test Oscillator"
        self.nparam = 4
        self.mu = 0
        self.label = ["a", "b", "c", "d"]
        self.param = np.zeros(self.nparam, float)
        Models_List.append(self)

    @classmethod
    def set_param(self, param_list):
        for i in range(self.nparam):
            self.param[i] = param_list[i]
        return


class Hi:
    def __init__(self):
        self.type = 3
        self.name = "Hi"
        self.nparam = 4
        self.mu = 0
        self.label = ["z", "y", "x", "w"]
        self.param = np.zeros(self.nparam, float)
        Models_List.append(self)

    @classmethod
    def set_param(self, param_list):
        for i in range(self.nparam):
            self.param[i] = param_list[i]
        return


class pyfghutil:
    def __init__(self):
        print('')

    @classmethod
    def IndexToPoint(self, D, N, idx):
        pt = idx[0]
        for j in range(1, D):
            pt = pt * N[j]
            pt = pt + idx[j]
        return pt

    @classmethod
    def PointToIndex(self, D, N, pt):
        idx = np.zeros(D, dtype=int)
        p = pt
        for j in range(D - 1, -1, -1):
            idx[j] = p % N[j]
            p = p // N[j]
        return idx

    # A lookup dictionary connecting each atomic number with its corresponding atomic symbol.

    AtomicSymbolLookup = {
        1: "H",
        2: "He",
        3: "Li",
        4: "Be",
        5: "B",
        6: "C",
        7: "N",
        8: "O",
        9: "F",
        10: "Ne",
        11: "Na",
        12: "Mg",
        13: "Al",
        14: "Si",
        15: "P",
        16: "S",
        17: "Cl",
        18: "Ar",
        19: "K",
        20: "Ca",
        21: "Sc",
        22: "Ti",
        23: "V",
        24: "Cr",
        25: "Mn",
        26: "Fe",
        27: "Co",
        28: "Ni",
        29: "Cu",
        30: "Zn",
        31: "Ga",
        32: "Ge",
        33: "As",
        34: "Se",
        35: "Br",
        36: "Kr",
        37: "Rb",
        38: "Sr",
        39: "Y",
        40: "Zr",
        41: "Nb",
        42: "Mo",
        43: "Tc",
        44: "Ru",
        45: "Rh",
        46: "Pd",
        47: "Ag",
        48: "Cd",
        49: "In",
        50: "Sn",
        51: "Sb",
        52: "Te",
        53: "I",
        54: "Xe",
        55: "Cs",
        56: "Ba",
        57: "La",
        58: "Ce",
        59: "Pr",
        60: "Nd",
        61: "Pm",
        62: "Sm",
        63: "Eu",
        64: "Gd",
        65: "Tb",
        66: "Dy",
        67: "Ho",
        68: "Er",
        69: "Tm",
        70: "Yb",
        71: "Lu",
        72: "Hf",
        73: "Ta",
        74: "W",
        75: "Re",
        76: "Os",
        77: "Ir",
        78: "Pt",
        79: "Au",
        80: "Hg",
        81: "Tl",
        82: "Pb",
        83: "Bi",
        84: "Po",
        85: "At",
        86: "Rn",
        87: "Fr",
        88: "Ra",
        89: "Ac",
        90: "Th",
        91: "Pa",
        92: "U",
        93: "Np",
        94: "Pu",
        95: "Am",
        96: "Cm",
        97: "Bk",
        98: "Cf",
        99: "Es",
        100: "Fm",
        101: "Md",
        102: "No",
        103: "Lr",
        104: "Rf",
        105: "Db",
        106: "Sg",
        107: "Bh",
        108: "Hs",
        109: "Mt",
        110: "Ds",
        111: "Rg",
        112: "Cn",
        113: "Nh",
        114: "Fl",
        115: "Mc",
        116: "Lv",
        117: "Ts",
        118: "Og"
    }

    # A lookup dictionary connecting each nuclide with its mass (in amu).

    MassLookup = {
        "H-1": 1.007825032,
        "H-2": 2.014101778,
        "H-3": 3.016049278,
        "He-3": 3.01602932,
        "He-4": 4.002603254,
        "Li-6": 6.015122887,
        "Li-7": 7.016003437,
        "Be-9": 9.012183065,
        "B-10": 10.01293695,
        "B-11": 11.00930536,
        "C-12": 12.0,
        "C-13": 13.00335484,
        "C-14": 14.00324199,
        "N-14": 14.003074,
        "N-15": 15.0001089,
        "O-16": 15.99491462,
        "O-17": 16.99913176,
        "O-18": 17.99915961,
        "F-19": 18.99840316,
        "Ne-20": 19.99244018,
        "Ne-21": 20.99384669,
        "Ne-22": 21.99138511,
        "Na-23": 22.98976928,
        "Mg-24": 23.9850417,
        "Mg-25": 24.98583698,
        "Mg-26": 25.98259297,
        "Al-27": 26.98153853,
        "Si-28": 27.97692653,
        "Si-29": 28.97649466,
        "Si-30": 29.97377014,
        "P-31": 30.973762,
        "P-32": 31.97207117,
        "P-33": 32.97145891,
        "P-34": 33.967867,
        "P-36": 35.96708071,
        "S-32": 31.97207117,
        "S-33": 32.97145890,
        "S-34": 33.96786701,
        "Cl-35": 34.96885268,
        "Cl-37": 36.9659026,
        "Ar-36": 35.96754511,
        "Ar-38": 37.96273211,
        "Ar-40": 39.96238312,
        "K-39": 38.96370649,
        "K-40": 39.96399817,
        "K-41": 40.96182526,
        "Ca-40": 39.96259086,
        "Ca-42": 41.95861783,
        "Ca-43": 42.95876644,
        "Ca-44": 43.95548156,
        "Ca-46": 45.953689,
        "Ca-48": 47.95252276,
        "Sc-45": 44.95590828,
        "Ti-46": 45.95262772,
        "Ti-47": 46.95175879,
        "Ti-48": 47.94794198,
        "Ti-49": 48.94786568,
        "Ti-50": 49.94478689,
        "V-50": 49.94715601,
        "V-51": 50.94395704,
        "Cr-50": 49.94604183,
        "Cr-52": 51.94050623,
        "Cr-53": 52.94064815,
        "Cr-54": 53.93887916,
        "Mn-55": 54.93804391,
        "Fe-54": 53.93960899,
        "Fe-56": 55.93493633,
        "Fe-57": 56.93539284,
        "Fe-58": 57.93327443,
        "Co-59": 58.93319429,
        "Ni-58": 57.93534241,
        "Ni-60": 59.93078588,
        "Ni-61": 60.93105557,
        "Ni-62": 61.92834537,
        "Ni-64": 63.92796682,
        "Cu-63": 62.92959772,
        "Cu-65": 64.9277897,
        "Zn-64": 63.92914201,
        "Zn-66": 65.92603381,
        "Zn-67": 66.92712775,
        "Zn-68": 67.92484455,
        "Zn-70": 69.9253192,
        "Ga-69": 68.9255735,
        "Ga-71": 70.92470258,
        "Ge-70": 69.92424875,
        "Ge-72": 71.92207583,
        "Ge-73": 72.92345896,
        "Ge-74": 73.92117776,
        "Ge-76": 75.92140273,
        "As-75": 74.92159457,
        "Se-74": 73.92247593,
        "Se-76": 75.9192137,
        "Se-77": 76.91991415,
        "Se-78": 77.91730928,
        "Se-80": 79.9165218,
        "Se-82": 81.9166995,
        "Br-79": 78.9183376,
        "Br-81": 80.9162897,
        "Kr-78": 77.92036494,
        "Kr-80": 79.91637808,
        "Kr-82": 81.91348273,
        "Kr-83": 82.91412716,
        "Kr-84": 83.91149773,
        "Kr-86": 85.91061063,
        "Rb-85": 84.91178974,
        "Rb-87": 86.90918053,
        "Sr-84": 83.9134191,
        "Sr-86": 85.9092606,
        "Sr-87": 86.9088775,
        "Sr-88": 87.9056125,
        "Y-89": 88.9058403,
        "Zr-90": 89.9046977,
        "Zr-91": 90.9056396,
        "Zr-92": 91.9050347,
        "Zr-94": 93.9063108,
        "Zr-96": 95.9082714,
        "Nb-93": 92.906373,
        "Mo-92": 91.90680796,
        "Mo-94": 93.9050849,
        "Mo-95": 94.90583877,
        "Mo-96": 95.90467612,
        "Mo-97": 96.90601812,
        "Mo-98": 97.90540482,
        "Mo-100": 99.9074718,
        "Tc-97": 96.9063667,
        "Tc-98": 97.9072124,
        "Tc-99": 98.9062508,
        "Ru-96": 95.90759025,
        "Ru-98": 97.9052868,
        "Ru-99": 98.9059341,
        "Ru-100": 99.9042143,
        "Ru-101": 100.9055769,
        "Ru-102": 101.9043441,
        "Ru-104": 103.9054275,
        "Rh-103": 102.905498,
        "Pd-102": 101.9056022,
        "Pd-104": 103.9040305,
        "Pd-105": 104.9050796,
        "Pd-106": 105.9034804,
        "Pd-108": 107.9038916,
        "Pd-110": 109.9051722,
        "Ag-107": 106.9050916,
        "Ag-109": 108.9047553,
        "Cd-106": 105.9064599,
        "Cd-108": 107.9041834,
        "Cd-110": 109.9030066,
        "Cd-111": 110.9041829,
        "Cd-112": 111.9027629,
        "Cd-113": 112.9044081,
        "Cd-114": 113.9033651,
        "Cd-116": 115.9047632,
        "In-113": 112.9040618,
        "In-115": 114.9038788,
        "Sn-112": 111.9048239,
        "Sn-114": 113.9027827,
        "Sn-115": 114.9033447,
        "Sn-116": 115.9017428,
        "Sn-117": 116.902954,
        "Sn-118": 117.9016066,
        "Sn-119": 118.9033112,
        "Sn-120": 119.9022016,
        "Sn-122": 121.9034438,
        "Sn-124": 123.9052766,
        "Sb-121": 120.903812,
        "Sb-123": 122.9042132,
        "Te-120": 119.9040593,
        "Te-122": 121.9030435,
        "Te-123": 122.9042698,
        "Te-124": 123.9028171,
        "Te-125": 124.9044299,
        "Te-126": 125.9033109,
        "Te-128": 127.9044613,
        "Te-139": 129.9062227,
        "I-127": 126.9044719,
        "Xe-124": 123.905892,
        "Xe-126": 125.9042983,
        "Xe-128": 127.903531,
        "Xe-129": 128.9047809,
        "Xe-130": 129.9035093,
        "Xe-131": 130.9050841,
        "Xe-132": 131.9041551,
        "Xe-134": 133.9053947,
        "Xe-136": 135.9072145,
        "Cs-133": 132.905452,
        "Ba-130": 129.9063207,
        "Ba-132": 131.9050611,
        "Ba-134": 133.9045082,
        "Ba-135": 134.9056884,
        "Ba-136": 135.9045757,
        "Ba-137": 136.9058271,
        "Ba-138": 137.905247,
        "La-138": 137.9071149,
        "La-139": 138.9063563,
        "Ce-136": 135.9071292,
        "Ce-138": 137.905991,
        "Ce-140": 139.9054431,
        "Ce-142": 141.9092504,
        "Pr-141": 140.9076576,
        "Nd-142": 141.907729,
        "Nd-143": 142.90982,
        "Nd-144": 143.910093,
        "Nd-145": 144.9125793,
        "Nd-146": 145.9131226,
        "Nd-148": 147.9168993,
        "Nd-150": 149.9209022,
        "Pm-145": 144.9127559,
        "Pm-147": 146.915145,
        "Sm-144": 143.9120065,
        "Sm-147": 146.9149044,
        "Sm-148": 147.9148292,
        "Sm-149": 148.9171921,
        "Sm-150": 149.9172829,
        "Sm-152": 151.9197397,
        "Sm-154": 153.9222169,
        "Eu-151": 150.9198578,
        "Eu-153": 152.921238,
        "Gd-152": 151.9197995,
        "Gd-154": 153.9208741,
        "Gd-155": 154.9226305,
        "Gd-156": 155.9221312,
        "Gd-157": 156.9239686,
        "Gd-158": 157.9241123,
        "Gd-160": 159.9270624,
        "Tb-159": 158.9253547,
        "Dy-156": 155.9242847,
        "Dy-158": 157.9244159,
        "Dy-160": 159.9252046,
        "Dy-161": 160.9269405,
        "Dy-162": 161.9268056,
        "Dy-163": 162.9287383,
        "Dy-164": 163.9291819,
        "Ho-165": 164.9303288,
        "Er-162": 161.9287884,
        "Er-164": 163.9292088,
        "Er-166": 165.9302995,
        "Er-167": 166.9320546,
        "Er-168": 167.9323767,
        "Er-170": 169.9354702,
        "Tm-169": 168.9342179,
        "Yb-168": 167.9338896,
        "Yb-170": 169.9347664,
        "Yb-171": 170.9363302,
        "Yb-172": 171.9363859,
        "Yb-173": 172.9382151,
        "Yb-174": 173.9388664,
        "Yb-176": 175.9425764,
        "Lu-175": 174.9407752,
        "Lu-176": 175.9426897,
        "Hf-174": 173.9400461,
        "Hf-176": 175.9414076,
        "Hf-177": 176.9432277,
        "Hf-178": 177.9437058,
        "Hf-179": 178.9458232,
        "Hf-180": 179.946557,
        "Ta-180": 179.9474648,
        "Ta-181": 180.9479958,
        "W-180": 179.9467108,
        "W-182": 181.9482039,
        "W-183": 182.9502228,
        "W-184": 183.9509309,
        "W-186": 185.9543628,
        "Re-185": 184.9529545,
        "Re-187": 186.9557501,
        "Os-184": 183.9524885,
        "Os-186": 185.953835,
        "Os-187": 186.9557474,
        "Os-188": 187.9558352,
        "Os-189": 188.9581442,
        "Os-190": 189.9584437,
        "Os-192": 191.961477,
        "Ir-191": 190.9605893,
        "Ir-193": 192.9629216,
        "Pt-190": 189.9599297,
        "Pt-192": 191.9610387,
        "Pt-194": 193.9626809,
        "Pt-195": 194.9647917,
        "Pt-196": 195.9649521,
        "Pt-198": 197.9678949,
        "Au-197": 196.9665688,
        "Hg-196": 195.9658326,
        "Hg-198": 197.9667686,
        "Hg-199": 198.9682806,
        "Hg-200": 199.9683266,
        "Hg-201": 200.9703028,
        "Hg-202": 201.9706434,
        "Hg-204": 203.973494,
        "Tl-203": 202.9723446,
        "Tl-205": 204.9744278,
        "Pb-204": 203.973044,
        "Pb-206": 205.9744657,
        "Pb-207": 206.9758973,
        "Pb-208": 207.9766525,
        "Bi-209": 208.9803991,
        "Po-209": 208.9824308,
        "Po-210": 209.9828741,
        "At-210": 209.9871479,
        "At-211": 210.9874966,
        "Rn-211": 210.9906011,
        "Rn-220": 220.0113941,
        "Rn-222": 222.0175782,
        "Fr-223": 223.019736,
        "Ra-223": 223.0185023,
        "Ra-224": 224.020212,
        "Ra-226": 226.0254103,
        "Ra-228": 228.0310707,
        "Ac-227": 227.0277523,
        "Th-230": 230.0331341,
        "Th-232": 232.0380558,
        "Pa-231": 231.0358842,
        "U-233": 233.0396355,
        "U-234": 234.0409523,
        "U-235": 235.0439301,
        "U-236": 236.0455682,
        "U-238": 238.0507884,
        "Np-236": 236.04657,
        "Np-237": 237.0481736,
        "Pu-238": 238.0495601,
        "Pu-239": 239.0521636,
        "Pu-240": 240.0538138,
        "Pu-241": 241.0568517,
        "Pu-242": 242.0587428,
        "Pu-244": 244.0642053,
        "Am-241": 241.0568293,
        "Am-243": 243.0613813,
        "Cm-243": 243.0613893,
        "Cm-244": 244.0627528,
        "Cm-245": 245.0654915,
        "Cm-246": 246.0672238,
        "Cm-247": 247.0703541,
        "Cm-248": 248.0723499,
        "Bk-247": 247.0703073,
        "Bk-249": 249.0749877,
        "Cf-249": 249.0748539,
        "Cf-250": 250.0764062,
        "Cf-251": 251.0795886,
        "Cf-252": 252.0816272,
        "Es-252": 252.08298,
        "Fm-257": 257.0951061,
        "Md-258": 258.0984315,
        "Md-260": 260.10365,
        "No-259": 259.10103,
        "Lr-262": 262.10961,
        "Rf-267": 267.12179,
        "Db-268": 268.12567,
        "Sg-271": 271.13393,
        "Bh-272": 272.13826,
        "Hs-270": 270.13429,
        "Mt-276": 276.15159,
        "Ds-281": 281.16451,
        "Rg-280": 280.16514,
        "Cn-285": 285.17712,
        "Nh-284": 284.17873,
        "Fl-289": 289.19042,
        "Mc-288": 288.19274,
        "Lv-293": 293.20449,
        "Ts-292": 292.20746,
        "Og-294": 294.21392

    }

    class Molecule:
        def __init__(self):
            self.Nat = 3
            self.x = []
            self.y = []
            self.z = []
            self.A = []
            self.Z = []
            self.m = []
            # self.m = MassLookup[self.s + "-" + str(self.A)] * 1822.89

        @classmethod
        def getNatom(self):
            return self.Nat

        """
        def getS(self):
            return self.S
        """

        @classmethod
        def setAtomicNoList(self, Z):
            self.Z = Z
            return

        @classmethod
        def getAtomicNoList(self):
            return self.Z

        @classmethod
        def setMassNoList(self, A):
            self.A = A
            return

        @classmethod
        def getMassNoList(self):
            return self.A

        @classmethod
        def setMassList(self, m):
            self.m = m
            return

        @classmethod
        def getMassList(self):
            return self.m

        @classmethod
        def setXList(self, x):
            self.x = x
            return

        @classmethod
        def getXList(self):
            return self.x

        @classmethod
        def setYList(self, y):
            self.y = y
            return

        @classmethod
        def getYList(self):
            return self.y

        @classmethod
        def setZList(self, z):
            self.z = z
            return

        @classmethod
        def getZList(self):
            return self.z


# A class to define a point on the potential energy surface.
# n = the number of the grid point (indexed from 0)
# q = a list of length 3 to define the values of q for the grid point
# x, y, z = a list of the x,y,z coordinates of the atoms at the point
# en = the value of the potential energy at this point (in atomic units)


class PESpoint:
    def __init__(self):
        self.n = 0
        self.q = []
        self.x = []
        self.y = []
        self.z = []
        self.en = 0

    @classmethod
    def getN(self):
        return self.n

    @classmethod
    def getq1(self):
        return self.q[0]

    @classmethod
    def getq2(self):
        return self.q[1]

    @classmethod
    def getq3(self):
        return self.q[2]

    @classmethod
    def getq(self, n):
        if (n == 1):
            return self.getq1()
        elif (n == 2):
            return self.getq2()
        elif (n == 3):
            return self.getq3()

    @classmethod
    def getQList(self):
        return self.q

    @classmethod
    def getX(self, n):
        return self.x[n - 1]

    @classmethod
    def getXList(self):
        return self.x

    @classmethod
    def getY(self, n):
        return self.y[n - 1]

    @classmethod
    def getYList(self):
        return self.y

    @classmethod
    def getZ(self, n):
        return self.z[n - 1]

    @classmethod
    def getZList(self):
        return self.z

    @classmethod
    def getCoord(self, c):
        if (c == 0):
            return self.getX(1)
        elif (c == 1):
            return self.getY(1)
        elif (c == 2):
            return self.getZ(1)
        elif (c == 3):
            return self.getX(2)
        elif (c == 4):
            return self.getY(2)
        elif (c == 5):
            return self.getZ(2)
        elif (c == 6):
            return self.getX(3)
        elif (c == 7):
            return self.getY(3)
        elif (c == 8):
            return self.getZ(3)

    @classmethod
    def setN(self, n):
        self.n = n
        return

    @classmethod
    def setQList(self, q):
        self.q = q
        return

    @classmethod
    def setXList(self, x):
        self.x = x
        return

    @classmethod
    def setYList(self, y):
        self.y = y
        return

    @classmethod
    def setZList(self, z):
        self.z = z
        return

    @classmethod
    def setEnergy(self, en):
        self.en = en
        return

    @classmethod
    def getEnergy(self):
        return self.en

    # A class to define a potential energy surface.
    # N = a list of length 3 containing the number of grid points in each dimension
    # Npts = number of points in the PES
    # pts = a list of length Npts of PESpoint objects

    class PotentialEnergySurface:
        N = []
        Npts = 0
        pts = []

        def __init__(self):
            self.N = []
            self.Npts = 0
            self.pts = []

        #    def getPointByN(self, t, u, v):
        #        m = v + self.N[2] * (u + self.N[1] * t)
        #        return self.pts[m]
        @classmethod
        def getPointByN(self, t, u, v):
            idx = [t, u, v]
            return self.getPointByIdx(idx)

        #    def getPointByIdx(self, idx):
        #        return self.getPointByN(idx[0],idx[1],idx[2])
        @classmethod
        def getPointByIdx(self, idx):
            pt = pyfghutil.IndexToPoint(len(self.N), self.N, idx)
            return self.getPointByPt(pt)

        @classmethod
        def getPointByPt(self, pt):
            return self.pts[pt]

        @classmethod
        def setNpts(self, Npts):
            self.Npts = Npts
            return

        @classmethod
        def setN(self, N):
            self.N = N
            return

        @classmethod
        def getNpts(self):
            return self.Npts

        @classmethod
        def appendPESpt(self, pt):
            self.pts.append(pt)
            return

    @classmethod
    def AlphaAndBetaToCounter(self, alpha, beta, D, N):
        alphaidx = pyfghutil.PointToIndex(D, N, alpha)
        betaidx = pyfghutil.PointToIndex(D, N, beta)
        counter = np.zeros(D * 2, dtype=int)
        for j in range(D):
            counter[2 * j] = betaidx[D - j - 1]
            counter[2 * j + 1] = alphaidx[D - j - 1]
        return counter

    @classmethod
    def AlphaCalc(self, D, counterarray, NValues):
        output = 0
        for a in reversed(range(D)):
            if (a + 1 == D):
                output += counterarray[(a * 2) + 1] * 1
            else:
                output += counterarray[(a * 2) + 1] * (np.prod(NValues[:(D - 1) - a]))
        return output

    @classmethod
    def BetaCalc(self, D, counterarray, NValues):
        output = 0
        for b in reversed(range(D)):
            if (b + 1 == D):
                output += counterarray[(b * 2)] * 1
            else:
                output += counterarray[(b * 2)] * (np.prod(NValues[:(D - 1) - b]))
        return output

    @classmethod
    def DCAAdvance(self, D, counterArray, NValues):
        counterArray[(D * 2) - 1, 0] += 1
        NValueC = 0
        jlcounter = 0
        for c in reversed(range(len(counterArray))):
            if (counterArray[c] >= NValues[NValueC]):
                counterArray[c] = 0
                counterArray[c - 1] += 1
            jlcounter += 1
            if (jlcounter >= 2):
                jlcounter = 0
                NValueC += 1
        return counterArray


def compute_derivative(x, y):
    spl = scipy.interpolate.splrep(x, y, s=0)
    yprime = scipy.interpolate.splev(x, spl, der=1)
    return yprime


class Gmatrix:
    def __init__(self):
        print('')

    @classmethod
    def calcGMatrix(self, D, N, pes, equil):

        Nat = equil.getNatom()
        Npts = np.prod(N)

        dxdq = np.zeros((3 * Nat, D, Npts), dtype=float)
        dxdqcalc = np.zeros((3 * Nat, D, Npts), dtype=int)

        for n in range(Npts):
            for d in range(D - 1, -1, -1):
                for c in range(3 * Nat):
                    if (dxdqcalc[c, d, n] == 0):
                        #                    print ("for point " + str(n) + " in dimension " + str(d))
                        x = np.zeros(N[d], dtype=float)
                        y = np.zeros(N[d], dtype=float)
                        for i in range(N[d]):
                            pt = n + i * np.prod(N[d + 1:])
                            idx = pyfghutil.PointToIndex(D, N, pt)
                            x[i] = pes.getPointByIdx(idx).getq(d + 1)
                            y[i] = pes.getPointByIdx(idx).getCoord(c)
                        #                    print(x, y)
                        dy = compute_derivative(x, y)  # Gmatrix.compute_derivative(x, y)
                        for i in range(N[d]):
                            pt = n + i * np.prod(N[d + 1:])
                            dxdq[c, d, pt] = dy[i]
                            dxdqcalc[c, d, pt] = 1

                #                    if (d == 2):
                #                        idx = pyfghutil.PointToIndex(D, N, n)
                #                        for i in range(D):
                #                            if (i != d):
                #                                print("q" + str(i + 1) + "=" + str(pes.getPointByIdx(idx).getq(i + 1)))
                #                        for i in range(D):
                #                            if (i == d):
                #                                print("q" + str(i + 1) + ": " + str(x))
                #                                print("x" + str(c + 1) + ": " + str(y))
                else:
                    pass
        #            print("skip point " + str(n) + " for dimension " + str(d))

        Gmatrix2 = np.zeros([N[0], N[1], N[2], 3, 3], dtype=float)
        m = equil.getMassList()
        m1 = m[0]
        m2 = m[1]
        m3 = m[2]

        for p in range(Npts):
            G = np.zeros([3, 3], float)
            G[0][0] = m1 * (dxdq[0][0][p] * dxdq[0][0][p] + dxdq[1][0][p] * dxdq[1][0][p]) \
                      + m2 * (dxdq[3][0][p] * dxdq[3][0][p] + dxdq[4][0][p] * dxdq[4][0][p]) \
                      + m3 * (dxdq[6][0][p] * dxdq[6][0][p] + dxdq[7][0][p] * dxdq[7][0][p])
            G[0][1] = m1 * (dxdq[0][0][p] * dxdq[0][1][p] + dxdq[1][0][p] * dxdq[1][1][p]) \
                      + m2 * (dxdq[3][0][p] * dxdq[3][1][p] + dxdq[4][0][p] * dxdq[4][1][p]) \
                      + m3 * (dxdq[6][0][p] * dxdq[6][1][p] + dxdq[7][0][p] * dxdq[7][1][p])
            G[0][2] = m1 * (dxdq[0][0][p] * dxdq[0][2][p] + dxdq[1][0][p] * dxdq[1][2][p]) \
                      + m2 * (dxdq[3][0][p] * dxdq[3][2][p] + dxdq[4][0][p] * dxdq[4][2][p]) \
                      + m3 * (dxdq[6][0][p] * dxdq[6][2][p] + dxdq[7][0][p] * dxdq[7][2][p])
            G[1][1] = m1 * (dxdq[0][1][p] * dxdq[0][1][p] + dxdq[1][1][p] * dxdq[1][1][p]) \
                      + m2 * (dxdq[3][1][p] * dxdq[3][1][p] + dxdq[4][1][p] * dxdq[4][1][p]) \
                      + m3 * (dxdq[6][1][p] * dxdq[6][1][p] + dxdq[7][1][p] * dxdq[7][1][p])
            G[1][2] = m1 * (dxdq[0][1][p] * dxdq[0][2][p] + dxdq[1][1][p] * dxdq[1][2][p]) \
                      + m2 * (dxdq[3][1][p] * dxdq[3][2][p] + dxdq[4][1][p] * dxdq[4][2][p]) \
                      + m3 * (dxdq[6][1][p] * dxdq[6][2][p] + dxdq[7][1][p] * dxdq[7][2][p])
            G[2][2] = m1 * (dxdq[0][2][p] * dxdq[0][2][p] + dxdq[1][2][p] * dxdq[1][2][p]) \
                      + m2 * (dxdq[3][2][p] * dxdq[3][2][p] + dxdq[4][2][p] * dxdq[4][2][p]) \
                      + m3 * (dxdq[6][2][p] * dxdq[6][2][p] + dxdq[7][2][p] * dxdq[7][2][p])
            G[1][0] = G[0][1]
            G[2][0] = G[0][2]
            G[2][1] = G[1][2]
            Ginv = scipy.linalg.inv(G)
            idx = pyfghutil.PointToIndex(D, N, p)
            for r in range(3):
                for s in range(3):
                    Gmatrix2[idx[0]][idx[1]][idx[2]][r][s] = Ginv[r][s]
        return Gmatrix2

    @classmethod
    def calcGMatrix_Old(self, D, N, pes, equil):
        dx1dq1 = np.zeros([N[0], N[1], N[2]])
        dy1dq1 = np.zeros([N[0], N[1], N[2]])
        dx2dq1 = np.zeros([N[0], N[1], N[2]])
        dy2dq1 = np.zeros([N[0], N[1], N[2]])
        dx3dq1 = np.zeros([N[0], N[1], N[2]])
        dy3dq1 = np.zeros([N[0], N[1], N[2]])
        dx1dq2 = np.zeros([N[0], N[1], N[2]])
        dy1dq2 = np.zeros([N[0], N[1], N[2]])
        dx2dq2 = np.zeros([N[0], N[1], N[2]])
        dy2dq2 = np.zeros([N[0], N[1], N[2]])
        dx3dq2 = np.zeros([N[0], N[1], N[2]])
        dy3dq2 = np.zeros([N[0], N[1], N[2]])
        dx1dq3 = np.zeros([N[0], N[1], N[2]])
        dy1dq3 = np.zeros([N[0], N[1], N[2]])
        dx2dq3 = np.zeros([N[0], N[1], N[2]])
        dy2dq3 = np.zeros([N[0], N[1], N[2]])
        dx3dq3 = np.zeros([N[0], N[1], N[2]])
        dy3dq3 = np.zeros([N[0], N[1], N[2]])

        for i in range(N[0]):
            for j in range(N[1]):
                q3 = np.zeros(N[2])
                x1 = np.zeros(N[2])
                y1 = np.zeros(N[2])
                x2 = np.zeros(N[2])
                y2 = np.zeros(N[2])
                x3 = np.zeros(N[2])
                y3 = np.zeros(N[2])
                for k in range(N[2]):
                    q3[k] = pes.getPointByN(i, j, k).getq3()
                    x1[k] = pes.getPointByN(i, j, k).x[0]
                    y1[k] = pes.getPointByN(i, j, k).y[0]
                    x2[k] = pes.getPointByN(i, j, k).x[1]
                    y2[k] = pes.getPointByN(i, j, k).y[1]
                    x3[k] = pes.getPointByN(i, j, k).x[2]
                    y3[k] = pes.getPointByN(i, j, k).y[2]
                x1p = compute_derivative(q3, x1)
                y1p = compute_derivative(q3, y1)
                x2p = compute_derivative(q3, x2)
                y2p = compute_derivative(q3, y2)
                x3p = compute_derivative(q3, x3)
                y3p = compute_derivative(q3, y3)
                for k in range(N[2]):
                    dx1dq3[i][j][k] = x1p[k]
                    dy1dq3[i][j][k] = y1p[k]
                    dx2dq3[i][j][k] = x2p[k]
                    dy2dq3[i][j][k] = y2p[k]
                    dx3dq3[i][j][k] = x3p[k]
                    dy3dq3[i][j][k] = y3p[k]

        for i in range(N[0]):
            for k in range(N[2]):
                q2 = np.zeros(N[1])
                x1 = np.zeros(N[1])
                y1 = np.zeros(N[1])
                x2 = np.zeros(N[1])
                y2 = np.zeros(N[1])
                x3 = np.zeros(N[1])
                y3 = np.zeros(N[1])
                for j in range(N[1]):
                    q2[j] = pes.getPointByN(i, j, k).getq2()
                    x1[j] = pes.getPointByN(i, j, k).x[0]
                    y1[j] = pes.getPointByN(i, j, k).y[0]
                    x2[j] = pes.getPointByN(i, j, k).x[1]
                    y2[j] = pes.getPointByN(i, j, k).y[1]
                    x3[j] = pes.getPointByN(i, j, k).x[2]
                    y3[j] = pes.getPointByN(i, j, k).y[2]
                x1p = compute_derivative(q2, x1)
                y1p = compute_derivative(q2, y1)
                x2p = compute_derivative(q2, x2)
                y2p = compute_derivative(q2, y2)
                x3p = compute_derivative(q2, x3)
                y3p = compute_derivative(q2, y3)
                for j in range(N[1]):
                    dx1dq2[i][j][k] = x1p[j]
                    dy1dq2[i][j][k] = y1p[j]
                    dx2dq2[i][j][k] = x2p[j]
                    dy2dq2[i][j][k] = y2p[j]
                    dx3dq2[i][j][k] = x3p[j]
                    dy3dq2[i][j][k] = y3p[j]

        for j in range(N[1]):
            for k in range(N[2]):
                q1 = np.zeros(N[0])
                x1 = np.zeros(N[0])
                y1 = np.zeros(N[0])
                x2 = np.zeros(N[0])
                y2 = np.zeros(N[0])
                x3 = np.zeros(N[0])
                y3 = np.zeros(N[0])
                for i in range(N[0]):
                    q1[i] = pes.getPointByN(i, j, k).getq1()
                    x1[i] = pes.getPointByN(i, j, k).x[0]
                    y1[i] = pes.getPointByN(i, j, k).y[0]
                    x2[i] = pes.getPointByN(i, j, k).x[1]
                    y2[i] = pes.getPointByN(i, j, k).y[1]
                    x3[i] = pes.getPointByN(i, j, k).x[2]
                    y3[i] = pes.getPointByN(i, j, k).y[2]
                x1p = compute_derivative(q1, x1)
                y1p = compute_derivative(q1, y1)
                x2p = compute_derivative(q1, x2)
                y2p = compute_derivative(q1, y2)
                x3p = compute_derivative(q1, x3)
                y3p = compute_derivative(q1, y3)
                for i in range(N[0]):
                    dx1dq1[i][j][k] = x1p[i]
                    dy1dq1[i][j][k] = y1p[i]
                    dx2dq1[i][j][k] = x2p[i]
                    dy2dq1[i][j][k] = y2p[i]
                    dx3dq1[i][j][k] = x3p[i]
                    dy3dq1[i][j][k] = y3p[i]

        m1 = equil.m[0]
        m2 = equil.m[1]
        m3 = equil.m[2]

        Gmatrix = np.zeros([N[0], N[1], N[2], 3, 3], float)

        for i in range(N[0]):
            for j in range(N[1]):
                for k in range(N[2]):
                    G = np.zeros([3, 3], float)
                    G[0][0] = m1 * (dx1dq1[i][j][k] * dx1dq1[i][j][k] + dy1dq1[i][j][k] * dy1dq1[i][j][k]) \
                              + m2 * (dx2dq1[i][j][k] * dx2dq1[i][j][k] + dy2dq1[i][j][k] * dy2dq1[i][j][k]) \
                              + m3 * (dx3dq1[i][j][k] * dx3dq1[i][j][k] + dy3dq1[i][j][k] * dy3dq1[i][j][k])
                    G[0][1] = m1 * (dx1dq1[i][j][k] * dx1dq2[i][j][k] + dy1dq1[i][j][k] * dy1dq2[i][j][k]) \
                              + m2 * (dx2dq1[i][j][k] * dx2dq2[i][j][k] + dy2dq1[i][j][k] * dy2dq2[i][j][k]) \
                              + m3 * (dx3dq1[i][j][k] * dx3dq2[i][j][k] + dy3dq1[i][j][k] * dy3dq2[i][j][k])
                    G[0][2] = m1 * (dx1dq1[i][j][k] * dx1dq3[i][j][k] + dy1dq1[i][j][k] * dy1dq3[i][j][k]) \
                              + m2 * (dx2dq1[i][j][k] * dx2dq3[i][j][k] + dy2dq1[i][j][k] * dy2dq3[i][j][k]) \
                              + m3 * (dx3dq1[i][j][k] * dx3dq3[i][j][k] + dy3dq1[i][j][k] * dy3dq3[i][j][k])
                    G[1][1] = m1 * (dx1dq2[i][j][k] * dx1dq2[i][j][k] + dy1dq2[i][j][k] * dy1dq2[i][j][k]) \
                              + m2 * (dx2dq2[i][j][k] * dx2dq2[i][j][k] + dy2dq2[i][j][k] * dy2dq2[i][j][k]) \
                              + m3 * (dx3dq2[i][j][k] * dx3dq2[i][j][k] + dy3dq2[i][j][k] * dy3dq2[i][j][k])
                    G[1][2] = m1 * (dx1dq2[i][j][k] * dx1dq3[i][j][k] + dy1dq2[i][j][k] * dy1dq3[i][j][k]) \
                              + m2 * (dx2dq2[i][j][k] * dx2dq3[i][j][k] + dy2dq2[i][j][k] * dy2dq3[i][j][k]) \
                              + m3 * (dx3dq2[i][j][k] * dx3dq3[i][j][k] + dy3dq2[i][j][k] * dy3dq3[i][j][k])
                    G[2][2] = m1 * (dx1dq3[i][j][k] * dx1dq3[i][j][k] + dy1dq3[i][j][k] * dy1dq3[i][j][k]) \
                              + m2 * (dx2dq3[i][j][k] * dx2dq3[i][j][k] + dy2dq3[i][j][k] * dy2dq3[i][j][k]) \
                              + m3 * (dx3dq3[i][j][k] * dx3dq3[i][j][k] + dy3dq3[i][j][k] * dy3dq3[i][j][k])
                    G[1][0] = G[0][1]
                    G[2][0] = G[0][2]
                    G[2][1] = G[1][2]
                    Ginv = scipy.linalg.inv(G)
                    for r in range(3):
                        for s in range(3):
                            Gmatrix[i][j][k][r][s] = Ginv[r][s]
        return Gmatrix


class Tmatrix:
    def __init__(self):
        print('')

    @classmethod
    def bmatrixgen(self, N, L):
        n = (N - 1) // 2
        B = np.zeros((N, N), dtype=float)
        a = np.zeros(N, dtype=complex)
        for i in range(N):
            a[i] = 2 * np.pi * (1j) * (i - n) / L
        aifft = ifft(a, n=N)
        for k in range(N):
            aifft[k] = aifft[k] * np.exp(-2 * np.pi * (1j) * n * k / N)
        for j in range(N):
            for t in range(N):
                B[j, t] = np.real(aifft[(N + j - t) % N])
        return B

    @classmethod
    def bmatrixgen_old(self, NValue, LValue):
        n = int((NValue - 1) / 2)
        b_matrix = np.zeros((NValue, NValue), float)
        for j in range(NValue):
            for l in range(NValue):
                for p in range(1, n + 1):
                    b_matrix[j][l] += float(p) * np.sin(2 * np.pi * float(p) * float(l - j) / float(NValue))
                b_matrix[j][l] *= (4.0 * np.pi) / (LValue * float(NValue))

        return (b_matrix)

    # A function to calculate the CMatrix
    # C(j,l) = ((-8*pi*pi)/(L*L*N) * sum(p=1,n)(p*p*cos(2*pi*p*(l-j)/N))
    # where n = (N-1)/2
    # LValue = L = length of the dimension
    # NValue = N = number of points in the dimension
    # Each dimension has its own set of C matrices
    @classmethod
    def cmatrixgen(self, N, L):
        n = (N - 1) // 2
        C = np.zeros((N, N), dtype=float)
        a = np.zeros(N, dtype=complex)
        for i in range(N):
            a[i] = -4 * np.pi * np.pi * (i - n) * (i - n) / (L * L)
        aifft = ifft(a, n=N)
        for k in range(N):
            aifft[k] = aifft[k] * np.exp(-2 * np.pi * (1j) * n * k / N)
        for j in range(N):
            for t in range(N):
                C[j, t] = np.real(aifft[(N + j - t) % N])
        return C

    @classmethod
    def cmatrixgen_old(self, NValue, LValue):
        # Generate the CMatrix
        c_matrix_local = np.zeros((NValue, NValue), float)
        # Calculate the similar values shared between x,y differences to improve efficiency
        difc_matrix = np.zeros((NValue, 1), float)
        for a in range(NValue):
            for b in range(int((NValue - 1) / 2)):
                difc_matrix[a] += (((b + 1) * (b + 1)) * np.cos(((b + 1) * 2 * np.pi * a) / NValue))
            difc_matrix[a] *= (-8.0 * (np.pi * np.pi) / (float(NValue) * (float(LValue) * float(LValue))))
        # Push the difc_matrix values to their respective c_matrix spots
        for y in range(NValue):
            for x in range(NValue):
                c_matrix_local[x, y] = (difc_matrix[abs(x - y)])
        # Return the matrix
        return c_matrix_local

    # A function to calculate the individual values for the TMatrix
    # Right now, only "approximation 2" is tested.  The other approximations will be for a
    # future release.
    @classmethod
    def Tab(self, d, NValue, LValue, mu, c_matrix_insert, dimensionCounterArray, approximation, b_matrix_insert, GMat):
        # Deltacounter is used to makes sure that the value being calculated is in the diagonal of the matrix
        Deltacounter = 0

        # Total is return value
        def delta(x, y):
            if (x == y):
                return float(1)
            else:
                return float(0)

        total = 0.0
        if (approximation == 4):
            for T in range(d):
                # Check if the T counter is not equal to the index of the C value being tested, and if so it checks for if the dimension's corrosponding x and y values equal each other.
                Deltacounter = 0
                for Ccounter in range(d):
                    if (Ccounter != T):
                        if (dimensionCounterArray[Ccounter * 2] == dimensionCounterArray[(Ccounter * 2) + 1]):
                            Deltacounter += 1
                    else:
                        pass
                # If deltacounter equals the dimensions - 1, add the formula to the total for that C value
                if (Deltacounter == (d - 1)):
                    # print(dimensionCounterArray)
                    try:
                        total += (-1.0 / 2.0) * (GMat[T][T]) * (
                            c_matrix_insert[T][dimensionCounterArray[(T * 2) + 1], dimensionCounterArray[T * 2]])
                    except:
                        print("Trying to access: " + str(dimensionCounterArray[(T * 2) + 1]) + ", " + str(
                            dimensionCounterArray[T * 2]))
                        print(c_matrix_insert[T])
                        print("TAB error")
        elif (approximation == 3):
            # Perform all of the "C" calcuations first
            for C in range(d):
                Deltacounter = 0
                for Ccounter in range(d):
                    if (Ccounter != C):
                        if (dimensionCounterArray[Ccounter * 2] == dimensionCounterArray[(Ccounter * 2) + 1]):
                            Deltacounter += 1
                if (Deltacounter == d - 1):
                    total += float((GMat[C][C])) * (
                        c_matrix_insert[C][dimensionCounterArray[(C * 2) + 1], dimensionCounterArray[C * 2]])
            # Perform all of the "B" calculations second
            for B in range(d):
                if (dimensionCounterArray[B * 2] == dimensionCounterArray[(B * 2) + 1]):
                    temptotal = 1.0
                    for BSecond in range(d):
                        if (BSecond != B):
                            temptotal *= b_matrix_insert[BSecond][
                                dimensionCounterArray[(BSecond * 2) + 1], dimensionCounterArray[BSecond * 2]]
                    # This will be the first set of numbers and then the flipped ones
                    GRange = [*range(d)]
                    GRange.remove(B)
                    Gx = min(GRange)
                    Gy = max(GRange)
                    total += float((GMat[Gx][Gy])) * temptotal * 2
            # Outside of summation multiplication of -hbar^2/2
            total *= (-1.0 * 1.0 ** 2) / (2.0)
        elif (approximation == 2):
            t = int(dimensionCounterArray[0])
            j = int(dimensionCounterArray[1])
            u = int(dimensionCounterArray[2])
            k = int(dimensionCounterArray[3])
            v = int(dimensionCounterArray[4])
            l = int(dimensionCounterArray[5])
            # BMatrix calls are backwards
            # So BMatrix[0] would be B1, but it's actually B3
            sums = 0.0
            for p in range(NValue[0]):
                sums += b_matrix_insert[2][j, p] * b_matrix_insert[2][p, t] * GMat[p][k][l][0][0]
            total += -0.5 * sums * delta(k, u) * delta(l, v)

            sums = 0.0
            for p in range(NValue[1]):
                sums += b_matrix_insert[1][k, p] * b_matrix_insert[1][p, u] * GMat[j][p][l][1][1]
            total += -0.5 * sums * delta(j, t) * delta(l, v)

            sums = 0.0
            for p in range(NValue[2]):
                sums += b_matrix_insert[0][l, p] * b_matrix_insert[0][p, v] * GMat[j][k][p][2][2]
            total += -0.5 * sums * delta(j, t) * delta(k, u)

            total += -0.5 * (b_matrix_insert[2][j, t] * b_matrix_insert[1][k, u] * GMat[t][k][l][0][1]) * delta(v, l)
            total += -0.5 * (b_matrix_insert[2][j, t] * b_matrix_insert[0][l, v] * GMat[t][k][l][0][2]) * delta(k, u)
            total += -0.5 * (b_matrix_insert[1][k, u] * b_matrix_insert[2][j, t] * GMat[j][u][l][1][0]) * delta(v, l)
            total += -0.5 * (b_matrix_insert[1][k, u] * b_matrix_insert[0][l, v] * GMat[j][u][l][1][2]) * delta(j, t)
            total += -0.5 * (b_matrix_insert[0][l, v] * b_matrix_insert[2][j, t] * GMat[j][k][v][2][0]) * delta(k, u)
            total += -0.5 * (b_matrix_insert[0][l, v] * b_matrix_insert[1][k, u] * GMat[j][k][v][2][1]) * delta(j, t)



        else:
            print("This current approximation is incorrect or not supported: " + str(approximation))
            exit()

        return (total)

    # A function that splits the Tmatrix calculation into blocks to be calculated in parallel.
    # Each block uses the Tab function above to calculate individual matrix elements.
    @classmethod
    def TBlockCalc(self, dimensions, NValue, LValue, mu, c_matrix, approximation, blockX, blockY, b_matrix, gmatrix):
        # Blocks will be 0 index
        blockHolder = np.zeros((NValue[0], NValue[0]), float)
        # The 0Start variables will always be 0 at the beginning to act as loop variables that correspond to the blockHolder size
        alpha0start = 0
        beta0start = 0
        for alpha in range(0 + NValue[0] * blockX, NValue[0] + NValue[0] * blockX):
            for beta in range(0 + NValue[0] * blockY, NValue[0] + NValue[0] * blockY):
                counter = pyfghutil.AlphaAndBetaToCounter(alpha, beta, dimensions, NValue)
                if (approximation > 2):
                    counter1 = int(counter[0])
                    counter2 = int(counter[2])
                    counter3 = int(counter[4])
                    blockHolder[alpha0start, beta0start] = Tmatrix.Tab(dimensions, NValue, LValue, mu, c_matrix,
                                                                       counter,
                                                                       approximation, b_matrix,
                                                                       gmatrix[counter1][counter2][counter3])
                else:
                    blockHolder[alpha0start, beta0start] = Tmatrix.Tab(dimensions, NValue, LValue, mu, c_matrix,
                                                                       counter,
                                                                       approximation, b_matrix, gmatrix)
                beta0start += 1
            alpha0start += 1
            beta0start = 0
        return blockHolder

    # The function to calculate a TMatrix using the dataObject class from input
    @classmethod
    def TMatrixCalc(self, dataObject, GMatrix):
        # Establish variables needed
        NValue = []
        LValue = []
        if (int(dataObject.N1) > 0):
            NValue.append(int(dataObject.N1))
            LValue.append(float(dataObject.L1))
        if (int(dataObject.N2) > 0):
            NValue.append(int(dataObject.N2))
            LValue.append(float(dataObject.L2))
        if (int(dataObject.N3) > 0):
            NValue.append(int(dataObject.N3))
            LValue.append(float(dataObject.L3))
        D = len(NValue)
        pes = dataObject.PES
        dimensionCounterArray = np.zeros(D * 2, int)
        mu = []
        Tapprox = 2

        # Create the TMatrix and the TFlagMatrix
        # The alpha and beta values are used to create the TMatrix in the correct position
        tmatrix = np.zeros((np.prod(NValue), np.prod(NValue)), dtype=float)
        tflag = np.zeros((np.prod(NValue), np.prod(NValue)), int)
        alpha = 0
        beta = 0

        # Create the C_Matrix
        c_matrix = []
        for x in reversed(range(len(NValue))):
            c_matrix.append(Tmatrix.cmatrixgen(NValue[x], LValue[x]))

        # Create the B_Matrix if necessary
        if (Tapprox < 4):
            b_matrix = []
            for x in reversed(range(len(NValue))):
                b_matrix.append(Tmatrix.bmatrixgen(NValue[x], LValue[x]))
        else:
            b_matrix = None

        blockCoords = []
        blocks = []
        paramz = []
        totalwidth = int(np.prod(NValue))
        repeatamount = int(totalwidth // NValue[0])
        for x in range(repeatamount):
            for y in range(repeatamount):
                blockCoords.append((x, y))
        if (Tapprox == 4):
            for coords in blockCoords:
                paramz.append((D, NValue, LValue, mu, c_matrix, Tapprox, coords[0], coords[1], None, GMatrix))
        elif (Tapprox < 4):
            for coords in blockCoords:
                paramz.append((D, NValue, LValue, mu, c_matrix, Tapprox, coords[0], coords[1], b_matrix, GMatrix))
        else:
            # Occurs when invalid or unsupported T Approximation is used
            pass
        # Pool and run
        p = mp.Pool(dataObject.cores_amount)
        #    print("Pool go T")
        blocks = p.starmap(Tmatrix.TBlockCalc, paramz)
        #    print("Pool's done T")
        p.close()

        precalc = 0
        for i in range(len(blockCoords)):
            block = blocks[i]
            x = blockCoords[i][0]
            y = blockCoords[i][1]
            tmatrix[(0 + NValue[precalc] * x):(NValue[precalc] + NValue[precalc] * x),
            (0 + NValue[precalc] * y):(NValue[precalc] + NValue[precalc] * y)] = block

        return tmatrix


class Vmatrix:
    def __init__(self):
        print('')

    class NBlock:
        def __init__(self, D, NValues):
            self.D = D
            self.N = NValues[D - 1]
            self.SmallestN = NValues[0]
            self.NProd = np.prod(NValues[:D - 1])
            self.diagblocks = []
            self.difblocks = []
            self.xboffset = 0
            self.yboffset = 0
            if (self.D > 1):
                self.diagblocks = [None] * self.N
                self.difblocks = [None] * (self.N - 1)
                for x in range(self.N):
                    self.diagblocks[x] = Vmatrix.NBlock(D - 1, NValues)

                for y in range(self.N - 1):
                    self.difblocks[y] = Vmatrix.NBlock(D - 1, NValues)

            else:
                self.difblocks = np.zeros((self.N, self.N), float)

        @classmethod
        def difSetup(self):
            if (self.D > 1):
                for x in range(self.N):
                    self.diagblocks[x].xboffset = self.xboffset + int(x * (self.NProd / self.SmallestN))
                    self.diagblocks[x].yboffset = self.yboffset + int(x * (self.NProd / self.SmallestN))
                    self.diagblocks[x].difSetup()

                for y in range(self.N - 1):
                    self.difblocks[y].xboffset = self.xboffset + 0
                    self.difblocks[y].yboffset = self.yboffset + 1 + int(y * (self.NProd / self.SmallestN))
                    self.difblocks[y].difSetup()

        @classmethod
        def coordGen(self):
            if (self.D > 1):
                coords = []
                for x in range(len(self.diagblocks)):
                    coords += self.diagblocks[x].coordGen()
                for y in range(len(self.difblocks)):
                    coords += self.difblocks[y].coordGen()
                return (coords)
            elif (self.D == 1):
                return ([(self.xboffset, self.yboffset)])

        @classmethod
        def print1x1(self):
            if (self.D != 1):
                blank = 0
                # Nothing
            else:
                pass

        @classmethod
        def accessPoint(self, alpha, beta):
            if (self.D > 1):
                return (self.blocks[beta // self.NProd, alpha // self.NProd].accessPoint(beta % self.NProd,
                                                                                         alpha % self.NProd))
            else:
                return (self.blocks[alpha, beta])

        @classmethod
        def setBlock(self, N1BlockX, N1BlockY, blockData, startFlag=True):
            if (startFlag):
                if (self.D > 1):
                    xb = (N1BlockX * self.SmallestN) // self.NProd
                    yb = (N1BlockY * self.SmallestN) // self.NProd
                    # print("Set block (D,xb,yb): "+str(self.D)+", "+str(xb)+", "+str(yb))
                    if (xb == yb):
                        self.diagblocks[xb].setBlock((N1BlockX * self.SmallestN) % self.NProd,
                                                     (N1BlockY * self.SmallestN) % self.NProd, blockData, False)
                    else:
                        xydif = abs(xb - yb)
                        self.difblocks[xydif - 1].setBlock((N1BlockX * self.SmallestN) % self.NProd,
                                                           (N1BlockY * self.SmallestN) % self.NProd, blockData, False)
                else:
                    self.difblocks = blockData
            else:
                if (self.D > 1):
                    xb = N1BlockX // self.NProd
                    yb = N1BlockY // self.NProd
                    if (xb == yb):
                        self.diagblocks[xb].setBlock(N1BlockX % self.NProd, N1BlockY % self.NProd, blockData, False)
                    else:
                        xydif = abs(xb - yb)
                        self.difblocks[xydif - 1].setBlock(N1BlockX % self.NProd, N1BlockY % self.NProd, blockData,
                                                           False)
                else:
                    self.difblocks = blockData

        @classmethod
        def readBlock(self, N1BlockX, N1BlockY, startFlag=True):
            if (startFlag):
                if (self.D > 1):
                    xb = (N1BlockX * self.SmallestN) // self.NProd
                    yb = (N1BlockY * self.SmallestN) // self.NProd
                    if (xb == yb):
                        return (self.diagblocks[xb].readBlock((N1BlockX * self.SmallestN) % self.NProd,
                                                              (N1BlockY * self.SmallestN) % self.NProd, False))
                    else:
                        xydif = abs(xb - yb)
                        return (self.difblocks[xydif - 1].readBlock((N1BlockX * self.SmallestN) % self.NProd,
                                                                    (N1BlockY * self.SmallestN) % self.NProd, False))
                else:
                    return (self.difblocks)
            else:
                if (self.D > 1):
                    xb = N1BlockX // self.NProd
                    yb = N1BlockY // self.NProd
                    if (xb == yb):
                        return (self.diagblocks[xb].readBlock(N1BlockX % self.NProd, N1BlockY % self.NProd, False))
                    else:
                        xydif = abs(xb - yb)
                        return (
                            self.difblocks[xydif - 1].readBlock(N1BlockX % self.NProd, N1BlockY % self.NProd, False))
                else:
                    return (self.difblocks)

    @classmethod
    # A function to calculate the invidivdual values for the VMatrix
    def Vab(self, d, NValue, LValue, deltax, pes, dimensionCounterArray):
        # Deltacounter is used to makes sure that the value being calculated is in the diagonal of the matrix
        Deltacounter = 0
        # Total is the value returned for the calculation
        total = 0.0
        for Vcounter in range(d):
            # Add 1 to deltacounter if the corrosponding x and y values for the dimension equals each other
            if (dimensionCounterArray[Vcounter * 2] == dimensionCounterArray[(Vcounter * 2) + 1]):
                Deltacounter += 1
        # If the deltacounter amount equals the amount of dimensions, perform a summation for the formula
        # Otherwise, the total will remain 0.0
        if (Deltacounter == d):
            total += pes.getPointByN(int(dimensionCounterArray[1]), int(dimensionCounterArray[3]),
                                     int(dimensionCounterArray[5])).getEnergy()

        return (total)

    @classmethod
    def VBlockCalc(self, dimensions, NValue, LValue, pes, blockX, blockY):
        # Blocks will be 0 index
        blockHolder = np.zeros((NValue[0], NValue[0]), float)
        # The 0Start variables will always be 0 at the beginning to act as loop variables that correspond to the blockHolder size
        alpha0start = 0
        beta0start = 0
        for alpha in range(0 + NValue[0] * blockX, NValue[0] + NValue[0] * blockX):
            for beta in range(0 + NValue[0] * blockY, NValue[0] + NValue[0] * blockY):
                counter = pyfghutil.AlphaAndBetaToCounter(alpha, beta, dimensions, NValue)
                blockHolder[alpha0start, beta0start] = (Vmatrix.Vab(dimensions, NValue, LValue, 0, pes, counter))
                beta0start += 1
            alpha0start += 1
            beta0start = 0
        return blockHolder

    @classmethod
    # The function to calculate a VMatrix using the DataObject class input
    def VMatrixCalc(self, dataObject):
        # Establish variables needed
        NValue = []
        LValue = []
        if (int(dataObject.N1) > 0):
            NValue.append(int(dataObject.N1))
            LValue.append(float(dataObject.L1))
        if (int(dataObject.N2) > 0):
            NValue.append(int(dataObject.N2))
            LValue.append(float(dataObject.L2))
        if (int(dataObject.N3) > 0):
            NValue.append(int(dataObject.N3))
            LValue.append(float(dataObject.L3))

        dimensions = len(NValue)
        pes = dataObject.PES

        dimensionCounterArray = np.zeros((dimensions * 2, 1), int)

        # Create the VMatrix
        # The alpha and beta values are used to create the VMatrix in the correct position
        vmatrix = np.zeros((np.prod(NValue), np.prod(NValue)), float)

        # NBlock Class System
        NBlocks = Vmatrix.NBlock(dimensions, NValue)
        NBlocks.difSetup()

        # Calculate by blocks:
        # Don't optimize for now. Just calculate blocks as needed.
        blockCoords = []
        optBlockCoords = []
        blocks = []
        paramz = []
        totalwidth = int(np.prod(NValue))
        repeatamount = int(totalwidth // NValue[0])
        for x in range(repeatamount):
            for y in range(repeatamount):
                blockCoords.append((x, y))
        optBlockCoords = NBlocks.coordGen()
        for coords in optBlockCoords:
            paramz.append((dimensions, NValue, LValue, pes, coords[0], coords[1]))

        # Pool and run
        p = mp.Pool(dataObject.cores_amount)
        # print("Pool go V")
        blocks = p.starmap(Vmatrix.VBlockCalc, paramz)
        # print("Pool's done V")
        p.close()

        precalc = 0
        for i in range(len(optBlockCoords)):
            block = blocks[i]
            x = optBlockCoords[i][0]
            y = optBlockCoords[i][1]
            NBlocks.setBlock(x, y, block)
        for i in range(len(blockCoords)):
            x = blockCoords[i][0]
            y = blockCoords[i][1]
            vmatrix[(0 + NValue[precalc] * x):(NValue[precalc] + NValue[precalc] * x),
            (0 + NValue[precalc] * y):(NValue[precalc] + NValue[precalc] * y)] = NBlocks.readBlock(x, y)

        return vmatrix


class GUItoCalc:
    def __init__(self):
        print('')

    @classmethod
    def eckartTranslation(self, D, N, equil, pes):
        Nat = equil.getNatom()
        Npts = np.prod(N)
        m = equil.getMassList()
        M = 0.0
        for i in range(3):
            M += m[i]

        for p in range(Npts):
            idx = pyfghutil.PointToIndex(D, N, p)
            mol = pes.getPointByIdx(idx)
            xcm = ycm = zcm = 0.0
            x = mol.getXList()
            y = mol.getYList()
            z = mol.getZList()
            for j in range(Nat):
                xcm += m[j] * x[j]
                ycm += m[j] * y[j]
                zcm += m[j] * z[j]
            xcm = xcm / M
            ycm = ycm / M
            zcm = zcm / M
            for j in range(Nat):
                x[j] = x[j] - xcm
                y[j] = y[j] - ycm
                z[j] = z[j] - zcm
            pes.getPointByIdx(idx).setXList(x)
            pes.getPointByIdx(idx).setYList(y)
            pes.getPointByIdx(idx).setZList(z)
        return

    @classmethod
    def eckartTranslationOld(self, D, N, equil, pes):
        N1 = N[0]
        N2 = N[1]
        N3 = N[2]

        m = equil.getMassList()
        M = 0.0
        for i in range(3):
            M += m[i]

        for i in range(N1):
            for j in range(N2):
                for k in range(N3):
                    xcm = ycm = 0.0
                    x = pes.getPointByN(i, j, k).getXList()
                    y = pes.getPointByN(i, j, k).getYList()
                    for p in range(3):
                        xcm += m[p] * x[p]
                        ycm += m[p] * y[p]
                    xcm = xcm / M
                    ycm = ycm / M
                    xnew = np.zeros(3, float)
                    ynew = np.zeros(3, float)
                    for p in range(3):
                        xnew[p] = x[p] - xcm
                        ynew[p] = y[p] - ycm
                    pes.getPointByN(i, j, k).setXList(xnew)
                    pes.getPointByN(i, j, k).setYList(ynew)
        return

    @classmethod
    def eckartRotation(self, D, N, equil, pes):
        Nat = equil.getNatom()
        Npts = np.prod(N)
        m = equil.getMassList()

        xe = equil.getXList()
        ye = equil.getYList()
        ze = equil.getZList()
        for p in range(Npts):
            idx = pyfghutil.PointToIndex(D, N, p)
            mol = pes.getPointByIdx(idx)
            x = mol.getXList()
            y = mol.getYList()
            z = mol.getZList()

            A = np.zeros((3, 3), dtype=float)
            for i in range(Nat):
                A[0, 0] += m[i] * x[i] * xe[i]
                A[0, 1] += m[i] * x[i] * ye[i]
                A[0, 2] += m[i] * x[i] * ze[i]
                A[1, 0] += m[i] * y[i] * xe[i]
                A[1, 1] += m[i] * y[i] * ye[i]
                A[1, 2] += m[i] * y[i] * ze[i]
                A[2, 0] += m[i] * z[i] * xe[i]
                A[2, 1] += m[i] * z[i] * ye[i]
                A[2, 2] += m[i] * z[i] * ze[i]

            A1 = np.matmul(A.T, A)
            A2 = np.matmul(A, A.T)

            eval1, evec1 = linalg.eig(A1)
            eval2, evec2 = linalg.eig(A2)

            eval1 = np.real(eval1)
            eval2 = np.real(eval2)
            evec1 = evec1.T
            evec2 = evec2.T

            sortidx1 = eval1.argsort()
            sortidx2 = eval2.argsort()
            evec1sort = np.zeros((3, 3), dtype=float)
            evec2sort = np.zeros((3, 3), dtype=float)
            for i in range(3):
                for j in range(3):
                    evec1sort[i, j] = evec1[sortidx1[i], j]
                    evec2sort[i, j] = evec2[sortidx2[i], j]

            cp1 = np.cross(evec1sort[0], evec1sort[1])
            if (np.dot(cp1, evec1sort[2]) < 0):
                evec1sort[2] *= -1.0

            cp2 = np.cross(evec2sort[0], evec2sort[1])
            if (np.dot(cp2, evec2sort[2]) < 0):
                evec2sort[2] *= -1.0

            T = np.zeros((3, 3), dtype=float)
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        T[i, j] += evec1sort[k, i] * evec2sort[k, j]

            xr = np.zeros(Nat, dtype=float)
            yr = np.zeros(Nat, dtype=float)
            zr = np.zeros(Nat, dtype=float)

            for j in range(Nat):
                xr[j] = T[0, 0] * x[j] + T[0, 1] * y[j] + T[0, 2] * z[j]
                yr[j] = T[1, 0] * x[j] + T[1, 1] * y[j] + T[1, 2] * z[j]
                zr[j] = T[2, 0] * x[j] + T[2, 1] * y[j] + T[2, 2] * z[j]

            pes.getPointByIdx(idx).setXList(xr)
            pes.getPointByIdx(idx).setYList(yr)
            pes.getPointByIdx(idx).setZList(zr)
        return

    @classmethod
    def eckartRotationOld(self, D, N, equil, pes):
        N1 = N[0]
        N2 = N[1]
        N3 = N[2]

        m = equil.getMassList()
        xeq = equil.getXList()
        yeq = equil.getYList()
        for i in range(N1):
            for j in range(N2):
                for k in range(N3):
                    x = pes.getPointByN(i, j, k).getXList()
                    y = pes.getPointByN(i, j, k).getYList()
                    numer = denom = 0.0
                    for p in range(3):
                        numer += m[p] * (x[p] * yeq[p] - y[p] * xeq[p])
                        denom += m[p] * (x[p] * xeq[p] + y[p] * yeq[p])
                    theta = math.atan2(numer, denom)
                    xnew = np.zeros(3, float)
                    ynew = np.zeros(3, float)
                    for p in range(3):
                        xnew[p] = x[p] * math.cos(theta) - y[p] * math.sin(theta)
                        ynew[p] = x[p] * math.sin(theta) + y[p] * math.cos(theta)
                    pes.getPointByN(i, j, k).setXList(xnew)
                    pes.getPointByN(i, j, k).setYList(ynew)
        return

    @classmethod
    def main(self):
        pass

    @classmethod
    def passToCalc(self, dataObj):
        # print("Got an object.")
        # print(dataObj)

        D = dataObj.getD()
        N = np.zeros(D, dtype=int)
        N[0] = dataObj.getN1()
        N[1] = dataObj.getN2()
        N[2] = dataObj.getN3()

        equil = dataObj.getEquilMolecule()
        pes = dataObj.getPES()

        print("Imposing Eckart conditions")
        GUItoCalc.eckartTranslation(D, N, equil, pes)
        GUItoCalc.eckartRotation(D, N, equil, pes)

        print("Creating G Matrix")
        GMat = Gmatrix.calcGMatrix(D, N, dataObj.PES, dataObj.EquilMolecule)
        print("Done with G Matrix")
        print("Creating V Matrix")
        VMat = Vmatrix.VMatrixCalc(dataObj)
        print("Done with V Matrix")
        print("Creating T Matrix")
        TMat = Tmatrix.TMatrixCalc(dataObj, GMat)
        print("Done with T Matrix")
        HMat = VMat + TMat

        print("Calculating eigenvalues")
        eigenval, eigenvec = linalg.eigh(HMat)
        eigenval = eigenval * 219474.6

        ResultObj = OutputData()
        ResultObj.setEigenvalues(eigenval)
        ResultObj.setEigenvectors(eigenvec)

        return ResultObj


class moleculetest:
    def __init__(self):
        print('')

    Q1 = []
    Q2 = []
    Q3 = []
    Z = []
    s = []
    A = []
    m = []
    list2 = []
    list3 = []
    x_coordinates = []
    y_coordinates = []
    z_coordinates = []
    mass = []
    potx1 = []
    potx2 = []
    potx3 = []
    poty1 = []
    poty2 = []
    poty3 = []
    potenergy = []
    energy = []
    totalN = 0

    """
    When selecting the files must select first and then select enter N and L values!!!
    """

    @classmethod
    def molecule_testing(self, N1, L1, N2, L2, N3, L3, eqfile, pesfile):
        # print(DataObject.test.equilibrium_file)
        N1_1 = N1
        N2_1 = N2
        N3_1 = N3
        # print(N1_1)
        #    with open(DataObject.test.equilibrium_file) as f:
        with open(eqfile) as f:
            for row in f:
                # print(row)
                moleculetest.list2.append(row.split(',')[0])  # Li
                new_row = ['-'.join([row.split(',')[0], row.split(',')[1]])]
                x = ' '.join(new_row)
                moleculetest.list3.append(x)
                moleculetest.x_coordinates.append(row.split(',')[2])
                moleculetest.y_coordinates.append(row.split(',')[3])
                moleculetest.z_coordinates.append((row.split(',')[4]).strip())
                moleculetest.mass.append(row.split(',')[1])
                masslist = ([float(x) for x in moleculetest.mass])
                # print(list2)  # ['Li']
                # print(list3)  # ['Li-6']
                # print("\n")

            """
            for x in list2:
                print(x)
            """

            for x in moleculetest.list2:  # x is the atomic symbol
                if x in pyfghutil.AtomicSymbolLookup.values():
                    # print(x + " is a valid element")
                    moleculetest.s.append(x)
                else:
                    raise Exception("Atom is not valid")
                    # throw an error

            print("\n")
            for x in moleculetest.list2:  # x is the atomic symbol
                for key, value in pyfghutil.AtomicSymbolLookup.items():
                    if x == value:
                        moleculetest.Z.append(key)
                        # print("Atomic number of " + x + ":", key)

            print("\n")
            for x in moleculetest.list3:  # x is the atomic symbol
                for key, value in pyfghutil.MassLookup.items():
                    if value is masslist:
                        # raise Exception("Atom is not valid")
                        pass
                    """
                    else:
                        raise Exception("Atom is not valid")
                    """
                    if x == key:
                        moleculetest.A.append(value)
                        # print("Atomic mass of " + x + ":", value)
            """
            print("\n")
            for x in list3:
                for key, value in pyfghutil.MassLookup.items():
                    if x == key:
                        print(x + " is a valid element")
                        if value in masslist:
                            print("valid atomic mass")
            """
            for x in moleculetest.A:
                atomic = x * 1822.89
                moleculetest.m.append(atomic)
                # print("amu to atomic ", m)

        def getNs():
            #        file = open(DataObject.test.potential_energy_file)
            file = open(pesfile)
            reader = csv.reader(file)
            lines = len(list(reader))
            f.close()
            totalN_2 = N1_1 * N2_1 * N3_1
            if lines == totalN_2:
                # print("The lines of waterpot-data equals the total of all N vales")
                pass
            else:
                # print("The lines of waterpot-data do not equal the total of all N vales ", lines)
                # raise Exception("N is not valid")
                pass
                # come back and fix this
            return totalN_2

        def calculations(x1, y1, z1, x2, y2, z2, xx2, yy2, zz2, xx3, yy3, zz3):
            d = math.sqrt(math.pow(x2 - x1, 2) +
                          math.pow(y2 - y1, 2) +
                          math.pow(z2 - z1, 2))

            d2 = math.sqrt(math.pow(xx3 - x1, 2) +
                           math.pow(yy3 - y1, 2) +
                           math.pow(zz3 - z1, 2))

            d3 = math.sqrt(math.pow(xx3 - xx2, 2) +
                           math.pow(yy3 - yy2, 2) +
                           math.pow(zz3 - zz2, 2))
            # cos theta equation
            costheta = (((x2 - x1) * (xx3 - x1) + (y2 - y1) * (yy3 - y1) + (z2 - z1) * (zz3 - z1)) / (d * d2))
            # print("Cos Theta is: ", costheta)

            if -1 < costheta < 1:
                # print('molecule is non-linear')
                # print("Cos Theta is: ", costheta)
                pass
            else:
                raise Exception("Molecular is linear")
                # throw an error

            if d >= 0.10 and d2 >= 0.10 and d3 >= 0.10:
                # print("Distance is", d + d2 + d3, " Atom is unique")
                pass
            else:
                raise Exception("Atom is not unique")
                # throw an error

            return

            # First atom is assumed to be the central atom

        xlist = [float(x) for x in moleculetest.x_coordinates]
        ylist = [float(x) for x in moleculetest.y_coordinates]
        zlist = [float(x) for x in moleculetest.z_coordinates]

        # Driver Code
        x1 = xlist[0]
        y1 = ylist[0]
        z1 = zlist[0]
        x2 = xlist[1]
        y2 = ylist[1]
        z2 = zlist[1]

        xx2 = xlist[1]
        yy2 = ylist[1]
        zz2 = zlist[1]
        xx3 = xlist[2]
        yy3 = ylist[2]
        zz3 = zlist[2]

        """
        Splices the data in the waterpot-data.csv file
        """

        def hi():
            holder = InputData()
            r = holder.potential_energy_file
            # print(r)
            #        hola = open(DataObject.test.potential_energy_file)
            #        hola = open(pesfile)
            with open(pesfile) as hola:
                for hello in hola:
                    moleculetest.potx1.append(hello.split(',')[3])
                    moleculetest.potx2.append(hello.split(',')[5])
                    moleculetest.potx3.append(hello.split(',')[7])

                    moleculetest.poty1.append(hello.split(',')[4])
                    moleculetest.poty2.append(hello.split(',')[6])
                    moleculetest.poty3.append(hello.split(',')[8])
                    moleculetest.energy.append(hello.split(',')[9])
            return

        hi()

        potxlist1 = [float(x) for x in moleculetest.potx1]
        potxlist2 = [float(x) for x in moleculetest.potx2]
        potxlist3 = [float(x) for x in moleculetest.potx3]

        potylist1 = [float(x) for x in moleculetest.poty1]
        potylist2 = [float(x) for x in moleculetest.poty2]
        potylist3 = [float(x) for x in moleculetest.poty3]
        potenergy = [float(x) for x in moleculetest.energy]

        """
        This does validation checking. Calculates the distance and the cos theta
        """

        def calculations2(x1, y1, x2, y2, x3, y3):
            d = math.sqrt(math.pow(x2 - x1, 2) +
                          math.pow(y2 - y1, 2))

            d2 = math.sqrt(math.pow(x3 - x1, 2) +
                           math.pow(y3 - y1, 2))

            d3 = math.sqrt(math.pow(x3 - x2, 2) +
                           math.pow(y3 - y2, 2))

            # cos theta equation
            costheta = (((x2 - x1) * (x3 - x1) + (y2 - y1) * (y3 - y1)) / (d * d2))
            # print("Cos Theta is: ", costheta)

            if -1 < costheta < 1:
                # print('molecule is non-linear')
                # print("Cos Theta is: ", costheta)
                pass
            else:
                # print("Molecule is linear")
                raise Exception("Molecule is linear")

            if d >= 0.10 and d2 >= 0.10 and d3 >= 0.10:
                # print("Distance is", d + d2 + d3, " Atom is unique")
                pass
            else:
                # print("Atom is not unique")
                raise Exception("Atom is not unique")

            return

            # First atom is assumed to be the central atom

        """
        This does validation checking for the waterpot-data.csv file
        """
        for x in range(
                len(potxlist1) and len(potxlist2) and len(potxlist3) and len(potylist1) and len(potylist2) and len(
                    potylist3)):
            calculations2(potxlist1[x], potylist1[x], potxlist2[x], potylist2[x], potxlist3[x], potylist3[x])
        """
        print("\n")
        print("WaterPot for x1: ", potxlist1)
        print("WaterPot for x2: ", potxlist2)
        print("WaterPot for x3: ", potxlist3)
        print("WaterPot for y1: ", potylist1)
        print("WaterPot for y2: ", potylist2)
        print("WaterPot for y3: ", potylist3)
        print("\n")
        print("X Coordinates of the elements: ", xlist)
        print("Y Coordinates of the elements: ", ylist)
        print("Z Coordinates of the elements: ", zlist)
        print("\n")
        print("Atomic Number: ", Z)  # Atomic Number
        print("Atomic Mass: ", A)  # Atomic Mass
        print("Symbol: ", s)  # Symbol
        """
        calculations(x1, y1, z1, x2, y2, z2, xx2, yy2, zz2, xx3, yy3, zz3)

        EquilMolecule = pyfghutil.Molecule()
        EquilMolecule.setAtomicNoList(moleculetest.Z)
        EquilMolecule.setMassNoList(moleculetest.A)
        EquilMolecule.setMassList(moleculetest.m)
        EquilMolecule.setXList(xlist)
        EquilMolecule.setYList(ylist)
        EquilMolecule.setZList(np.zeros(3, dtype=float))

        # print("This is from the molecule gui: ", EquilMolecule.Z)
        getNs()

        # validateQ()

        """
        This is for validating the water potential energy file
        """
        N1_2 = N1
        L1_2 = L1
        N2_2 = N2
        L2_2 = L2
        N3_2 = N3
        L3_2 = L3

        deltaQ1 = L1_2 / float(N1_2)
        deltaQ2 = L2_2 / float(N2_2)
        deltaQ3 = L3_2 / float(N3_2)
        #    with open(DataObject.test.potential_energy_file) as a:
        with open(pesfile) as a:
            for x in a:
                moleculetest.Q1.append(float(x.split(',')[0]))
                moleculetest.Q2.append(float(x.split(',')[1]))
                moleculetest.Q3.append(float(x.split(',')[2]))

        pes = PESpoint.PotentialEnergySurface()
        pes.setN([N1, N2, N3])
        pes.setNpts(N1 * N2 * N3)
        n = 0
        for i in range(N1_2):
            for j in range(N2_2):
                for k in range(N3_2):
                    q1 = deltaQ1 * float(i - int(N1_2 / 2))
                    q2 = deltaQ2 * float(j - int(N2_2 / 2))
                    q3 = deltaQ3 * float(k - int(N3_2 / 2))

                    if (round(q1, 3) == round(moleculetest.Q1[n], 3)) \
                            and (round(q2, 3) == round(moleculetest.Q2[n], 3)) \
                            and (round(q3, 3) == round(moleculetest.Q3[n], 3)):
                        pass
                    else:
                        # print(round(q1, 3), round(Q1[n], 3), round(q2, 3), round(Q2[n], 3), round(q3, 3), round(Q3[n], 3))
                        print("Error!!!!!!!!!!!!!!!, File is NOT Valid")
                        os._exit(0)
                        # print('Values are not valid')

                    pt = PESpoint()
                    pt.setN(n)
                    pt.setQList([q1, q2, q3])
                    pt.setXList([potxlist1[n], potxlist2[n], potxlist3[n]])
                    pt.setYList([potylist1[n], potylist2[n], potylist3[n]])
                    pt.setZList([0, 0, 0])
                    pt.setEnergy(potenergy[n])
                    pes.appendPESpt(pt)
                    n += 1

        return EquilMolecule, pes

    @classmethod
    def setMessage(param):
        return None


class run:
    def __init__(self):
        print('')

    @classmethod
    def datamuncher(self, q):
        print('This is the child process: ', os.getpid())
        holder1 = q.get()
        print(holder1.message)

        """
        print("N1: ", holder1.N1)
        print("L1: ", holder1.L1)
        print("N2: ", holder1.N2)
        print("L2: ", holder1.L2)
        print("N3: ", holder1.N3)
        print("L3: ", holder1.L3)
        """

        data = [holder1.equilibrium_file, holder1.N1, holder1.L1, holder1.N2,
                holder1.L2, holder1.N3, holder1.L3]

        save_path = "./resources/"
        file_name = "DataList.txt"
        completeName = os.path.join(save_path, file_name)
        file = open(completeName, "w", encoding="utf-8")
        for x in data:
            file.write('%s\n' % x)
        file.close()

        ReturnObj = GUItoCalc.passToCalc(holder1)
        q.put(ReturnObj)

        return

    # this is the parent process
    @classmethod
    def datagrabber(self):
        q = Queue()
        p1 = Process(target=run.datamuncher, args=(q,))
        p1.start()
        time.sleep(1)

        print('The interface is started Process: ', os.getpid())

        # At this point, insert the data into the handler
        q.put(OutputData)
        ResultObj = q.get()  # an object of type OutputData

        wfnorder = np.argsort(ResultObj.eigenvalues)
        Npts = InputData.getN1() * InputData.getN2() * InputData.getN3()

        # with open("./output files/Eigenvalues.csv", 'w', newline='', encoding='UTF8') as f:
        #     writer = csv.writer(f)
        #     for i in range(Npts):
        #         val = ResultObj.eigenvalues[wfnorder[i]] - ResultObj.eigenvalues[wfnorder[0]]
        #         writer.writerow([val])

        # for i in range(Npts):
        #     val = ResultObj.eigenvalues[wfnorder[i]] - ResultObj.eigenvalues[wfnorder[0]]

        for i in range(1, 11):
            val = ResultObj.eigenvalues[wfnorder[i]] - ResultObj.eigenvalues[wfnorder[0]]
            print(val)

        wfn = np.zeros([Npts, InputData.getN1(), InputData.getN2(), InputData.getN3()], float)

        for p in range(Npts):
            for alpha in range(Npts):
                l = np.mod(alpha, InputData.getN3())
                f = int(alpha / InputData.getN3())
                k = np.mod(f, InputData.getN2())
                f2 = int(f / InputData.getN2())
                j = np.mod(f2, InputData.getN1())

                wfn[p][j][k][l] = ResultObj.eigenvectors[alpha][wfnorder[p]]

        dq1 = InputData.getL1() / float(InputData.getN1())
        dq2 = InputData.getL2() / float(InputData.getN2())
        dq3 = InputData.getL3() / float(InputData.getN3())

        for p in range(0, 21):
            filename = "./output files/Eigenvector-" + str(p) + ".csv"
            with open(filename, 'w', newline='', encoding='UTF8') as f:
                writer = csv.writer(f)

                for n in range(InputData.getN1() * InputData.getN2() * InputData.getN3()):
                    l = np.mod(n, InputData.getN3())
                    f = int(n / InputData.getN3())
                    k = np.mod(f, InputData.getN2())
                    f2 = int(f / InputData.getN2())
                    j = np.mod(f2, InputData.getN1())

                    q1 = dq1 * float(j - int(InputData.getN1() / 2))
                    q2 = dq2 * float(k - int(InputData.getN2() / 2))
                    q3 = dq3 * float(l - int(InputData.getN3() / 2))
                    writer.writerow([q1, q2, q3, wfn[p][j][k][l]])

        return


class test:
    def __init__(self):
        print('')

    @classmethod
    def gethello(cls):
        print('hi')
