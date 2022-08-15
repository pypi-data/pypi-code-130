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

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def getFractionalAnisotropy(
        farray_e1,
        farray_e2,
        farray_e3,
        verbose=1):

    mypy.my_print(verbose, "*** getFractionalAnisotropy ***")

    n_tuples = farray_e1.GetNumberOfTuples()

    farray_FA   = myvtk.createFloatArray("FA"   , 1, n_tuples)
    farray_FA12 = myvtk.createFloatArray("FA_12", 1, n_tuples)
    farray_FA23 = myvtk.createFloatArray("FA_23", 1, n_tuples)

    for k_tuple in range(n_tuples):
        e1 = farray_e1.GetTuple1(k_tuple)
        e2 = farray_e2.GetTuple1(k_tuple)
        e3 = farray_e3.GetTuple1(k_tuple)
        FA   = ((e1-e2)**2+(e1-e3)**2+(e2-e3)**2)**(0.5) / (2*(e1**2+e2**2+e3**2))**(0.5)
        FA12 = ((e1-e2)**2)**(0.5) / (e1**2+e2**2)**(0.5)
        FA23 = ((e2-e3)**2)**(0.5) / (e2**2+e3**2)**(0.5)

        farray_FA.SetTuple1(k_tuple, FA)
        farray_FA12.SetTuple1(k_tuple, FA12)
        farray_FA23.SetTuple1(k_tuple, FA23)

    return (farray_FA,
            farray_FA12,
            farray_FA23)

########################################################################

def addFractionalAnisotropy(
        ugrid,
        field_name,
        type_of_support="cell",
        verbose=1):

    mypy.my_print(verbose, "*** addFractionalAnisotropy ***")

    if (type_of_support == "cell"):
        data = ugrid.GetCellData()
    elif (type_of_support == "point"):
        data = ugrid.GetPointData()

    farray_e1 = data.GetArray(field_name+"_Lmax")
    farray_e2 = data.GetArray(field_name+"_Lmid")
    farray_e3 = data.GetArray(field_name+"_Lmin")

    (farray_FA,
    farray_FA12,
    farray_FA23) = getFractionalAnisotropy(
        farray_e1=farray_e1,
        farray_e2=farray_e2,
        farray_e3=farray_e3,
        verbose=verbose-1)

    farray_FA.SetName(field_name+"_FA")
    farray_FA12.SetName(field_name+"_FA_12")
    farray_FA23.SetName(field_name+"_FA_23")

    data.AddArray(farray_FA)
    data.AddArray(farray_FA12)
    data.AddArray(farray_FA23)

    return (farray_FA,
            farray_FA12,
            farray_FA23)
