#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2022                               ###
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

def addEquivDeviatoricStrainsFromDeformationGradients(
        mesh,
        defo_grad_array_name="DeformationGradient",
        equiv_dev_strain_array_basename="EquivDeviatoric",
        verbose=0):

    mypy.my_print(verbose, "*** addEquivDeviatoricStrainsFromDeformationGradients ***")

    assert (mesh.GetCellData().HasArray(defo_grad_array_name))
    farray_f = mesh.GetCellData().GetArray(defo_grad_array_name)

    n_cells = mesh.GetNumberOfCells()
    farray_equiv_Cdev = myvtk.createFloatArray(
        name=equiv_dev_strain_array_basename+"C",
        n_components=1,
        n_tuples=n_cells)
    farray_equiv_Edev = myvtk.createFloatArray(
        name=equiv_dev_strain_array_basename+"E",
        n_components=1,
        n_tuples=n_cells)
    mesh.GetCellData().AddArray(farray_equiv_Cdev)
    mesh.GetCellData().AddArray(farray_equiv_Edev)
    I = numpy.eye(3)
    for k_cell in range(n_cells):
        F = numpy.reshape(farray_f.GetTuple(k_cell), (3,3), order="C")
        F = numpy.linalg.det(F)**(-1./3) * F
        C = numpy.dot(numpy.transpose(F), F)
        E = (C - I)/2.
        c = numpy.append(numpy.empty(shape=(1,0)), numpy.linalg.norm(C)/3)
        e = numpy.append(numpy.empty(shape=(1,0)), numpy.linalg.norm(E))
        farray_equiv_Cdev.SetTuple(k_cell, c)
        farray_equiv_Edev.SetTuple(k_cell, e)
