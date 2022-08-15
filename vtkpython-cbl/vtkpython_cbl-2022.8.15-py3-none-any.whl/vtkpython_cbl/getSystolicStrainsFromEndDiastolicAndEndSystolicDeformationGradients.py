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

def getSystolicStrainsFromEndDiastolicAndEndSystolicDeformationGradients(
        farray_F_dia,
        farray_F_sys,
        verbose=1):

    mypy.my_print(verbose, "*** getSystolicStrainsFromEndDiastolicAndEndSystolicDeformationGradients ***")

    n_tuples = farray_F_dia.GetNumberOfTuples()
    assert (farray_F_sys.GetNumberOfTuples() == n_tuples)

    farray_E_dia = myvtk.createFloatArray('E_dia', 6, n_tuples)
    farray_E_sys = myvtk.createFloatArray('E_sys', 6, n_tuples)
    farray_F_num = myvtk.createFloatArray('F_num', 6, n_tuples)
    farray_E_num = myvtk.createFloatArray('E_num', 6, n_tuples)

    I = numpy.eye(3)
    E_vec = numpy.empty(6)
    for k_tuple in range(n_tuples):
        F_dia = numpy.reshape(farray_F_dia.GetTuple(k_tuple), (3,3), order='C')
        F_sys = numpy.reshape(farray_F_sys.GetTuple(k_tuple), (3,3), order='C')
        #print('F_dia =', F_dia)
        #print('F_sys =', F_sys)

        C = numpy.dot(numpy.transpose(F_dia), F_dia)
        E = (C - I)/2
        mypy.mat_sym33_to_vec_col6(E, E_vec)
        farray_E_dia.SetTuple(k_tuple, E_vec)

        C = numpy.dot(numpy.transpose(F_sys), F_sys)
        E = (C - I)/2
        mypy.mat_sym33_to_vec_col6(E, E_vec)
        farray_E_sys.SetTuple(k_tuple, E_vec)

        F = numpy.dot(F_sys, numpy.linalg.inv(F_dia))
        farray_F_num.SetTuple(k_tuple, numpy.reshape(F, 9, order='C'))
        #print('F =', F)

        C = numpy.dot(numpy.transpose(F), F)
        E = (C - I)/2
        mypy.mat_sym33_to_vec_col6(E, E_vec)
        farray_E_num.SetTuple(k_tuple, E_vec)

    return (farray_E_dia,
            farray_E_sys,
            farray_F_num,
            farray_E_num)
