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

def getPseudoProlateSpheroidalCoordinatesAndBasisForLV(
        points,
        farray_c,
        farray_l,
        farray_eL,
        pdata_end,
        pdata_epi,
        iarray_part_id=None,
        verbose=1):

    mypy.my_print(verbose, "*** getPseudoProlateSpheroidalCoordinatesAndBasisForLV ***")

    mypy.my_print(verbose-1, "Computing surface cell normals...")

    myvtk.addPDataNormals(
        pdata=pdata_end,
        verbose=verbose-1)
    myvtk.addPDataNormals(
        pdata=pdata_epi,
        verbose=verbose-1)

    mypy.my_print(verbose-1, "Initializing surface cell locators...")


    (cell_locator_end,
     closest_point_end,
     generic_cell,
     cellId_end,
     subId,
     dist_end) = myvtk.getCellLocator(
         mesh=pdata_end,
         verbose=verbose-1)
    (cell_locator_epi,
     closest_point_epi,
     generic_cell,
     cellId_epi,
     subId,
     dist_epi) = myvtk.getCellLocator(
         mesh=pdata_epi,
         verbose=verbose-1)

    mypy.my_print(verbose-1, "Computing local prolate spheroidal directions...")

    n_points = points.GetNumberOfPoints()

    farray_rr = myvtk.createFloatArray("rr", 1, n_points)
    farray_cc = myvtk.createFloatArray("cc", 1, n_points)
    farray_ll = myvtk.createFloatArray("ll", 1, n_points)

    farray_eRR = myvtk.createFloatArray("eRR", 3, n_points)
    farray_eCC = myvtk.createFloatArray("eCC", 3, n_points)
    farray_eLL = myvtk.createFloatArray("eLL", 3, n_points)

    if (n_points == 0):
        return (farray_rr,
                farray_cc,
                farray_ll,
                farray_eRR,
                farray_eCC,
                farray_eLL)

    c_lst = [farray_c.GetTuple1(k_point) for k_point in range(n_points)]
    c_min = min(c_lst)
    c_max = max(c_lst)

    l_lst = [farray_l.GetTuple1(k_point) for k_point in range(n_points)]
    l_min = min(l_lst)
    l_max = max(l_lst)

    pdata_end_normals = pdata_end.GetCellData().GetNormals()
    pdata_epi_normals = pdata_epi.GetCellData().GetNormals()
    pdata_end_normal = numpy.empty(3)
    pdata_epi_normal = numpy.empty(3)

    eL = numpy.empty(3)

    point = numpy.empty(3)
    for k_point in range(n_points):
        if (iarray_part_id is not None) and (int(iarray_part_id.GetTuple1(k_point)) > 0):
            rr = 0.
            cc = 0.
            ll = 0.
            eRR = numpy.array([1.,0.,0.])
            eCC = numpy.array([0.,1.,0.])
            eLL = numpy.array([0.,0.,1.])

        else:
            points.GetPoint(k_point, point)
            cell_locator_end.FindClosestPoint(
                point,
                closest_point_end,
                generic_cell,
                cellId_end,
                subId,
                dist_end)
            cell_locator_epi.FindClosestPoint(
                point,
                closest_point_epi,
                generic_cell,
                cellId_epi,
                subId,
                dist_epi)

            rr = dist_end/(dist_end+dist_epi)

            c = farray_c.GetTuple1(k_point)
            cc = (c-c_min) / (c_max-c_min)

            l = farray_l.GetTuple1(k_point)
            ll = (l-l_min) / (l_max-l_min)

            pdata_end_normals.GetTuple(cellId_end, pdata_end_normal)
            pdata_epi_normals.GetTuple(cellId_epi, pdata_epi_normal)
            eRR  = (1.-rr) * pdata_end_normal + rr * pdata_epi_normal
            eRR /= numpy.linalg.norm(eRR)

            farray_eL.GetTuple(k_point, eL)
            eCC  = numpy.cross(eL, eRR)
            eCC /= numpy.linalg.norm(eCC)

            eLL = numpy.cross(eRR, eCC)

        farray_rr.SetTuple1(k_point, rr)
        farray_cc.SetTuple1(k_point, cc)
        farray_ll.SetTuple1(k_point, ll)
        farray_eRR.SetTuple(k_point, eRR)
        farray_eCC.SetTuple(k_point, eCC)
        farray_eLL.SetTuple(k_point, eLL)

    return (farray_rr,
            farray_cc,
            farray_ll,
            farray_eRR,
            farray_eCC,
            farray_eLL)

########################################################################

def addPseudoProlateSpheroidalCoordinatesAndBasisToLV(
        ugrid,
        pdata_end,
        pdata_epi,
        verbose=1):

    mypy.my_print(verbose, "*** addPseudoProlateSpheroidalCoordinatesAndBasisToLV ***")

    (farray_rr,
     farray_cc,
     farray_ll,
     farray_eRR,
     farray_eCC,
     farray_eLL) = getPseudoProlateSpheroidalCoordinatesAndBasisForLV(
        points=ugrid.GetPoints(),
        farray_c=ugrid.GetPointData().GetArray("c"),
        farray_l=ugrid.GetPointData().GetArray("l"),
        farray_eL=ugrid.GetPointData().GetArray("eL"),
        pdata_end=pdata_end,
        pdata_epi=pdata_epi,
        iarray_part_id=ugrid.GetPointData().GetArray("part_id"),
        verbose=verbose-1)
    ugrid.GetPointData().AddArray(farray_rr)
    ugrid.GetPointData().AddArray(farray_cc)
    ugrid.GetPointData().AddArray(farray_ll)
    ugrid.GetPointData().AddArray(farray_eRR)
    ugrid.GetPointData().AddArray(farray_eCC)
    ugrid.GetPointData().AddArray(farray_eLL)

    cell_centers = myvtk.getCellCenters(
        mesh=ugrid,
        verbose=verbose-1)
    (farray_rr,
    farray_cc,
    farray_ll,
    farray_eRR,
    farray_eCC,
    farray_eLL) = getPseudoProlateSpheroidalCoordinatesAndBasisForLV(
        points=cell_centers,
        farray_c=ugrid.GetCellData().GetArray("c"),
        farray_l=ugrid.GetCellData().GetArray("l"),
        farray_eL=ugrid.GetCellData().GetArray("eL"),
        pdata_end=pdata_end,
        pdata_epi=pdata_epi,
        iarray_part_id=ugrid.GetCellData().GetArray("part_id"),
        verbose=verbose-1)
    ugrid.GetCellData().AddArray(farray_rr)
    ugrid.GetCellData().AddArray(farray_cc)
    ugrid.GetCellData().AddArray(farray_ll)
    ugrid.GetCellData().AddArray(farray_eRR)
    ugrid.GetCellData().AddArray(farray_eCC)
    ugrid.GetCellData().AddArray(farray_eLL)

########################################################################

def getPseudoProlateSpheroidalCoordinatesAndBasisForBiV(
        points,
        iarray_regions,
        farray_c,
        farray_l,
        farray_eL,
        pdata_endLV,
        pdata_endRV,
        pdata_epi,
        iarray_part_id=None,
        verbose=1):

    mypy.my_print(verbose, "*** getPseudoProlateSpheroidalCoordinatesAndBasisForBiV ***")

    mypy.my_print(verbose-1, "Computing surface cell normals...")

    myvtk.addPDataNormals(
        pdata=pdata_endLV,
        verbose=verbose-1)
    myvtk.addPDataNormals(
        pdata=pdata_endRV,
        verbose=verbose-1)
    myvtk.addPDataNormals(
        pdata=pdata_epi,
        verbose=verbose-1)

    mypy.my_print(verbose-1, "Initializing surface cell locators...")

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

    mypy.my_print(verbose-1, "Computing local prolate spheroidal directions...")

    n_points = points.GetNumberOfPoints()

    farray_rr = myvtk.createFloatArray("rr", 1, n_points)
    farray_cc = myvtk.createFloatArray("cc", 1, n_points)
    farray_ll = myvtk.createFloatArray("ll", 1, n_points)

    farray_eRR = myvtk.createFloatArray("eRR", 3, n_points)
    farray_eCC = myvtk.createFloatArray("eCC", 3, n_points)
    farray_eLL = myvtk.createFloatArray("eLL", 3, n_points)

    c_lst_FWLV = numpy.array([farray_c.GetTuple1(k_point) for k_point in range(n_points) if (iarray_regions.GetTuple1(k_point) == 0)])
    (c_avg_FWLV, c_std_FWLV) = cbl.getMeanStddevAngles(
        angles=c_lst_FWLV,
        angles_in_degrees=False,
        angles_in_pm_pi=False)
    mypy.my_print(verbose-1, "c_avg_FWLV = "+str(c_avg_FWLV))
    c_lst_FWLV = (((c_lst_FWLV-c_avg_FWLV+math.pi)%(2*math.pi))-math.pi+c_avg_FWLV)
    c_min_FWLV = min(c_lst_FWLV)
    c_max_FWLV = max(c_lst_FWLV)
    mypy.my_print(verbose-1, "c_min_FWLV = "+str(c_min_FWLV))
    mypy.my_print(verbose-1, "c_max_FWLV = "+str(c_max_FWLV))

    c_lst_S = numpy.array([farray_c.GetTuple1(k_point) for k_point in range(n_points) if (iarray_regions.GetTuple1(k_point) == 1)])
    (c_avg_S, c_std_S) = cbl.getMeanStddevAngles(
        angles=c_lst_S,
        angles_in_degrees=False,
        angles_in_pm_pi=False)
    mypy.my_print(verbose-1, "c_avg_S = "+str(c_avg_S))
    c_lst_S = (((c_lst_S-c_avg_S+math.pi)%(2*math.pi))-math.pi+c_avg_S)
    c_min_S = min(c_lst_S)
    c_max_S = max(c_lst_S)
    mypy.my_print(verbose-1, "c_min_S = "+str(c_min_S))
    mypy.my_print(verbose-1, "c_max_S = "+str(c_max_S))

    c_lst_FWRV = numpy.array([farray_c.GetTuple1(k_point) for k_point in range(n_points) if (iarray_regions.GetTuple1(k_point) == 2)])
    (c_avg_FWRV, c_std_FWRV) = cbl.getMeanStddevAngles(
        angles=c_lst_FWRV,
        angles_in_degrees=False,
        angles_in_pm_pi=False)
    mypy.my_print(verbose-1, "c_avg_FWRV = "+str(c_avg_FWRV))
    c_lst_FWRV = (((c_lst_FWRV-c_avg_FWRV+math.pi)%(2*math.pi))-math.pi+c_avg_FWRV)
    c_min_FWRV = min(c_lst_FWRV)
    c_max_FWRV = max(c_lst_FWRV)
    mypy.my_print(verbose-1, "c_min_FWRV = "+str(c_min_FWRV))
    mypy.my_print(verbose-1, "c_max_FWRV = "+str(c_max_FWRV))

    l_lst = [farray_l.GetTuple1(k_point) for k_point in range(n_points)]
    l_min = min(l_lst)
    l_max = max(l_lst)

    point = numpy.empty(3)
    for k_point in range(n_points):
        if (iarray_part_id is not None) and (int(iarray_part_id.GetTuple1(k_point)) > 0):
            rr = 0.
            cc = 0.
            ll = 0.
            eRR = [1.,0.,0.]
            eCC = [0.,1.,0.]
            eLL = [0.,0.,1.]

        else:
            points.GetPoint(k_point, point)
            region_id = iarray_regions.GetTuple1(k_point)

            if (region_id == 0):
                cell_locator_endLV.FindClosestPoint(
                    point,
                    closest_point_endLV,
                    generic_cell,
                    cellId_endLV,
                    subId,
                    dist_endLV)
                cell_locator_epi.FindClosestPoint(
                    point,
                    closest_point_epi,
                    generic_cell,
                    cellId_epi,
                    subId,
                    dist_epi)

                rr = dist_endLV/(dist_endLV+dist_epi)

                c = farray_c.GetTuple1(k_point)
                c = (((c-c_avg_FWLV+math.pi)%(2*math.pi))-math.pi+c_avg_FWLV)
                cc = (c-c_min_FWLV) / (c_max_FWLV-c_min_FWLV)

                l = farray_l.GetTuple1(k_point)
                ll = (l-l_min) / (l_max-l_min)

                normal_endLV = numpy.reshape(pdata_endLV.GetCellData().GetNormals().GetTuple(cellId_endLV), (3))
                normal_epi = numpy.reshape(pdata_epi.GetCellData().GetNormals().GetTuple(cellId_epi), (3))
                eRR  = (1.-rr) * normal_endLV + rr * normal_epi
                eRR /= numpy.linalg.norm(eRR)

                eL = numpy.reshape(farray_eL.GetTuple(k_point), (3))
                eCC  = numpy.cross(eL, eRR)
                eCC /= numpy.linalg.norm(eCC)

                eLL  = numpy.cross(eRR, eCC)
            elif (region_id == 1):
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

                rr = dist_endLV/(dist_endLV+dist_endRV)

                c = farray_c.GetTuple1(k_point)
                c = (((c-c_avg_S+math.pi)%(2*math.pi))-math.pi+c_avg_S)
                cc = (c-c_min_S) / (c_max_S-c_min_S)

                l = farray_l.GetTuple1(k_point)
                ll = (l-l_min) / (l_max-l_min)

                normal_endLV = numpy.reshape(pdata_endLV.GetCellData().GetNormals().GetTuple(cellId_endLV), (3))
                normal_endRV = numpy.reshape(pdata_endRV.GetCellData().GetNormals().GetTuple(cellId_endRV), (3))
                eRR  = (1.-rr) * normal_endLV - rr * normal_endRV
                eRR /= numpy.linalg.norm(eRR)

                eL = numpy.reshape(farray_eL.GetTuple(k_point), (3))
                eCC  = numpy.cross(eL, eRR)
                eCC /= numpy.linalg.norm(eCC)

                eLL = numpy.cross(eRR, eCC)
            if (region_id == 2):
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

                rr = dist_endRV/(dist_endRV+dist_epi)

                c = farray_c.GetTuple1(k_point)
                c = (((c-c_avg_FWRV+math.pi)%(2*math.pi))-math.pi+c_avg_FWRV)
                cc = (c-c_min_FWRV) / (c_max_FWRV-c_min_FWRV)

                l = farray_l.GetTuple1(k_point)
                ll = (l-l_min) / (l_max-l_min)

                normal_endRV = numpy.reshape(pdata_endRV.GetCellData().GetNormals().GetTuple(cellId_endRV), (3))
                normal_epi = numpy.reshape(pdata_epi.GetCellData().GetNormals().GetTuple(cellId_epi), (3))
                eRR  = (1.-rr) * normal_endRV + rr * normal_epi
                eRR /= numpy.linalg.norm(eRR)

                eL = numpy.reshape(farray_eL.GetTuple(k_point), (3))
                eCC  = numpy.cross(eL, eRR)
                eCC /= numpy.linalg.norm(eCC)

                eLL = numpy.cross(eRR, eCC)

        farray_rr.SetTuple1(k_point, rr)
        farray_cc.SetTuple1(k_point, cc)
        farray_ll.SetTuple1(k_point, ll)
        farray_eRR.SetTuple(k_point, eRR)
        farray_eCC.SetTuple(k_point, eCC)
        farray_eLL.SetTuple(k_point, eLL)

    return (farray_rr,
            farray_cc,
            farray_ll,
            farray_eRR,
            farray_eCC,
            farray_eLL)

########################################################################

def addPseudoProlateSpheroidalCoordinatesAndBasisToBiV(
        ugrid,
        pdata_endLV,
        pdata_endRV,
        pdata_epi,
        verbose=1):

    mypy.my_print(verbose, "*** addPseudoProlateSpheroidalCoordinatesAndBasisToBiV ***")

    (farray_rr,
     farray_cc,
     farray_ll,
     farray_eRR,
     farray_eCC,
     farray_eLL) = getPseudoProlateSpheroidalCoordinatesAndBasisForBiV(
        points=ugrid.GetPoints(),
        iarray_regions=ugrid.GetPointData().GetArray("region_id"),
        farray_c=ugrid.GetPointData().GetArray("c"),
        farray_l=ugrid.GetPointData().GetArray("l"),
        farray_eL=ugrid.GetPointData().GetArray("eL"),
        pdata_endLV=pdata_endLV,
        pdata_endRV=pdata_endRV,
        pdata_epi=pdata_epi,
        iarray_part_id=ugrid.GetPointData().GetArray("part_id"),
        verbose=verbose-1)
    ugrid.GetPointData().AddArray(farray_rr)
    ugrid.GetPointData().AddArray(farray_cc)
    ugrid.GetPointData().AddArray(farray_ll)
    ugrid.GetPointData().AddArray(farray_eRR)
    ugrid.GetPointData().AddArray(farray_eCC)
    ugrid.GetPointData().AddArray(farray_eLL)

    cell_centers = myvtk.getCellCenters(
        mesh=ugrid,
        verbose=verbose-1)
    (farray_rr,
     farray_cc,
     farray_ll,
     farray_eRR,
     farray_eCC,
     farray_eLL) = getPseudoProlateSpheroidalCoordinatesAndBasisForBiV(
        points=cell_centers,
        iarray_regions=ugrid.GetCellData().GetArray("region_id"),
        farray_c=ugrid.GetCellData().GetArray("c"),
        farray_l=ugrid.GetCellData().GetArray("l"),
        farray_eL=ugrid.GetCellData().GetArray("eL"),
        pdata_endLV=pdata_endLV,
        pdata_endRV=pdata_endRV,
        pdata_epi=pdata_epi,
        iarray_part_id=ugrid.GetCellData().GetArray("part_id"),
        verbose=verbose-1)
    ugrid.GetCellData().AddArray(farray_rr)
    ugrid.GetCellData().AddArray(farray_cc)
    ugrid.GetCellData().AddArray(farray_ll)
    ugrid.GetCellData().AddArray(farray_eRR)
    ugrid.GetCellData().AddArray(farray_eCC)
    ugrid.GetCellData().AddArray(farray_eLL)
