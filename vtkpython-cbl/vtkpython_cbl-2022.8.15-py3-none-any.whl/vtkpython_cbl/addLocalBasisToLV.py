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
import numpy

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filename', type=str)
    parser.add_argument('--end_filename', type=str, default=None)
    parser.add_argument('--epi_filename', type=str, default=None)
    parser.add_argument('--n_sectors_r', type=int, default=1)
    parser.add_argument('--n_sectors_c', type=int, default=1)
    parser.add_argument('--n_sectors_l', type=int, default=1)
    parser.add_argument('--getABPointsFrom', type=str, default="BoundsAndCenter")
    parser.add_argument('-v', '--verbose', type=int, default=1)
    args = parser.parse_args()

    mypy.my_print(args.verbose, "*** addLocalBasisToLV ***")

    ugrid_mesh = myvtk.readUGrid(
        filename=args.mesh_filename,
        verbose=args.verbose-1)

    cbl.addCartesianCoordinates(
        ugrid=ugrid_mesh,
        verbose=args.verbose-1)

    if (args.end_filename == None):
        args.end_filename = args.mesh_filename.replace("LV", "EndLV").replace(".vtk", ".stl").replace(".vtu", ".stl")
    if (args.epi_filename == None):
        args.epi_filename = args.mesh_filename.replace("LV", "EpiLV").replace(".vtk", ".stl").replace(".vtu", ".stl")

    pdata_end = myvtk.readPData(
        filename=args.end_filename,
        verbose=args.verbose-1)
    pdata_epi = myvtk.readPData(
        filename=args.epi_filename,
        verbose=args.verbose-1)

    if (args.getABPointsFrom == "BoundsAndCenter"):
        points_AB = cbl.getABPointsFromBoundsAndCenter(
            mesh=pdata_epi,
            AB=[0,0,1],
            verbose=args.verbose-1)
    elif (args.getABPointsFrom == "OrientedBoundingBox"):
        points_AB = cbl.getABPointsFromOrientedBoundingBox(
            mesh=pdata_epi,
            verbose=args.verbose-1)
    else:
        assert (0)

    cbl.addCylindricalCoordinatesAndBasis(
        ugrid=ugrid_mesh,
        points_AB=points_AB,
        verbose=args.verbose-1)

    cbl.addPseudoProlateSpheroidalCoordinatesAndBasisToLV(
        ugrid=ugrid_mesh,
        pdata_end=pdata_end,
        pdata_epi=pdata_epi,
        verbose=args.verbose-1)

    cbl.addSectorsToLV(
        ugrid=ugrid_mesh,
        n_r=args.n_sectors_r,
        n_c=args.n_sectors_c,
        n_l=args.n_sectors_l,
        verbose=args.verbose-1)

    filename = args.mesh_filename.replace(".vtk", "-WithLocalBasis.vtk").replace(".vtu", "-WithLocalBasis.vtu")

    myvtk.writeUGrid(
        ugrid=ugrid_mesh,
        filename=filename,
        verbose=args.verbose-1)
