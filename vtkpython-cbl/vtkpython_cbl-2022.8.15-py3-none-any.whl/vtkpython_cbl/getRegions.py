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

def getRegionsForBiV(
        points,
        pdata_endLV,
        pdata_endRV,
        pdata_epi,
        verbose=1):

    mypy.my_print(verbose, "*** getRegionsForBiV ***")

    mypy.my_print(verbose-1, "Initializing cell locators...")

    (cell_locator_endLV,
     closest_point_endLV,
     generic_cell,
     cellId_endLV,
     subId,
     dist_endLV) = myvtk.getCellLocator(
         mesh=pdata_endLV,
         verbose=verbose-1)
    (cell_locator_endRV,
     closest_point_endRV,
     generic_cell,
     cellId_endRV,
     subId,
     dist_endRV) = myvtk.getCellLocator(
         mesh=pdata_endRV,
         verbose=verbose-1)
    (cell_locator_epi,
     closest_point_epi,
     generic_cell,
     cellId_epi,
     subId,
     dist_epi) = myvtk.getCellLocator(
         mesh=pdata_epi,
         verbose=verbose-1)

    n_points = points.GetNumberOfPoints()

    iarray_region = myvtk.createIntArray("region_id", 1, n_points)

    point = numpy.empty(3)
    for k_point in range(n_points):
        points.GetPoint(k_point, point)
        cell_locator_endLV.FindClosestPoint(
            point,
            closest_point_endLV,
            generic_cell,
            cellId_endLV,
            subId,
            dist_endLV)
        cell_locator_endRV.FindClosestPoint(
            point,
            closest_point_endRV,
            generic_cell,
            cellId_endRV,
            subId,
            dist_endRV)
        cell_locator_epi.FindClosestPoint(
            point,
            closest_point_epi,
            generic_cell,
            cellId_epi,
            subId,
            dist_epi)

        if   (dist_endRV == max(dist_endLV, dist_endRV, dist_epi)):
            iarray_region.SetTuple1(k_point, 0)
        elif (dist_epi == max(dist_endLV, dist_endRV, dist_epi)):
            iarray_region.SetTuple1(k_point, 1)
        elif (dist_endLV == max(dist_endLV, dist_endRV, dist_epi)):
            iarray_region.SetTuple1(k_point, 2)

    return iarray_region

########################################################################

def addRegionsToBiV(
        ugrid_mesh,
        pdata_endLV,
        pdata_endRV,
        pdata_epi,
        verbose=1):

    mypy.my_print(verbose, "*** addRegionsToBiV ***")

    points = ugrid_mesh.GetPoints()
    iarray_region = getRegionsForBiV(
        points=points,
        pdata_endLV=pdata_endLV,
        pdata_endRV=pdata_endRV,
        pdata_epi=pdata_epi,
        verbose=verbose-1)
    ugrid_mesh.GetPointData().AddArray(iarray_region)

    cell_centers = myvtk.getCellCenters(
        mesh=ugrid_mesh,
        verbose=verbose-1)
    iarray_region = getRegionsForBiV(
        points=cell_centers,
        pdata_endLV=pdata_endLV,
        pdata_endRV=pdata_endRV,
        pdata_epi=pdata_epi,
        verbose=verbose-1)
    ugrid_mesh.GetCellData().AddArray(iarray_region)

########################################################################
