#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2019                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

from builtins import range

import numpy

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def readAbaqusFibersFromINP(
        filename,
        verbose=1):

    mypy.my_print(verbose, "*** readAbaqusFibersFromINP: "+filename+" ***")

    eF_array = myvtk.createFloatArray('eF', 3)
    eS_array = myvtk.createFloatArray('eS', 3)
    eN_array = myvtk.createFloatArray('eN', 3)

    file = open(filename, 'r')
    file.readline()

    for line in file:
        line = line.split(', ')
        #print(line)

        eF = [float(item) for item in line[1:4]]
        eS = [float(item) for item in line[4:7]]
        eN = numpy.cross(eF,eS)
        #print("eF =", eF)
        #print("eS =", eS)
        #print("eN =", eN)

        eF_array.InsertNextTuple(eF)
        eS_array.InsertNextTuple(eS)
        eN_array.InsertNextTuple(eN)

    file.close()

    mypy.my_print(verbose-1, "n_tuples = "+str(eF_array.GetNumberOfTuples()))

    return (eF_array,
            eS_array,
            eN_array)
