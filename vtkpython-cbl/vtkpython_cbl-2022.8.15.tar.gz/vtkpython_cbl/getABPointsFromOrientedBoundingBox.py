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
import vtk

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def getABPointsFromOrientedBoundingBox(
        mesh,
        verbose=1):

    mypy.my_print(verbose, "*** getABPointsFromOrientedBoundingBox ***")

    center = numpy.array(mesh.GetCenter())

    res_corner = numpy.empty(3)
    res_max    = numpy.empty(3)
    res_mid    = numpy.empty(3)
    res_min    = numpy.empty(3)
    res_size   = numpy.empty(3)
    obb_tree = vtk.vtkOBBTree()
    obb_tree.ComputeOBB(
        mesh,
        res_corner,
        res_max,
        res_mid,
        res_min,
        res_size)
    mypy.my_print(verbose-1, "res_corner = "+str(res_corner))
    mypy.my_print(verbose-1, "res_max = "+str(res_max))
    mypy.my_print(verbose-1, "res_mid = "+str(res_mid))
    mypy.my_print(verbose-1, "res_min = "+str(res_min))
    mypy.my_print(verbose-1, "res_size = "+str(res_size))

    point_A = res_corner + numpy.dot(center-res_corner, res_min/numpy.linalg.norm(res_min)) * res_min/numpy.linalg.norm(res_min) + numpy.dot(center-res_corner, res_mid/numpy.linalg.norm(res_mid)) * res_mid/numpy.linalg.norm(res_mid)
    point_B = point_A + res_max
    mypy.my_print(verbose-1, "point_A = "+str(point_A))
    mypy.my_print(verbose-1, "point_B = "+str(point_B))
    mypy.my_print(verbose-1, "AB = "+str(point_B-point_A))

    points_AB = vtk.vtkPoints()
    points_AB.InsertNextPoint(point_A)
    points_AB.InsertNextPoint(point_B)
    #mypy.my_print(verbose-1, "points_AB = "+str(points_AB))

    return points_AB
