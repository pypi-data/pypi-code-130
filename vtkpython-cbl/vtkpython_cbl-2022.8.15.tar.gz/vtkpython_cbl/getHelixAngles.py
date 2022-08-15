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

import math
import numpy

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def getHelixAngles(
        farray_eRR,
        farray_eCC,
        farray_eLL,
        farray_eF,
        verbose=1):

    mypy.my_print(verbose, "*** getHelixAngles ***")

    n_tuples = farray_eRR.GetNumberOfTuples()
    assert (farray_eCC.GetNumberOfTuples() == n_tuples)
    assert (farray_eLL.GetNumberOfTuples() == n_tuples)
    assert (farray_eF.GetNumberOfTuples() == n_tuples)

    farray_angle_helix = myvtk.createFloatArray("angle_helix", 1, n_tuples)

    eRR = numpy.empty(3)
    eCC = numpy.empty(3)
    eLL = numpy.empty(3)
    eF = numpy.empty(3)
    for k_tuple in range(n_tuples):
        farray_eRR.GetTuple(k_tuple, eRR)
        farray_eCC.GetTuple(k_tuple, eCC)
        farray_eLL.GetTuple(k_tuple, eLL)
        farray_eF.GetTuple(k_tuple, eF)
        eF -= numpy.dot(eF, eRR) * eRR
        eF /= numpy.linalg.norm(eF)
        helix_angle = math.copysign(1., numpy.dot(eF, eCC)) * math.asin(min(1., max(-1., numpy.dot(eF, eLL)))) * (180./math.pi)
        farray_angle_helix.SetTuple1(k_tuple, helix_angle)

    return farray_angle_helix

########################################################################

def addHelixAngles(
        ugrid,
        type_of_support="cell",
        verbose=1):

    mypy.my_print(verbose, "*** addHelixAngles ***")

    if (type_of_support == "cell"):
        ugrid_data = ugrid.GetCellData()
    elif (type_of_support == "point"):
        ugrid_data = ugrid.GetPointData()

    farray_eRR = ugrid_data.GetArray("eRR")
    farray_eCC = ugrid_data.GetArray("eCC")
    farray_eLL = ugrid_data.GetArray("eLL")

    farray_eF = ugrid_data.GetArray("eF")

    farray_angle_helix = getHelixAngles(
        farray_eRR=farray_eRR,
        farray_eCC=farray_eCC,
        farray_eLL=farray_eLL,
        farray_eF=farray_eF,
        verbose=verbose-1)

    ugrid_data.AddArray(farray_angle_helix)

    return farray_angle_helix
