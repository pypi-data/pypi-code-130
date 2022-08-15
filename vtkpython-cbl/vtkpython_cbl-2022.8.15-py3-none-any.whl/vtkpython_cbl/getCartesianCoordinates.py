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

def getCartesianCoordinates(
        points,
        verbose=1):

    mypy.my_print(verbose, "*** getCartesianCoordinates ***")

    n_points = points.GetNumberOfPoints()

    [xmin, xmax, ymin, ymax, zmin, zmax] = points.GetBounds()
    dx = xmax-xmin
    dy = ymax-ymin
    dz = zmax-zmin
    mypy.my_print(verbose-1, "xmin = "+str(xmin))
    mypy.my_print(verbose-1, "xmax = "+str(xmax))
    mypy.my_print(verbose-1, "dx = "+str(dx))
    mypy.my_print(verbose-1, "ymin = "+str(ymin))
    mypy.my_print(verbose-1, "ymax = "+str(ymax))
    mypy.my_print(verbose-1, "dy = "+str(dy))
    mypy.my_print(verbose-1, "zmin = "+str(zmin))
    mypy.my_print(verbose-1, "zmax = "+str(zmax))
    mypy.my_print(verbose-1, "dz = "+str(dz))

    farray_xx = myvtk.createFloatArray("xx", 1, n_points)
    farray_yy = myvtk.createFloatArray("yy", 1, n_points)
    farray_zz = myvtk.createFloatArray("zz", 1, n_points)

    point = numpy.empty(3)
    for k_point in range(n_points):
        mypy.my_print(verbose-2, "k_point = "+str(k_point))

        points.GetPoint(k_point, point)
        mypy.my_print(verbose-2, "point = "+str(point))

        xx = (point[0] - xmin) / dx
        yy = (point[1] - ymin) / dy
        zz = (point[2] - zmin) / dz

        farray_xx.SetTuple1(k_point, xx)
        farray_yy.SetTuple1(k_point, yy)
        farray_zz.SetTuple1(k_point, zz)

    return (farray_xx,
            farray_yy,
            farray_zz)

########################################################################

def addCartesianCoordinates(
        ugrid,
        verbose=1):

    mypy.my_print(verbose, "*** addCartesianCoordinates ***")

    points = ugrid.GetPoints()
    (farray_xx,
     farray_yy,
     farray_zz) = getCartesianCoordinates(
        points=points,
        verbose=verbose-1)

    ugrid.GetPointData().AddArray(farray_xx)
    ugrid.GetPointData().AddArray(farray_yy)
    ugrid.GetPointData().AddArray(farray_zz)

    cell_centers = myvtk.getCellCenters(
        mesh=ugrid,
        verbose=verbose-1)
    (farray_xx,
     farray_yy,
     farray_zz) = getCartesianCoordinates(
        points=cell_centers,
        verbose=verbose-1)

    ugrid.GetCellData().AddArray(farray_xx)
    ugrid.GetCellData().AddArray(farray_yy)
    ugrid.GetCellData().AddArray(farray_zz)
