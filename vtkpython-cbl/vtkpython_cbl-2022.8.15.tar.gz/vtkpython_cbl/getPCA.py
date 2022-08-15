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

def discretizeData(
        farray_rr,
        farray_cc,
        farray_ll,
        farray_h,
        n_r,
        n_c,
        n_l,
        verbose=1):

    mypy.my_print(verbose, "*** discretizeData ***")

    n_tuples = farray_ll.GetNumberOfTuples()

    h = numpy.empty((n_r, n_c, n_l))

    for k_l in range(n_l):
        #print("k_l = "+str(k_l))
        sel_l = [k_tuple for k_tuple in range(n_tuples) if (math.floor(n_l*farray_ll.GetTuple1(k_tuple)) == k_l)]
        #print(len(sel_l))

        for k_c in range(n_c):
            #print("k_c = "+str(k_c))

            sel_c = [k_tuple for k_tuple in sel_l if (math.floor(n_c*farray_cc.GetTuple1(k_tuple)) == k_c)]
            #print(len(sel_c))

            for k_r in range(n_r):
                #print("k_r = "+str(k_r))

                sel_r = [k_tuple for k_tuple in sel_c if (math.floor(n_r*farray_rr.GetTuple1(k_tuple)) == k_r)]
                #print(len(sel_r))

                (m, s) = cbl.getMeanStddevAngles([farray_h.GetTuple1(k_tuple) for k_tuple in sel_r], verbose=0)
                h[k_r, k_c, k_l] = m

    mypy.my_print(verbose-1, "h = "+str(h))

    return h

def getSVD(
        h,
        verbose=1):

    mypy.my_print(verbose, "*** getSVD ***")

    (n_r, n_c, n_l) = h.shape

    M_r = numpy.empty((n_r, n_r))

    for i in range(n_r):
        for j in range(n_r):
            M_r[i,j] = numpy.sum([h[i,k_c,k_l]*h[j,k_c,k_l] for k_c in range(n_c) for k_l in range(n_l)])
    #print(M_r)

    U_r, D_r, V_r = numpy.linalg.svd(M_r)

    M_c = numpy.empty((n_c, n_c))

    for i in range(n_c):
        for j in range(n_c):
            M_c[i,j] = numpy.sum([h[k_r,i,k_l]*h[k_r,i,k_l] for k_r in range(n_r) for k_l in range(n_l)])
    #print(M_c)

    U_c, D_c, V_c = numpy.linalg.svd(M_c)

    M_l = numpy.empty((n_l, n_l))

    for i in range(n_l):
        for j in range(n_l):
            M_l[i,j] = numpy.sum([h[k_r,k_c,i]*h[k_r,k_c,j] for k_r in range(n_r) for k_c in range(n_c)])
    #print(M_l)

    U_l, D_l, V_l = numpy.linalg.svd(M_l)

    return U_r, D_r, V_r, U_c, D_c, V_c, U_l, D_l, V_l

def getPOD(
        h,
        verbose=1):

    mypy.my_print(verbose, "*** getPOD ***")

    (n_r, n_c, n_l) = h.shape

    M_r = numpy.empty((n_r, n_r))

    for i in range(n_r):
        for j in range(n_r):
            M_r[i,j] = numpy.sum([h[i,k_c,k_l]*h[j,k_c,k_l] for k_c in range(n_c) for k_l in range(n_l)])
    #print(M_r)

    w_r,v_r = numpy.linalg.eig(M_r)
    #print(w_r)
    #print(v_r)
    w_r = w_r.real
    v_r = v_r.real
    #print(w_r)
    #print(v_r)
    idx = w_r.argsort()[::-1]
    w_r = w_r[idx]
    v_r = v_r[:,idx]
    #print(w_r)
    #print(v_r[:,0])

    M_c = numpy.empty((n_c, n_c))

    for i in range(n_c):
        for j in range(n_c):
            M_c[i,j] = numpy.sum([h[k_r,i,k_l]*h[k_r,i,k_l] for k_r in range(n_r) for k_l in range(n_l)])
    #print(M_c)

    w_c,v_c = numpy.linalg.eig(M_c)
    w_c = w_c.real
    v_c = v_c.real
    idx = w_c.argsort()[::-1]
    w_c = w_c[idx]
    v_c = v_c[:,idx]
    #print(w_c)
    #print(v_c[:,0])

    M_l = numpy.empty((n_l, n_l))

    for i in range(n_l):
        for j in range(n_l):
            M_l[i,j] = numpy.sum([h[k_r,k_c,i]*h[k_r,k_c,j] for k_r in range(n_r) for k_c in range(n_c)])
    #print(M_l)

    w_l,v_l = numpy.linalg.eig(M_l)
    w_l = w_l.real
    v_l = v_l.real
    idx = w_l.argsort()[::-1]
    w_l = w_l[idx]
    v_l = v_l[:,idx]
    #print(w_l)
    #print(v_l[:,0])

    return w_r,v_r,w_c,v_c,w_l,v_l
