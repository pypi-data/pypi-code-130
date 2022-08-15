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

def getABPointsFromBoundsAndCenter(
        mesh,
        AB=[0,0,1],
        verbose=1):

    mypy.my_print(verbose, "*** getABPointsFromBoundsAndCenter ***")

    C = numpy.array(mesh.GetCenter())
    #mypy.my_print(verbose-1, "C = "+str(C))

    bounds = mesh.GetBounds()
    diag = numpy.array([bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4]])
    AB = numpy.array(AB)
    AB = abs(numpy.dot(diag, AB)) * AB
    #mypy.my_print(verbose-1, "bounds = "+str(bounds))
    #mypy.my_print(verbose-1, "diag = "+str(diag))
    #mypy.my_print(verbose-1, "AB = "+str(AB))

    point_A = C - AB/2
    point_B = C + AB/2
    #mypy.my_print(verbose-1, "point_A = "+str(point_A))
    #mypy.my_print(verbose-1, "point_B = "+str(point_B))

    points_AB = vtk.vtkPoints()
    points_AB.InsertNextPoint(point_A)
    points_AB.InsertNextPoint(point_B)
    #mypy.my_print(verbose-1, "points_AB = "+str(points_AB))

    return points_AB
