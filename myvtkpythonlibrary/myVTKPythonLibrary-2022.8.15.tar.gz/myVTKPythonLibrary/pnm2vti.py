#!python3
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

import argparse

import myPythonLibrary    as mypy
import myVTKPythonLibrary as myvtk

########################################################################

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pnm_filename", type=str, default=None)
    parser.add_argument("--pnm_filepattern", type=str, default=None)
    parser.add_argument("--extent", type=int, nargs=6, default=None)
    parser.add_argument("--vti_filename", type=str, default=None)
    args = parser.parse_args()

    ext_lst = ["pbm", "pgm", "ppm"]
    if (args.pnm_filename is not None):
        assert (any("."+ext in args.pnm_filename for ext in ext_lst))

    image = myvtk.readPNMImage(
        filename=args.pnm_filename,
        filepattern=args.pnm_filepattern,
        extent=args.extent)

    if (args.pnm_filename is not None) and (args.vti_filename is None):
        for ext in ext_lst:
            if ("."+ext in args.pnm_filename):
                args.vti_filename = args.pnm_filename.split("."+ext)[0]+".vti"
    myvtk.writeImage(
        image=image,
        filename=args.vti_filename)
