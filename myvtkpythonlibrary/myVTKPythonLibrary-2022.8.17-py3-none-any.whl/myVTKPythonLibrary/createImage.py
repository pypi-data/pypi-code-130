#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2022                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

import numpy
import vtk

import myPythonLibrary    as mypy
import myVTKPythonLibrary as myvtk

########################################################################

def createImage(
        dimensions,
        spacing,
        origin,
        array_name="ImageScalars",
        array_n_components=1,
        verbose=0):

    image = vtk.vtkImageData()
    image.SetDimensions(dimensions)
    image.SetSpacing(spacing)
    image.SetOrigin(origin)

    n_points = image.GetNumberOfPoints()
    image_scalars = myvtk.createDoubleArray(
        name=array_name,
        n_components=array_n_components,
        n_tuples=n_points,
        verbose=0)
    image.GetPointData().SetScalars(image_scalars)

    return image

def createImageFromSizeAndRes(
        dim: int,
        size,
        res,
        up=1,
        **kwargs):

    if type(size) is float: size = [size]*dim
    if type(res ) is int  : res  = [res ]*dim
    if type(up  ) is int  : up   = [up  ]*dim

    assert (len(size) == dim)
    assert (len(res ) == dim)
    assert (len(up  ) == dim)

    delta = list(numpy.divide(size, res))

    res_upsampled   = list(numpy.multiply(res, up))
    delta_upsampled = list(numpy.divide(size, res_upsampled))

    dimensions_upsampled = res_upsampled                + [1 ]*(3-dim)
    spacing_upsampled    = delta_upsampled              + [1.]*(3-dim)
    origin_upsampled     = list(numpy.divide(delta, 2)) + [0.]*(3-dim)

    return myvtk.createImage(
        dimensions=dimensions_upsampled,
        spacing=spacing_upsampled,
        origin=origin_upsampled,
        **kwargs)
