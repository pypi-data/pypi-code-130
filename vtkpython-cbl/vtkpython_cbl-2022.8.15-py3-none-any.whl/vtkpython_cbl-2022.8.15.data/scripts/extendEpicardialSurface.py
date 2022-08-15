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
import vtk

import myPythonLibrary as mypy
import myVTKPythonLibrary as myvtk

import vtkpython_cbl as cbl

########################################################################

def extendEpicardialSurface(
        pdata_epi,
        dZ=5.,
        verbose=1):

    mypy.my_print(verbose, "*** extendEpicardialSurface ***")

    bounds = pdata_epi.GetBounds()
    Zmin = bounds[4]

    n_points = pdata_epi.GetNumberOfPoints()
    X = numpy.empty(3)
    for k_point in range(n_points):
        pdata_epi.GetPoint(k_point, X)
        if (abs(X[2] - Zmin) < 1e-1):
            X[2] -= dZ
            pdata_epi.GetPoints().SetPoint(k_point, X)

    return pdata_epi


########################################################################

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('epi_filename', type=str)
    parser.add_argument('--dZ', type=float, default=5.)
    parser.add_argument('--verbose', type=int, default=1)
    args = parser.parse_args()

    mypy.my_print(args.verbose, "*** extendEpicardialSurface ***")

    pdata_epi = myvtk.readDataSet(
        filename=args.epi_filename,
        verbose=args.verbose-1)

    cbl.extendEpicardialSurface(
        pdata_epi=pdata_epi,
        verbose=args.verbose-1)

    epi_filename = args.epi_filename.replace(".", "-extended.")

    myvtk.writeDataSet(
        dataset=pdata_epi,
        filename=epi_filename,
        verbose=args.verbose-1)
