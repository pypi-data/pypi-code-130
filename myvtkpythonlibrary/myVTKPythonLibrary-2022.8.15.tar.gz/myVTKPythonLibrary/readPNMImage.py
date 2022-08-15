#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2021                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

from builtins import range

import os
import vtk

import myPythonLibrary    as mypy
import myVTKPythonLibrary as myvtk

########################################################################

def readPNMImage(
        filename=None,
        filepattern=None,
		extent=None,
        verbose=0):

    mypy.my_print(verbose, "*** readPNMImage ***")

    image_reader = vtk.vtkPNMReader()
    if (filename is not None) and (filepattern is None) and (extent is None):
        assert (os.path.isfile(filename)),\
            "Wrong filename (\""+filename+"\"). Aborting."
        image_reader.SetFileName(filename)
    elif (filepattern is not None) and (extent is not None) and (filename is None):
        image_reader.SetFilePattern(filepattern)
        image_reader.SetDataExtent(extent)
    image_reader.Update()
    image = image_reader.GetOutput()

    mypy.my_print(verbose-1, "n_points = "+str(image.GetNumberOfPoints()))

    return image
