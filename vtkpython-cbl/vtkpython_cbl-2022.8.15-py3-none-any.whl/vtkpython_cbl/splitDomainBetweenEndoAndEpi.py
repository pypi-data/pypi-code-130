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

def splitDomainBetweenEndoAndEpi(
        pdata_domain,
        r=None,
        verbose=1):

    mypy.my_print(verbose, "*** splitDomainBetweenEndoAndEpi ***")

    if (r == None):
        dr = 1e-2
        r_list = numpy.arange(1.-dr, 0., -dr)
    else:
        assert (r > 0.)
        assert (r < 1.)
        r_list = [r]

    bounds = pdata_domain.GetBounds()
    for r in r_list:
        mypy.my_print(verbose-1, "r = "+str(r))

        origin = [(1./2)*bounds[0]+(1./2)*bounds[1],
                  (1./2)*bounds[2]+(1./2)*bounds[3],
                  (1.-r)*bounds[4]+(  r )*bounds[5]]

        pdata_clipped_domain = myvtk.getClippedPDataUsingPlane(
             pdata_mesh=pdata_domain,
             plane_O=origin,
             plane_N=[0,0,-1],
             verbose=verbose-1)

        connectivity = vtk.vtkPolyDataConnectivityFilter()
        connectivity.SetExtractionModeToAllRegions()
        connectivity.ColorRegionsOn()
        if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
            connectivity.SetInputData(pdata_clipped_domain)
        else:
            connectivity.SetInput(pdata_clipped_domain)
        connectivity.Update()

        n_regions = connectivity.GetNumberOfExtractedRegions()
        mypy.my_print(verbose-1, "n_regions = "+str(n_regions))
        assert (n_regions in (1,2))
        if (n_regions == 1):
            continue

        pdata_clipped_domain = connectivity.GetOutput()
        #print(pdata_clipped_domain.GetNumberOfPoints())
        #print(pdata_clipped_domain.GetPointData().GetArray("RegionId"))
        #for k_point in xrange(pdata_clipped_domain.GetNumberOfPoints()):
            #print(pdata_clipped_domain.GetPointData().GetArray("RegionId").GetTuple(k_point))
        #myvtk.writePData(pdata_clipped_domain, "pdata_clipped_domain1.vtk")

        threshold = vtk.vtkThreshold()
        if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
            threshold.SetInputData(pdata_clipped_domain)
        else:
            threshold.SetInput(pdata_clipped_domain)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "RegionId")

        threshold.ThresholdByLower(0.5)
        threshold.Update()
        ugrid1 = threshold.GetOutput()
        #print(ugrid1.GetNumberOfPoints())
        #myvtk.writeUGrid(ugrid1, "ugrid1.vtk")
        pdata1 = myvtk.ugrid2pdata(ugrid1)
        #print(pdata1.GetNumberOfPoints())
        #myvtk.writePData(pdata1, "pdata1.vtk")

        threshold.ThresholdByUpper(0.5)
        threshold.Update()
        ugrid2 = threshold.GetOutput()
        #print(ugrid2.GetNumberOfPoints())
        pdata2 = myvtk.ugrid2pdata(ugrid2)
        #print(pdata2.GetNumberOfPoints())

        if (myvtk.getPDataSurfaceArea(pdata1) < myvtk.getPDataSurfaceArea(pdata2)):
            return pdata1, pdata2
        else:
            return pdata2, pdata1

########################################################################

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("domain_filename" , type=str                )
    parser.add_argument("--r"             , type=float, default=None)
    parser.add_argument("--endLV_filename", type=str  , default=None)
    parser.add_argument("--epiLV_filename", type=str  , default=None)
    parser.add_argument("--verbose", "-v" , type=int  , default=1   )
    args = parser.parse_args()

    mypy.my_print(args.verbose, "*** splitDomainBetweenEndoAndEpi ***")

    if (args.endLV_filename is None):
        args.endLV_filename = args.domain_filename.replace("LV", "EndLV")
    if (args.epiLV_filename is None):
        args.epiLV_filename = args.domain_filename.replace("LV", "EpiLV")

    pdata_domain = myvtk.readPData(
        filename=args.domain_filename,
        verbose=args.verbose-1)

    (pdata_end,
     pdata_epi) = cbl.splitDomainBetweenEndoAndEpi(
         pdata_domain=pdata_domain,
         r=args.r,
         verbose=args.verbose-1)

    myvtk.writeSTL(
        pdata=pdata_end,
        filename=args.endLV_filename,
        verbose=args.verbose-1)

    myvtk.writeSTL(
        pdata=pdata_epi,
        filename=args.epiLV_filename,
        verbose=args.verbose-1)
