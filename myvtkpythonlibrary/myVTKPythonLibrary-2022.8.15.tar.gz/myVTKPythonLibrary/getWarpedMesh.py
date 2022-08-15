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

import vtk

def getWarpedMesh(
        mesh,
        displacement_field_name='displacement'
        ):

    mesh.GetPointData().SetActiveVectors(displacement_field_name)
    warp = vtk.vtkWarpVector()
    warp.SetInputData(mesh)
    warp.Update()
    mesh = warp.GetOutput()

    return mesh
