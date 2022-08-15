#!python
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

import argparse
import vtk

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def clipSurfacesForFullBiVMesh(
        pdata_endLV,
        pdata_endRV,
        pdata_epi,
        verbose=1):

    mypy.my_print(verbose, "*** clipSurfacesForFullBiVMesh ***")

    pdata_endLV_implicit_distance = vtk.vtkImplicitPolyDataDistance()
    pdata_endLV_implicit_distance.SetInput(pdata_endLV)

    pdata_endRV_implicit_distance = vtk.vtkImplicitPolyDataDistance()
    pdata_endRV_implicit_distance.SetInput(pdata_endRV)

    pdata_epi_implicit_distance = vtk.vtkImplicitPolyDataDistance()
    pdata_epi_implicit_distance.SetInput(pdata_epi)

    pdata_endLV_clip = vtk.vtkClipPolyData()
    if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
        pdata_endLV_clip.SetInputData(pdata_endLV)
    else:
        pdata_endLV_clip.SetInput(pdata_endLV)
    pdata_endLV_clip.SetClipFunction(pdata_epi_implicit_distance)
    pdata_endLV_clip.InsideOutOn()
    pdata_endLV_clip.Update()
    clipped_pdata_endLV = pdata_endLV_clip.GetOutput(0)

    pdata_endRV_clip = vtk.vtkClipPolyData()
    if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
        pdata_endRV_clip.SetInputData(pdata_endRV)
    else:
        pdata_endRV_clip.SetInput(pdata_endRV)
    pdata_endRV_clip.SetClipFunction(pdata_epi_implicit_distance)
    pdata_endRV_clip.InsideOutOn()
    pdata_endRV_clip.Update()
    clipped_pdata_endRV = pdata_endRV_clip.GetOutput(0)

    pdata_epi_clip = vtk.vtkClipPolyData()
    if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
        pdata_epi_clip.SetInputData(pdata_epi)
    else:
        pdata_epi_clip.SetInput(pdata_epi)
    pdata_epi_clip.SetClipFunction(pdata_endLV_implicit_distance)
    pdata_epi_clip.GenerateClippedOutputOn()
    pdata_epi_clip.Update()
    clipped_pdata_epi = pdata_epi_clip.GetOutput(0)
    clipped_valM = pdata_epi_clip.GetOutput(1)

    pdata_epi_clip = vtk.vtkClipPolyData()
    if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
        pdata_epi_clip.SetInputData(clipped_pdata_epi)
    else:
        pdata_epi_clip.SetInput(clipped_pdata_epi)
    pdata_epi_clip.SetClipFunction(pdata_endRV_implicit_distance)
    pdata_epi_clip.GenerateClippedOutputOn()
    pdata_epi_clip.Update()
    clipped_pdata_epi = pdata_epi_clip.GetOutput(0)
    clipped_valP = pdata_epi_clip.GetOutput(1)

    return (clipped_pdata_endLV,
            clipped_pdata_endRV,
            clipped_pdata_epi,
            clipped_valM,
            clipped_valP)

########################################################################

if (__name__ == "__main__"):

    parser = argparse.ArgumentParser()
    parser.add_argument('endLV_filename', type=str)
    parser.add_argument('endRV_filename', type=str)
    parser.add_argument('epi_filename', type=str)
    parser.add_argument('-v', '--verbose', type=int, default=1)
    args = parser.parse_args()

    mypy.my_print(args.verbose, "*** clipSurfacesForFullBiVMesh ***")

    pdata_endLV = myvtk.readPData(
        filename=args.endLV_filename,
        verbose=args.verbose-1)
    pdata_endRV = myvtk.readPData(
        filename=endRV_filename,
        verbose=args.verbose-1)
    pdata_epi = myvtk.readPData(
        filename=args.epi_filename,
        verbose=args.verbose-1)

    (clipped_pdata_endLV,
     clipped_pdata_endRV,
     clipped_pdata_epi,
     clipped_valM,
     clipped_valP) = cbl.clipSurfacesForFullBiVMesh(
        pdata_endLV=pdata_endLV,
        pdata_endRV=pdata_endRV,
        pdata_epi=pdata_epi,
        verbose=args.verbose-1)

    myvtk.writeSTL(
        pdata=clipped_pdata_endLV,
        filename="endLV.stl",
        verbose=args.verbose-1)
    myvtk.writeSTL(
        pdata=clipped_pdata_endRV,
        filename="endRV.stl",
        verbose=args.verbose-1)
    myvtk.writeSTL(
        pdata=clipped_pdata_epi,
        filename="epi.stl",
        verbose=args.verbose-1)
    myvtk.writeSTL(
        pdata=clipped_pdata_valM,
        filename="valM.stl",
        verbose=args.verbose-1)
    myvtk.writeSTL(
        pdata=clipped_pdata_valP,
        filename="valP.stl",
        verbose=args.verbose-1)
