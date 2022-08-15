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

def getCylindricalCoordinatesAndBasis(
        points,
        points_AB,
        verbose=1):

    mypy.my_print(verbose, "*** getCylindricalCoordinatesAndBasis ***")

    assert (points_AB.GetNumberOfPoints() >= 2), "points_AB must have at least two points. Aborting."
    point_A = numpy.empty(3)
    point_B = numpy.empty(3)
    points_AB.GetPoint(                              0, point_A)
    points_AB.GetPoint(points_AB.GetNumberOfPoints()-1, point_B)
    eL  = point_B - point_A
    eL /= numpy.linalg.norm(eL)
    mypy.my_print(verbose-1, "eL = "+str(eL))

    point_C = point_A+numpy.array([1.,0.,0.])
    #point_C = numpy.empty(3)
    #points.GetPoint(0, point_C)

    AC  = point_C - point_A
    AD  = numpy.cross(eL, AC)
    AD /= numpy.linalg.norm(AD)
    AC  = numpy.cross(AD, eL)

    n_points = points.GetNumberOfPoints()

    farray_r = myvtk.createFloatArray("r", 1, n_points)
    farray_c = myvtk.createFloatArray("c", 1, n_points)
    farray_l = myvtk.createFloatArray("l", 1, n_points)

    farray_eR = myvtk.createFloatArray("eR", 3, n_points)
    farray_eC = myvtk.createFloatArray("eC", 3, n_points)
    farray_eL = myvtk.createFloatArray("eL", 3, n_points)

    point = numpy.empty(3)
    for k_point in range(n_points):
        mypy.my_print(verbose-2, "k_point = "+str(k_point))

        points.GetPoint(k_point, point)

        mypy.my_print(verbose-2, "point = "+str(point))

        eR  = point - point_A
        eC  = numpy.cross(eL, eR)
        eC /= numpy.linalg.norm(eC)
        eR  = numpy.cross(eC, eL)

        farray_eR.SetTuple(k_point, eR)
        farray_eC.SetTuple(k_point, eC)
        farray_eL.SetTuple(k_point, eL)

        r = numpy.dot(point - point_A, eR)
        farray_r.SetTuple1(k_point, r)

        c  = math.atan2(numpy.dot(eR, AD), numpy.dot(eR, AC))
        c += (c<0.)*(2*math.pi)
        farray_c.SetTuple1(k_point, c)

        l = numpy.dot(point - point_A, eL)
        farray_l.SetTuple1(k_point, l)

    return (farray_r,
            farray_c,
            farray_l,
            farray_eR,
            farray_eC,
            farray_eL)

########################################################################

def addCylindricalCoordinatesAndBasis(
        ugrid,
        points_AB,
        verbose=1):

    mypy.my_print(verbose, "*** addCylindricalCoordinatesAndBasis ***")

    points = ugrid.GetPoints()
    (farray_r,
     farray_c,
     farray_l,
     farray_eR,
     farray_eC,
     farray_eL) = getCylindricalCoordinatesAndBasis(
        points=points,
        points_AB=points_AB,
        verbose=verbose-1)

    ugrid.GetPointData().AddArray(farray_r)
    ugrid.GetPointData().AddArray(farray_c)
    ugrid.GetPointData().AddArray(farray_l)
    ugrid.GetPointData().AddArray(farray_eR)
    ugrid.GetPointData().AddArray(farray_eC)
    ugrid.GetPointData().AddArray(farray_eL)

    cell_centers = myvtk.getCellCenters(
        mesh=ugrid,
        verbose=verbose-1)
    (farray_r,
     farray_c,
     farray_l,
     farray_eR,
     farray_eC,
     farray_eL) = getCylindricalCoordinatesAndBasis(
        points=cell_centers,
        points_AB=points_AB,
        verbose=verbose-1)

    ugrid.GetCellData().AddArray(farray_r)
    ugrid.GetCellData().AddArray(farray_c)
    ugrid.GetCellData().AddArray(farray_l)
    ugrid.GetCellData().AddArray(farray_eR)
    ugrid.GetCellData().AddArray(farray_eC)
    ugrid.GetCellData().AddArray(farray_eL)
