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

def getSyntheticHelixAngles(
        farray_rr,
        helix_angle_end,
        helix_angle_epi,
        farray_angle_helix=None,
        verbose=1):

    mypy.my_print(verbose, "*** getSyntheticHelixAngles ***")

    n_cells = farray_rr.GetNumberOfTuples()

    if (farray_angle_helix is None):
        farray_angle_helix = myvtk.createFloatArray(
            name="angle_helix",
            n_components=1,
            n_tuples=n_cells)

    for k_cell in range(n_cells):
        rr = farray_rr.GetTuple1(k_cell)

        helix_angle_in_degrees = (1.-rr) * helix_angle_end \
                               +     rr  * helix_angle_epi
        farray_angle_helix.SetTuple1(
            k_cell,
            helix_angle_in_degrees)

    return farray_angle_helix

########################################################################

def addSyntheticHelixAngles(
        ugrid,
        helix_angle_end,
        helix_angle_epi,
        type_of_support="cell",
        verbose=1):

    mypy.my_print(verbose, "*** addSyntheticHelixAngles ***")

    if (type_of_support == "cell"):
        ugrid_data = ugrid.GetCellData()
    elif (type_of_support == "point"):
        ugrid_data = ugrid.GetPointData()

    farray_rr = ugrid_data.GetArray("rr")
    farray_angle_helix = ugrid_data.GetArray("angle_helix")

    farray_angle_helix = getSyntheticHelixAngles(
        farray_rr=farray_rr,
        helix_angle_end=helix_angle_end,
        helix_angle_epi=helix_angle_epi,
        farray_angle_helix=farray_angle_helix,
        verbose=verbose-1)

    ugrid_data.AddArray(farray_angle_helix)

    return farray_angle_helix
