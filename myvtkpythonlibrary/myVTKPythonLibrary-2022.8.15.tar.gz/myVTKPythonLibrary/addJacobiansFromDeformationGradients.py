#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2021                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

from builtins import range

import numpy
import vtk

import myPythonLibrary    as mypy
import myVTKPythonLibrary as myvtk

########################################################################

def addJacobiansFromDeformationGradients(
        mesh,
        defo_grad_array_name="DeformationGradient",
        jacobian_array_name="Jacobian",
        verbose=0):

    mypy.my_print(verbose, "*** addJacobiansFromDeformationGradients ***")

    assert (mesh.GetCellData().HasArray(defo_grad_array_name))
    farray_f = mesh.GetCellData().GetArray(defo_grad_array_name)

    n_cells = mesh.GetNumberOfCells()
    farray_jacobian = myvtk.createFloatArray(
        name=jacobian_array_name,
        n_components=1,
        n_tuples=n_cells)
    mesh.GetCellData().AddArray(farray_jacobian)
    for k_cell in range(n_cells):
        F = numpy.reshape(farray_f.GetTuple(k_cell), (3,3), order="C")
        J = numpy.append(numpy.empty(shape=(1,0)), numpy.linalg.det(F))
        farray_jacobian.SetTuple(k_cell, J)
