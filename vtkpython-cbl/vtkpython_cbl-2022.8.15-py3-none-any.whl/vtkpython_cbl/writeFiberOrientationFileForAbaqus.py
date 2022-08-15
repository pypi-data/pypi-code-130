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

def writeFiberOrientationFileForAbaqus(
        mesh,
        filename,
        eF_field_name="eF",
        eS_field_name="eS",
        sep=", ",
        verbose=1):

    mypy.my_print(verbose, "*** writeFiberOrientationFileForAbaqus ***")

    orientation_file = open(filename, "w")
    orientation_file.write(", 1., 0., 0., 0., 1., 0."+"\n")

    n_cells = mesh.GetNumberOfCells()

    eF_array = mesh.GetCellData().GetArray(eF_field_name)
    eS_array = mesh.GetCellData().GetArray(eS_field_name)
    eF = numpy.empty(3)
    eS = numpy.empty(3)

    for k_cell in range(n_cells):
        eF_array.GetTuple(k_cell, eF)
        eS_array.GetTuple(k_cell, eS)

        line = str(k_cell+1)
        for k in range(3): line += sep + str(eF[k])
        for k in range(3): line += sep + str(eS[k])
        line += "\n"
        orientation_file.write(line)

    orientation_file.close()
