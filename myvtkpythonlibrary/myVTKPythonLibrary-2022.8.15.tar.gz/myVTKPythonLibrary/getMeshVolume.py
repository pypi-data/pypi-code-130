#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2021                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
###                                                                  ###
### And Cécile Patte, 2020                                           ###
###                                                                  ###
### INRIA, Palaiseau, France                                         ###
###                                                                  ###
########################################################################

import myVTKPythonLibrary as myvtk
import vtk

def getMeshVolume(
        mesh,
        warp_mesh=1
        ):

    if warp_mesh == 1:
        warp = vtk.vtkWarpVector()
        warp.SetInputData(mesh)
        warp.Update()
        mesh = warp.GetOutput()

    polydata = myvtk.ugrid2pdata(mesh)
    mass = myvtk.getMassProperties(polydata)
    volume = mass.GetVolume()

    return volume
