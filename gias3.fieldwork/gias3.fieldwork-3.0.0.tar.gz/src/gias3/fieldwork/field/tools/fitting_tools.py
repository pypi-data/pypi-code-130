"""
FILE: fitting_tools.py
LAST MODIFIED: 24-12-2015
DESCRIPTION: functions and classes for fitting meshes.

===============================================================================
This file is part of GIAS2. (https://bitbucket.org/jangle/gias2)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
===============================================================================
"""

import itertools
import logging
import sys

import numpy as np
from scipy.optimize import leastsq, fmin
from scipy.spatial import cKDTree

from gias3.common import transform3D
from gias3.fieldwork.field import geometric_field
from gias3.fieldwork.field import geometric_field_fitter as GFF

log = logging.getLogger(__name__)


# ======================================================================#
def _sampleData(data, N):
    """
    Pick N evenly spaced points from data
    """

    if N < 1:
        raise ValueError('N must be > 1')
    elif N > len(data):
        return data
    else:
        i = np.linspace(0, len(data) - 1, N).astype(int)
        return data[i, :]


# ======================================================================#
# correspondent fitting data fitting                                   #
# ======================================================================#
def fitAffine(data, target, xtol=1e-5, maxfev=0, sample=None, verbose=0, output_errors=0):
    if len(data) != len(target):
        raise ValueError('data and target points must have same number of points')

    rms0 = np.sqrt(((data - target) ** 2.0).sum(1).mean())

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    t = transform3D.directAffine(D, T)
    dataFitted = transform3D.transformAffine(data, t)
    rmsOpt = np.sqrt(((dataFitted - target) ** 2.0).sum(1).mean())
    if verbose:
        log.debug('initial RMS: {}'.format(rms0))
        log.debug('final RMS: {}'.format(rmsOpt))

    if output_errors:
        return t, dataFitted, (rms0, rmsOpt)
    else:
        return t, dataFitted


def fitTranslation(data, target, xtol=1e-5, maxfev=0, sample=None, verbose=0, output_errors=0):
    """ fits for tx,ty for transforms points in data to points
    in target. Points in data and target are assumed to correspond by
    order
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    def obj(x):
        DT = D + x
        d = ((DT - T) ** 2.0).sum(1)
        return d

    t0 = target.mean(0) - data.mean(0)
    # t0 = np.array([ 0.0, 0.0, 0.0 ])

    rms0 = np.sqrt(obj(t0).mean())
    if verbose:
        log.debug('initial RMS: {}'.format(rms0))

    xOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]

    rmsOpt = np.sqrt(obj(xOpt).mean())
    if verbose:
        log.debug('final RMS: {}'.format(rmsOpt))

    dataFitted = data + xOpt
    if output_errors:
        return xOpt, dataFitted, (rms0, rmsOpt)
    else:
        return xOpt, dataFitted


def fitRigid(data, target, t0=None, xtol=1e-3, maxfev=0, sample=None, verbose=0, epsfcn=0, output_errors=0):
    """ fits for tx,ty,tz,rx,ry,rz to transform points in data to points
    in target. Points in data and target are assumed to correspond by
    order
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def obj(x):
        DT = transform3D.transformRigid3DAboutCoM(D, x)
        d = ((DT - T) ** 2.0).sum(1)
        return d

    t0 = np.array(t0)
    rms0 = np.sqrt(obj(t0).mean())
    if verbose:
        log.debug('initial RMS: {}'.format(rms0))

    xOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev, epsfcn=epsfcn)[0]

    rmsOpt = np.sqrt(obj(xOpt).mean())
    if verbose:
        log.debug('final RMS: {}'.format(rmsOpt))

    dataFitted = transform3D.transformRigid3DAboutCoM(data, xOpt)
    if output_errors:
        return xOpt, dataFitted, (rms0, rmsOpt)
    else:
        return xOpt, dataFitted


def fitRigidFMin(data, target, t0=None, xtol=1e-3, maxfev=0, sample=None, verbose=0, output_errors=0):
    """ fits for tx,ty,tz,rx,ry,rz to transform points in data to points
    in target. Points in data and target are assumed to correspond by
    order
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def obj(x):
        DT = transform3D.transformRigid3DAboutCoM(D, x)
        d = ((DT - T) ** 2.0).sum(1)
        rmsd = np.sqrt(d.mean())
        return rmsd

    t0 = np.array(t0)
    rms0 = np.sqrt(obj(t0).mean())
    if verbose:
        log.debug('initial RMS: {}'.format(rms0))

    xOpt = fmin(obj, t0, xtol=xtol, maxiter=maxfev)

    rmsOpt = np.sqrt(obj(xOpt).mean())
    if verbose:
        log.debug('final RMS: {}'.format(rmsOpt))

    dataFitted = transform3D.transformRigid3DAboutCoM(data, xOpt)
    if output_errors:
        return xOpt, dataFitted, (rms0, rmsOpt)
    else:
        return xOpt, dataFitted


def fitRigidScale(data, target, t0=None, xtol=1e-3, maxfev=0, sample=None, verbose=0, output_errors=0):
    """ fits for tx,ty,tz,rx,ry,rz,s to transform points in data to points
    in target. Points in data and target are assumed to correspond by
    order
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    def obj(x):
        DT = transform3D.transformRigidScale3DAboutCoM(D, x)
        d = ((DT - T) ** 2.0).sum(1)
        return d

    t0 = np.array(t0)
    rms0 = np.sqrt(obj(t0).mean())
    if verbose:
        log.debug('initial RMS: {}'.format(rms0))

    xOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]

    rmsOpt = np.sqrt(obj(xOpt).mean())
    if verbose:
        log.debug('final RMS: {}'.format(rmsOpt))

    dataFitted = transform3D.transformRigidScale3DAboutCoM(data, xOpt)
    if output_errors:
        return xOpt, dataFitted, (rms0, rmsOpt)
    else:
        return xOpt, dataFitted

    # ======================================================================#


# Non correspondent fitting data fitting                               #
# ======================================================================#
def fitDataRigidEPDP(data, target, xtol=1e-5, maxfev=0, t0=None, sample=None, output_errors=0):
    """ fit list of points data to list of points target by minimising
    least squares distance between each point in data and closest neighbour
    in target
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    TTree = cKDTree(T)
    D = np.array(D)

    def obj(t):
        DT = transform3D.transformRigid3DAboutCoM(D, t)
        d = TTree.query(DT)[0]
        # print d.mean()
        return d * d

    initialRMSE = np.sqrt(obj(t0).mean())
    tOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]
    dataFitted = transform3D.transformRigid3DAboutCoM(data, tOpt)
    finalRMSE = np.sqrt(obj(tOpt).mean())
    # print 'fitDataRigidEPDP finalRMSE:', finalRMSE

    if output_errors:
        return tOpt, dataFitted, (initialRMSE, finalRMSE)
    else:
        return tOpt, dataFitted


def fitDataTranslateEPDP(data, target, xtol=1e-5, maxfev=0, t0=None, sample=None, output_errors=0):
    """ fit list of points data to list of points target by minimising
    least squares distance between each point in data and closest neighbour
    in target
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = np.array([0.0, 0.0, 0.0])

    TTree = cKDTree(T)
    D = np.array(D)

    def obj(t):
        DT = transform3D.transformRigid3DAboutCoM(D, np.hstack((t, [0.0, 0.0, 0.0])))
        d = TTree.query(list(DT))[0]
        # ~ print d.mean()
        return d * d

    initialRMSE = np.sqrt(obj(t0).mean())
    tOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]
    dataFitted = transform3D.transformRigid3DAboutCoM(data, np.hstack((tOpt, [0.0, 0.0, 0.0])))
    finalRMSE = np.sqrt(obj(tOpt).mean())

    if output_errors:
        return tOpt, dataFitted, (initialRMSE, finalRMSE)
    else:
        return tOpt, dataFitted


def fitDataRigidDPEP(data, target, xtol=1e-5, maxfev=0, t0=None, sample=None, output_errors=0):
    """ fit list of points data to list of points target by minimising
    least squares distance between each point in target and closest neighbour
    in data
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    D = np.array(D)

    def obj(t):
        DT = transform3D.transformRigid3DAboutCoM(D, t)
        DTTree = cKDTree(DT)
        d = DTTree.query(list(T))[0]
        # ~ print d.mean()
        return d * d

    initialRMSE = np.sqrt(obj(t0).mean())
    tOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]
    dataFitted = transform3D.transformRigid3DAboutCoM(data, tOpt)
    finalRMSE = np.sqrt(obj(tOpt).mean())

    if output_errors:
        return tOpt, dataFitted, (initialRMSE, finalRMSE)
    else:
        return tOpt, dataFitted


def fitDataRigidScaleEPDP(data, target, xtol=1e-5, maxfev=0, t0=None, sample=None, output_errors=0, scale_threshold=None):
    """ fit list of points data to list of points target by minimising
    least squares distance between each point in data and closest neighbour
    in target
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])

    TTree = cKDTree(T)
    D = np.array(D)

    if scale_threshold is not None:
        # print 'scale penalty on'
        def obj(t):
            DT = transform3D.transformRigidScale3DAboutCoM(D, t)
            d = TTree.query(list(DT))[0]
            s = max(t[-1], 1.0 / t[-1])
            if s > scale_threshold:
                sw = 1000.0 * s
            else:
                sw = 1.0
            return d * d + sw
    else:
        def obj(t):
            DT = transform3D.transformRigidScale3DAboutCoM(D, t)
            d = TTree.query(list(DT))[0]
            return d * d

    initialRMSE = np.sqrt(obj(t0).mean())
    tOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]
    dataFitted = transform3D.transformRigidScale3DAboutCoM(data, tOpt)
    finalRMSE = np.sqrt(obj(tOpt).mean())

    if output_errors:
        return tOpt, dataFitted, (initialRMSE, finalRMSE)
    else:
        return tOpt, dataFitted


def fitDataRigidScaleDPEP(data, target, xtol=1e-5, maxfev=0, t0=None, sample=None, output_errors=0, scale_threshold=None):
    """ fit list of points data to list of points target by minimising
    least squares distance between each point in target and closest neighbour
    in data
    """

    if sample is not None:
        D = _sampleData(data, sample)
        T = _sampleData(target, sample)
    else:
        D = data
        T = target

    if t0 is None:
        t0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])

    D = np.array(D)

    if scale_threshold is not None:
        def obj(t):
            DT = transform3D.transformRigidScale3DAboutCoM(D, t)
            DTTree = cKDTree(DT)
            d = DTTree.query(T)[0]
            s = t[6]
            if s > scale_threshold:
                sw = 1000.0 * s
            else:
                sw = 1.0
            return d * d + sw
    else:
        def obj(t):
            DT = transform3D.transformRigidScale3DAboutCoM(D, t)
            DTTree = cKDTree(DT)
            d = DTTree.query(T)[0]
            return d * d

    initialRMSE = np.sqrt(obj(t0).mean())
    tOpt = leastsq(obj, t0, xtol=xtol, maxfev=maxfev)[0]
    dataFitted = transform3D.transformRigidScale3DAboutCoM(data, tOpt)
    finalRMSE = np.sqrt(obj(tOpt).mean())

    if output_errors:
        return tOpt, dataFitted, (initialRMSE, finalRMSE)
    else:
        return tOpt, dataFitted


# ======================================================================#
# mesh fitting helper functions                                        #
# ======================================================================#
def combineObjs(obj1, obj2, w1, w2):
    c = itertools.count(0)

    def obj(p):
        err1 = obj1(p)
        err2 = obj2(p)
        err = np.hstack((err1 * w1, err2 * w2))

        sys.stdout.write('\rit' + str(next(c)) + '\tgeom rms:' + str(np.sqrt((err1).mean())) + '\tcomb rms:' + str(
            np.sqrt((err).mean())))
        sys.stdout.flush()

        return err

    return obj


def combObjGeomSobNormalStack(g_obj, sob_obj, n_obj, sob_w, n_w, fixed_node_i=None, fixed_node_val=None):
    c = itertools.count(0)

    if fixed_node_i is None:
        def obj(p):
            gErr = g_obj(p)
            sobErr = sob_obj(p) * sob_w
            nErr = n_obj(p) * n_w
            err = np.hstack((gErr, sobErr, nErr))

            sys.stdout.write(
                '\rit' + str(next(c)) + '\tgeom rms:' + str(np.sqrt((gErr).mean())) + '\tcomb rms:' + str(
                    np.sqrt((err).mean())))
            sys.stdout.flush()

            return err
    else:
        def obj(p):

            p = p.reshape(3, -1).T
            p[fixed_node_i] = fixed_node_val
            p = p.T.ravel()

            gErr = g_obj(p)
            sobErr = sob_obj(p) * sob_w
            nErr = n_obj(p) * n_w
            err = np.hstack((gErr, sobErr, nErr))

            sys.stdout.write(
                '\rit' + str(next(c)) + '\tgeom rms:' + str(np.sqrt(gErr.mean())) + '\tcomb rms:' + str(
                    np.sqrt((err).mean())))
            sys.stdout.flush()

            return err

    return obj


def combObjGeomSobNormalSum(g_obj, sob_obj, n_obj, sob_w, n_w, fixed_node_i=None, fixed_node_val=None):
    c = itertools.count(0)

    if fixed_node_i is None:
        def obj(p):
            gErr = g_obj(p)
            sobErr = sob_obj(p) * sob_w
            nErr = n_obj(p) * n_w
            err = np.hstack((gErr + sobErr, nErr))

            sys.stdout.write(
                '\rit: ' + str(next(c)) + '\tgeom rms:' + str(np.sqrt((gErr).mean())) + '\tcomb rms:' + str(
                    np.sqrt((err).mean())))
            sys.stdout.flush()

            return err

    else:
        def obj(p):

            p = p.reshape(3, -1).T
            p[fixed_node_i] = fixed_node_val
            p = p.T.ravel()

            gErr = g_obj(p)
            sobErr = sob_obj(p) * sob_w
            nErr = n_obj(p) * n_w
            err = np.hstack((gErr + sobErr, nErr))

            sys.stdout.write(
                '\rit: ' + str(next(c)) + '\tgeom rms:' + str(np.sqrt((gErr).mean())) + '\tcomb rms:' + str(
                    np.sqrt((err).mean())))
            sys.stdout.flush()

            return err

    return obj


# ======================================================================#
# mesh fitting function                                                #
# ======================================================================#

"""
specific cases, don't use these directly
"""


def fitBoundaryCurveDPEP(curve_gf, data, GD, sob_w, tangent_w, it_max=10, n_closest_points=1, tree_args=None, fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty1D(curve_gf, GD, sob_w)
    tangentSmoother = GFF.tangentSmoother(curve_gf.ensemble_field_function)
    nObj = tangentSmoother.makeObj()

    gObj = GFF.makeObjDPEP(curve_gf, data, GD, dataWeights=None, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, tangent_w)

    # initialise geometric field fitter
    p0 = curve_gf.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((curve_gf.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='DPEP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    curve_gf.set_field_parameters(Opt.copy())

    return curve_gf, Opt, finalErr


def fitSurfaceDPEP(GF, data, GD, sob_w, normal_d, normal_w, it_max=10, data_weights=None, n_closest_points=1, tree_args=None,
                   fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)

    gObj = GFF.makeObjDPEP(GF, data, GD, data_weights=data_weights, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((GF.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='DPEP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


def fitSurfaceDPEPFixNodes(GF, data, GD, sob_w, normal_d, normal_w, fixed_nodes, it_max=10, data_weights=None,
                           n_closest_points=1, tree_args=None, fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args
    # get indices of params free to fit
    P0 = GF.get_field_parameters()
    P0[:, fixed_nodes, :] = -99999
    nonFixedInd = np.where(P0.ravel() != -99999)

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)

    gObj = GFF.makeObjDPEP(GF, data, GD, data_weights=data_weights, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    X = GF.get_field_parameters().ravel()

    def fixedObj(x):
        X[nonFixedInd] = x
        return obj(X)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()[nonFixedInd]
    maxFEval = len(p0) * it_max
    output = leastsq(fixedObj, p0, xtol=1e-3, maxfev=maxFEval)

    X[nonFixedInd] = output[0]
    Opt = X.copy().reshape((GF.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='DPEP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


def fitBoundaryCurveEPDP(curve_gf, data, GD, sob_w, tangent_w, it_max=10, n_closest_points=1, tree_args=None, fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty1D(curve_gf, GD, sob_w)
    tangentSmoother = GFF.tangentSmoother(curve_gf.ensemble_field_function)
    nObj = tangentSmoother.makeObj()

    gObj = GFF.makeObjEPDP(curve_gf, data, GD, data_weights=None, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, tangent_w)

    # initialise geometric field fitter
    p0 = curve_gf.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((curve_gf.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='EPDP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    curve_gf.set_field_parameters(Opt.copy())

    return curve_gf, Opt, finalErr


def fitSurfaceEPDP(GF, data, GD, sob_w, normal_d, normal_w, it_max=10, data_weights=None, n_closest_points=1, tree_args=None,
                   fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)

    gObj = GFF.makeObjEPDP(GF, data, GD, data_weights=data_weights, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((GF.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='DPEP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


def fitSurfaceEPDPFixNodes(GF, data, GD, sob_w, normal_d, normal_w, fixed_nodes, it_max=10, data_weights=None,
                           n_closest_points=1, tree_args=None, fit_verbose=False):
    tree_args = {} if tree_args is None else tree_args

    # get indices of params free to fit
    P0 = GF.get_field_parameters()
    P0[:, fixed_nodes, :] = -99999
    nonFixedInd = np.where(P0.ravel() != -99999)

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)

    gObj = GFF.makeObjEPDP(GF, data, GD, data_weights=data_weights, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    X = GF.get_field_parameters().ravel()

    def fixedObj(x):
        X[nonFixedInd] = x
        return obj(X)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()[nonFixedInd]
    maxFEval = len(p0) * it_max
    output = leastsq(fixedObj, p0, xtol=1e-3, maxfev=maxFEval)

    X[nonFixedInd] = output[0]
    Opt = X.copy().reshape((GF.dimensions, -1, 1))

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


def fitBoundaryCurve2Way(curve_gf, data, GD, sob_w, tangent_w, it_max=10, n_closest_points=1, tree_args=None, fit_verbose=False):
    """
    both EPDP and DPEP
    """
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty1D(curve_gf, GD, sob_w)
    tangentSmoother = GFF.tangentSmoother(curve_gf.ensemble_field_function)
    nObj = tangentSmoother.makeObj()
    gObj = GFF.makeObj2Way(curve_gf, data, GD, data_weights=None, n_closest_points=n_closest_points, tree_args=tree_args)

    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, tangent_w)

    # initialise geometric field fitter
    p0 = curve_gf.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((curve_gf.dimensions, -1, 1))

    # old way using the GFF class
    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='EPDP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    curve_gf.set_field_parameters(Opt.copy())

    return curve_gf, Opt, finalErr


def fitSurface2Way(GF, data, GD, sob_w, normal_d, normal_w, dataWeights=None, it_max=10, n_closest_points=1, tree_args=None,
                   fit_verbose=False):
    """
    both EPDP and DPEP
    """
    tree_args = {} if tree_args is None else tree_args

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)
    gObj = GFF.makeObj2Way(GF, data, GD, data_weights=dataWeights, n_closest_points=n_closest_points, tree_args=tree_args)

    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=1e-3, maxfev=maxFEval)
    Opt = output[0].reshape((GF.dimensions, -1, 1))

    # old way using the GFF class
    # ~ gFitter = GFF.geometryFit(GF, data, [20], fitMode='geometry', projectionDirection='EPDP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = obj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


def fitBoundaryCurve2WayFixNodes(curve_gf, data, GD, sob_w, tangent_w, fixed_nodes, it_max=10, n_closest_points=1, tree_args=None,
                                 fit_verbose=False):
    """
    both EPDP and DPEP
    """
    tree_args = {} if tree_args is None else tree_args

    # get indices of params free to fit
    P0 = curve_gf.get_field_parameters()
    P0[:, fixed_nodes, :] = -99999
    nonFixedInd = np.where(P0.ravel() != -99999)

    sobObj = GFF.makeSobelovPenalty1D(curve_gf, GD, sob_w)
    tangentSmoother = GFF.tangentSmoother(curve_gf.ensemble_field_function)
    nObj = tangentSmoother.makeObj()
    gObj = GFF.makeObj2Way(curve_gf, data, GD, data_weights=None, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, tangent_w)

    X = curve_gf.get_field_parameters().ravel()

    def fixedObj(x):
        X[nonFixedInd] = x
        return obj(X)

    # initialise geometric field fitter
    p0 = curve_gf.get_field_parameters().ravel()[nonFixedInd]
    maxFEval = len(p0) * it_max
    output = leastsq(fixedObj, p0, xtol=1e-3, maxfev=maxFEval)
    optParams = output[0].reshape((curve_gf.dimensions, -1, 1))

    X[nonFixedInd] = output[0]
    Opt = X.copy().reshape((curve_gf.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='EPDP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = fixedObj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    curve_gf.set_field_parameters(Opt.copy())

    return curve_gf, Opt, finalErr


def fitSurface2WayFixNodes(GF, data, GD, sob_w, normal_d, normal_w, fixed_nodes, data_weights=None, it_max=10,
                           n_closest_points=1, tree_args=None, fit_verbose=False):
    """
    both EPDP and DPEP
    """
    tree_args = {} if tree_args is None else tree_args

    # get indices of params free to fit
    P0 = GF.get_field_parameters()
    P0[:, fixed_nodes, :] = -99999
    nonFixedInd = np.where(P0.ravel() != -99999)

    sobObj = GFF.makeSobelovPenalty2D(GF, GD, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)
    gObj = GFF.makeObj2Way(GF, data, GD, data_weights=data_weights, n_closest_points=n_closest_points, tree_args=tree_args)
    obj = combObjGeomSobNormalStack(gObj, sobObj, nObj, 1.0, normal_w)

    X = GF.get_field_parameters().ravel()

    def fixedObj(x):
        X[nonFixedInd] = x
        return obj(X)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()[nonFixedInd]
    maxFEval = len(p0) * it_max
    output = leastsq(fixedObj, p0, xtol=1e-3, maxfev=maxFEval)
    optParams = output[0].reshape((GF.dimensions, -1, 1))

    X[nonFixedInd] = output[0]
    Opt = X.copy().reshape((GF.dimensions, -1, 1))

    # ~ gFitter = GFF.geometryFit(curveGF, data, [20], fitMode='geometry', projectionDirection='EPDP', projectionFreq='percall', smoothing=False )
    # ~ gFitter.objMesh = fixedObj
    # ~ Opt, fitOutput, errors = gFitter.meshFit( it=it_max, errorOutput=True, verbose=fit_verbose )

    fE = gObj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    return GF, Opt, finalErr


gObjMakers = {
    'EPDP': GFF.makeObjEPDP,
    'DPEP': GFF.makeObjDPEP,
    'EPEP': GFF.makeObjEPEP,
    '2Way': GFF.makeObj2Way,
}

"""
use these instead of the ones above
"""


def fitSurface(g_obj_type, GF, data, GD, sob_d, sob_w, normal_d, normal_w,
               xtol=1e-6, it_max=10, data_weights=None, n_closest_points=1, tree_args=None,
               fit_verbose=False, sob_obj=None, n_obj=None, g_obj=None, gf_eval=None,
               full_errors=False):
    """
    both EPDP and DPEP
    """
    tree_args = {} if tree_args is None else tree_args

    log.debug(xtol)
    if sob_obj is None:
        sob_obj = GFF.makeSobelovPenalty2D(GF, sob_d, sob_w)
    if n_obj is None:
        normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
        n_obj = normalSmoother.makeObj(normal_d)
    if g_obj is None:
        g_obj = gObjMakers[g_obj_type](GF, data, GD, data_weights=data_weights,
                                       n_closest_points=n_closest_points, tree_args=tree_args,
                                       evaluator=gf_eval
                                       )

    obj = combObjGeomSobNormalStack(g_obj, sob_obj, n_obj, 1.0, normal_w)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()
    maxFEval = len(p0) * it_max
    output = leastsq(obj, p0, xtol=xtol, maxfev=maxFEval)
    Opt = output[0].reshape((GF.dimensions, -1, 1))

    fE = g_obj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    if full_errors:
        return GF, Opt, finalErr, fE
    else:
        return GF, Opt, finalErr


def fitSurfaceFixNodes(g_obj_type, GF, data, GD, sob_d, sob_w, normal_d, normal_w,
                       fixed_nodes, xtol=1e-6, it_max=10, data_weights=None, n_closest_points=1,
                       tree_args=None, fit_verbose=False, sob_obj=None, n_obj=None, g_obj=None,
                       gf_eval=None, full_errors=False):
    # get indices of params free to fit
    tree_args = {} if tree_args is None else tree_args

    P0 = GF.get_field_parameters()
    P0[:, fixed_nodes, :] = -99999
    nonFixedInd = np.where(P0.ravel() != -99999)

    if sob_obj is None:
        sob_obj = GFF.makeSobelovPenalty2D(GF, sob_d, sob_w)
    if n_obj is None:
        normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
        n_obj = normalSmoother.makeObj(normal_d)
    if g_obj is None:
        g_obj = gObjMakers[g_obj_type](GF, data, GD, data_weights=data_weights,
                                       n_closest_points=n_closest_points, tree_args=tree_args, evaluator=gf_eval
                                       )

    obj = combObjGeomSobNormalStack(g_obj, sob_obj, n_obj, 1.0, normal_w)

    X = GF.get_field_parameters().ravel()

    def fixedObj(x):
        X[nonFixedInd] = x
        return obj(X)

    # initialise geometric field fitter
    p0 = GF.get_field_parameters().ravel()[nonFixedInd]
    maxFEval = len(p0) * it_max
    output = leastsq(fixedObj, p0, xtol=xtol, maxfev=maxFEval)

    X[nonFixedInd] = output[0]
    Opt = X.copy().reshape((GF.dimensions, -1, 1))

    fE = g_obj(Opt.ravel())
    finalErr = np.sqrt(fE[np.where(np.isfinite(fE))].mean())
    GF.set_field_parameters(Opt.copy())

    if full_errors:
        return GF, Opt, finalErr, fE
    else:
        return GF, Opt, finalErr


def closestSearch(X, Y, k=1, tree_args={}):
    """
    for each point in X, find the closest point in Y
    """
    closestDist, closestInd = cKDTree(Y).query(list(X), k=k, **tree_args)

    closest = np.zeros(X.shape, dtype=float)
    # if any dist are inf (closest point not found), replace its closest point
    # by the point in X itself, replace its closestInd with None
    isFinite = np.isfinite(closestDist)
    for i in np.where(np.bitwise_not(isFinite))[0]:
        closest[i] = X[i]
        # closestInd[i] = None

    closest[np.where(isFinite)] = Y[closestInd[np.where(isFinite)]]
    return closest, closestInd, closestDist


def calcRelError(x1, x2):
    return abs(x1 - x2) / x1


# main fitting function
def fitSurfacePerItSearch(g_obj_type, GF, data, GD, sob_d, sob_w, normal_d, normal_w,
                          fixed_nodes=None, sample_elems=None, xtol=1e-6, it_max=10,
                          it_max_per_it=3, data_weights=None, n_closest_points=1, tree_args=None,
                          fit_verbose=False, full_errors=False, fit_output_callback=None):
    """
    search for closest points once per leastsq iteration
    gObjType='EPDP' or 'DPEP' supported only
    returns fitOutput = [GF, pOpt, fitRMS, [fitErrors]]
    """
    fitOutput = None
    tree_args = {} if tree_args is None else tree_args

    if g_obj_type not in ('EPDP', 'DPEP'):
        raise ValueError('gObjType ' + g_obj_type + ' not supported in fitSurfacePerItSearch')

    printInputs = 1

    if printInputs:
        log.debug('gObjType:', g_obj_type)
        log.debug('data shape:', data.shape)
        log.debug('GD:', GD)
        log.debug('sobD:', sob_d)
        log.debug('sob_w:', sob_w)
        log.debug('normal_d:', normal_d)
        log.debug('normal_w:', normal_w)
        log.debug('fixedNodes:', fixed_nodes)
        log.debug('sampleElems:', sample_elems)
        log.debug('xtol:', xtol)
        log.debug('maxIt:', it_max)
        log.debug('it_maxPerIt:', it_max_per_it)

    sobObj = GFF.makeSobelovPenalty2D(GF, sob_d, sob_w)
    normalSmoother = GFF.normalSmoother2(GF.ensemble_field_function.flatten()[0])
    nObj = normalSmoother.makeObj(normal_d)
    useGFEval = False

    if hasattr(GD, '__getitem__') or (g_obj_type == 'EPDP'):
        GFEval = geometric_field.makeGeometricFieldEvaluatorSparse(GF, GD)
        useGFEval = True

    # if gObjType=='EPDP':
    # GFEval = geometric_field.makeGeometricFieldEvaluatorSparse( GF, GD )

    it = 0
    fitRMSOld = 9999999999
    while it < it_max:
        if g_obj_type == 'EPDP':
            ep = GFEval(GF.get_field_parameters().ravel()).T
            fitData, fitDataI, fitDataDist = closestSearch(ep, data, 1, tree_args)
            if data_weights is not None:
                gObj = gObjMakers['EPEP'](GF, fitData, GD, dataWeights=data_weights[fitDataI], evaluator=GFEval)
            else:
                gObj = gObjMakers['EPEP'](GF, fitData, GD, dataWeights=None, evaluator=GFEval)
        elif g_obj_type == 'DPEP':
            if sample_elems is None:
                fitData = data

                # KD-tree search
                if useGFEval:
                    ep = GFEval(GF.get_field_parameters().ravel()).T
                else:
                    ep = GF.discretiseAllElementsRegularGeoD(GD, geo_coordinates=True)[1]

                fitEP, fitEPI, fitEPDist = closestSearch(data, ep, 1, tree_args)
                gObj = gObjMakers['EPEP'](GF, fitData, GD, dataWeights=data_weights, epIndex=fitEPI)

                # minisation search
                # ~ closestMPs, fitEP, fitEPDist = GF.find_closest_material_points( data, initGD=[10,10], verbose=True )
                # ~ gObj = gObjMakers['EPEP']( GF, fitData, GD, dataWeights=dataWeights, matPoints=closestMPs )
            else:
                ep = np.vstack([GF.discretiseElementRegularGeoD(e, GD, geo_coords=True)[1] for e in sample_elems])

            # ~ pdb.set_trace()
            # ~ geometric_field.mlab.points3d(ep[fitEPI,0],ep[fitEPI,1],ep[fitEPI,2])
            # ~ geometric_field.mlab.points3d(fitData[:,0],fitData[:,1],fitData[:,2])

        # fit output = [GF, pOpt, fitRMS, [fitErrors]]
        if fixed_nodes is not None:
            fitOutput = fitSurfaceFixNodes('EPEP', GF, fitData, GD, sob_d, sob_w, normal_d, normal_w, fixed_nodes,
                                           xtol=xtol, it_max=it_max_per_it, data_weights=None, n_closest_points=1, tree_args={},
                                           fit_verbose=fit_verbose, sob_obj=sobObj, n_obj=nObj, g_obj=gObj,
                                           full_errors=full_errors)
        else:
            fitOutput = fitSurface('EPEP', GF, fitData, GD, sob_d, sob_w, normal_d, normal_w,
                                   xtol=xtol, it_max=it_max_per_it, data_weights=None, n_closest_points=1, tree_args={},
                                   fit_verbose=fit_verbose, sob_obj=sobObj, n_obj=nObj, g_obj=gObj, full_errors=full_errors)

        fitRMS = fitOutput[2]
        sys.stdout.write('\nit: %(i)i\tRMSE: %(RMSE)8.6f\n' % {'i': it, 'RMSE': fitRMS})
        # ~ sys.stdout.flush()

        if fit_output_callback is not None:
            fit_output_callback(fitOutput)

        if calcRelError(fitRMSOld, fitRMS) < xtol:
            break
        else:
            fitRMSOld = fitRMS
            it += 1

    return fitOutput


def hostMeshFit(host_gf, slave_gf, slave_obj, slave_xi=None, max_it=0,
                sob_d=None, sob_w=1e-5, xtol=1e-6, fixed_slave_nodes=None, verbose=True):
    """ host mesh fit slaveGF using hostGF as the 
    host mesh and slaveObj as the objective function to minimise
    """

    sob_d = [4, 4, 4] if sob_d is None else sob_d
    # # calc slave node xi in host
    # if slaveXi==None:
    #     if verbose:
    #         log.debug('calculating slave xi...')
    #     slaveXi = np.array([hostGF.findXi(0, node)[0] for node in slaveGF.field_parameters[:,:,0].T])
    #     #~ pdb.set_trace()
    #     #~ savetxt( 'host_mesh_fitting/slaveXi.txt', slaveXi )

    # # calc host basis values at slaveXis
    # hostElem = hostGF.ensemble_field_function.mesh.elements[0]
    # evaluator = hostGF.ensemble_field_function.evaluators[hostElem.type]
    # basisFunction = hostGF.ensemble_field_function.basis[hostElem.type]
    # slaveBasis = basisFunction.eval( slaveXi.T )
    # #~ pdb.set_trace()
    # A = np.zeros( [slaveGF.get_number_of_points(), hostGF.get_number_of_points()], dtype=float )
    # slaveEvalEntries = [ [0,b] for b in slaveBasis.T ]
    # evalSlaveParams = geometric_field.buildEvaluatorSparse(A, slaveEvalEntries,
    #                     hostGF.ensemble_field_function.mapper._element_to_ensemble_map,
    #                     hostGF.dimensions
    #                     )

    # calc slave node xi in host
    if slave_xi is None:
        slave_xi = host_gf.find_closest_material_points(
            slave_gf.field_parameters[:, :, 0].T,
            init_gd=[40, 40, 40],
            verbose=True
        )[0]

    # calc host basis values at slaveXis
    evalSlaveParams = geometric_field.makeGeometricFieldEvaluatorSparse(
        host_gf, [1, 1], mat_points=slave_xi
    )

    # initialise smoothing for host mesh
    sobolevW = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0])
    hostParam0 = host_gf.get_field_parameters()
    smoother = GFF.makeSobelovPenalty3D(host_gf, sob_d, sobolevW * sob_w)

    # handle fixed slave nodes
    if fixed_slave_nodes is not None:
        slaveP0 = slave_gf.get_field_parameters()
        slaveP0[:, fixed_slave_nodes, :] = np.inf
        fixedSlaveInds = np.where(~np.isfinite(slaveP0.ravel()))[0]
        fixedSlaveParams = slave_gf.get_field_parameters().ravel()[fixedSlaveInds]
        fixedSlave = True
    else:
        fixedSlave = False
        fixedSlaveInd = None

    c = itertools.count(0)

    # hostmesh obj function
    def hostMeshObj(host_params):

        host_params = host_params.reshape(3, -1, 1)
        host_gf.set_field_parameters(host_params)
        slaveParams = evalSlaveParams(host_params).ravel()
        # pdb.set_trace()
        if fixedSlave:
            # replace parameters at fixed indices with their original values
            slaveParams[fixedSlaveInd] = fixedSlaveParams

        slaveErr = slave_obj(slaveParams)
        smoothErr = smoother(host_params)
        err = np.hstack((slaveErr, smoothErr))

        sys.stdout.write(
            'it: {it:d}, slaveRMS: {srms:8.6f}, combinedRMS: {crms:8.6f}\r'.format(
                it=next(c),
                srms=np.sqrt(slaveErr.mean()),
                crms=np.sqrt(err.mean())
            ))
        sys.stdout.flush()

        return err

    maxf = max_it * host_gf.get_number_of_points() * 3

    if verbose:
        log.info('HMF initial rms: %s', np.sqrt(hostMeshObj(hostParam0).mean()))

    # do fit
    hostParamsOpt = leastsq(hostMeshObj, hostParam0.ravel(), xtol=xtol,
                            maxfev=maxf
                            )[0].reshape((3, -1, 1))
    host_gf.set_field_parameters(hostParamsOpt)
    slaveParamsOpt = evalSlaveParams(hostParamsOpt)[:, :, np.newaxis]
    if fixedSlave:
        # replace parameters at fixed indices with their original values
        slaveParamsOptFlat = slaveParamsOpt.ravel()
        slaveParamsOptFlat[fixedSlaveInd] = fixedSlaveParams
        slaveParamsOpt = slaveParamsOptFlat.reshape((3, -1, 1))

    slave_gf.set_field_parameters(slaveParamsOpt)

    finalHostRMS = np.sqrt(hostMeshObj(hostParamsOpt.ravel().copy()).mean())
    finalSlaveRMS = np.sqrt(slave_obj(slaveParamsOpt.ravel().copy()).mean())
    if verbose:
        log.info('final host rms: %s, final slave rms: %s', finalHostRMS, finalSlaveRMS)

    return hostParamsOpt, slaveParamsOpt, slave_xi, finalSlaveRMS


def hostMeshFitMulti(host_gf, slave_gf, slave_obj, slave_xi=None, max_it=0,
                     sob_d=None, sob_w=1e-5, xtol=1e-6, fixed_slave_nodes=None, verbose=True):
    """ host mesh fit self.G using host (geometric_field) as the 
    host mesh and slaveObj as the objective function to minimise
    """
    log.debug('host mesh fit...')
    sob_d = [4, 4, 4] if sob_d is None else sob_d
    # calc slave node xi in host
    if slave_xi is None:
        if verbose:
            log.debug('calculating slave xi...')
        slave_xi = host_gf.find_closest_material_points(slave_gf.field_parameters[:, :, 0].T,
                                                        init_gd=[40, 40, 40],
                                                        verbose=False)[0]

    # calc host basis values at slaveXis
    evalSlaveParams = geometric_field.makeGeometricFieldEvaluatorSparse(host_gf, [1, 1], mat_points=slave_xi)

    # initialise smoothing for host mesh
    sobolevW = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 3.0])
    hostParam0 = host_gf.get_field_parameters()
    smoother = GFF.makeSobelovPenalty3D(host_gf, sob_d, sobolevW * sob_w)

    # handle fixed slave nodes
    if fixed_slave_nodes is not None:
        slaveP0 = slave_gf.get_field_parameters()
        slaveP0[:, fixed_slave_nodes, :] = np.inf
        fixedSlaveInds = np.where(~np.isfinite(slaveP0.ravel()))[0]
        fixedSlaveParams = slave_gf.get_field_parameters().ravel()[fixedSlaveInds]
        fixedSlave = True
    else:
        fixedSlave = False
        fixedSlaveInd = None

    c = itertools.count(0)

    # hostmesh obj function
    def hostMeshObj(host_params):

        host_params = host_params.reshape(3, -1, 1)
        host_gf.set_field_parameters(host_params)
        # ~ slaveParams = np.array( [ evaluator( slaveBasis, p ) for p in hostParams] ).ravel()
        slaveParams = evalSlaveParams(host_params).ravel()
        if fixedSlave:
            # replace parameters at fixed indices with their original values
            slaveParams[fixedSlaveInd] = fixedSlaveParams

        slaveErr = slave_obj(slaveParams)

        smoothErr = smoother(host_params)
        Err = np.hstack((slaveErr, smoothErr))
        sys.stdout.write('it: {it:d}, slaveRMS: {srms:8.6f}, combinedRMS: {crms:8.6f}\r'.format(
            it=next(c),
            srms=np.sqrt(slaveErr.mean()),
            crms=np.sqrt(Err.mean())
        ))
        sys.stdout.flush()
        return Err

    maxf = max_it * (host_gf.get_number_of_points() * 3)

    if verbose:
        log.debug('HMF initial rms: {}'.format(np.sqrt(hostMeshObj(hostParam0).mean())))

    # do fit
    hostParamsOpt = leastsq(hostMeshObj, hostParam0.ravel(), xtol=xtol, maxfev=maxf)[0].reshape((3, -1, 1))
    host_gf.set_field_parameters(hostParamsOpt)
    # slaveParamsOpt = hostGF.evaluate_geometric_field_at_element_points( 0, slaveXi )[:,:,np.newaxis]
    slaveParamsOpt = evalSlaveParams(hostParamsOpt)[:, :, np.newaxis]
    if fixedSlave:
        # replace parameters at fixed indices with their original values
        slaveParamsOptFlat = slaveParamsOpt.ravel()
        slaveParamsOptFlat[fixedSlaveInd] = fixedSlaveParams
        slaveParamsOpt = slaveParamsOptFlat.reshape((3, -1, 1))

    slave_gf.set_field_parameters(slaveParamsOpt)

    finalHostRMS = np.sqrt(hostMeshObj(hostParamsOpt.ravel().copy()).mean())
    finalSlaveRMS = np.sqrt(slave_obj(slaveParamsOpt.ravel().copy()).mean())
    if verbose:
        log.debug('final host rms: {}, final slave rms: {}'.format(finalHostRMS, finalSlaveRMS))

    return hostParamsOpt, slaveParamsOpt, slave_xi, finalSlaveRMS


def hostMeshFitMultiPerItSearch(data, host_gf, slave_gf, slave_g_obj_type, slave_gd,
                                slave_sob_d, slave_sob_w, slave_nd, slave_nw, host_sob_d=None, host_sob_w=1e-5,
                                data_weights=None, slave_xi=None, xtol=1e-6, max_it=5, max_it_per_it=2, tree_args=None,
                                fit_output_callback=None, fixed_slave_nodes=None, verbose=True):
    log.debug('host mesh fit...')
    host_sob_d = [4, 4, 4] if host_sob_d is None else host_sob_d
    fitOutput = None
    # calc slave node xi in host
    if slave_xi is None:
        if verbose:
            log.debug('calculating slave xi...')
        slave_xi = host_gf.find_closest_material_points(
            slave_gf.field_parameters[:, :, 0].T,
            init_gd=[40, 40, 40],
            verbose=False)[0]

    # init slave params evaluator given host params
    evalSlaveParams = geometric_field.makeGeometricFieldEvaluatorSparse(
        host_gf,
        [1, 1],
        mat_points=slave_xi)

    # init slave functions
    slaveSobObj = GFF.makeSobelovPenalty2D(slave_gf, slave_sob_d, slave_sob_w)
    slaveNormalSmoother = GFF.normalSmoother2(slave_gf.ensemble_field_function.flatten()[0])
    slaveNObj = slaveNormalSmoother.makeObj(slave_nd)
    if slave_g_obj_type == 'EPDP':
        slaveGFEval = geometric_field.makeGeometricFieldEvaluatorSparse(
            slave_gf,
            slave_gd
        )

    if tree_args is None:
        tree_args = {}

    it = 1
    fitRMSOld = 9999999999.0
    while it <= max_it:
        if slave_g_obj_type == 'EPDP':
            ep = slaveGFEval(slave_gf.get_field_parameters().ravel()).T
            fitData, fitDataI, fitDataDist = closestSearch(ep, data, 1, tree_args)
            if data_weights is not None:
                slaveGObj = gObjMakers['EPEP'](slave_gf, fitData, slave_gd,
                                               dataWeights=data_weights[fitDataI],
                                               evaluator=slaveGFEval
                                               )
            else:
                slaveGObj = gObjMakers['EPEP'](slave_gf, fitData, slave_gd,
                                               dataWeights=None,
                                               evaluator=slaveGFEval
                                               )
        elif slave_g_obj_type == 'DPEP':
            fitData = data
            # KD-tree search
            ep = slave_gf.discretiseAllElementsRegularGeoD(slave_gd, geo_coordinates=True)[1]
            fitEP, fitEPI, fitEPDist = closestSearch(data, ep, 1, tree_args)
            slaveGObj = gObjMakers['EPEP'](slave_gf, fitData, slave_gd,
                                           dataWeights=data_weights,
                                           epIndex=fitEPI
                                           )
        else:
            raise ValueError('Unrecognised slaveGObj Type ' + slave_g_obj_type)

        # create slave obj
        def slaveObj(x):
            errSurface = slaveGObj(x)
            errSob = slaveSobObj(x)
            errNorm = slaveNObj(x) * slave_nw
            return np.hstack([errSurface, errSob, errNorm])

        # run iterations of HMF
        fitOutput = hostMeshFitMulti(
            host_gf, slave_gf, slaveObj,
            slave_xi=slave_xi, max_it=max_it_per_it,
            sob_d=host_sob_d, sob_w=host_sob_w,
            fixed_slave_nodes=fixed_slave_nodes,
            verbose=False
        )

        fitRMS = fitOutput[3]
        sys.stdout.write('\nit: {i:d}\tRMSE: {RMSE:8.6f}\n'.format(i=it, RMSE=fitRMS))
        # sys.stdout.flush()

        if fit_output_callback is not None:
            fit_output_callback(fitOutput)

        if calcRelError(fitRMSOld, fitRMS) < xtol:
            break
        else:
            fitRMSOld = fitRMS
            it += 1

    return fitOutput


def hostMeshFitPoints(host_mesh, slave_points, slave_func, slave_xi=None, max_it=0,
                      xtol=1e-6, sob_d=[4, 4, 4], sob_w=1e-5, fixed_points=None, verbose=True
                      ):
    """
    Host mesh fit slave_points. Minimises slave_func by deforming host_mesh
    in which slave_points are embedded.

    For details on hostmesh fitting, see
    Fernandez, J. W., Mithraratne, P., Thrupp, S. F., Tawhai, M. H., & Hunter, P. J.
    (2004). Anatomically based geometric modelling of the musculo-skeletal system
    and other organs. Biomech Model Mechanobiol, 2(3), 139-155.

    Inputs:
    host_mesh: a fieldwork.field.geometric_field mesh that fully encloses
        slave points
    slave_points: a nx3 array of point coordinates to fit.
    slave_func: a function that takes slave point coordinates as input and
        returns an error vector
    slave_xi (optional): material coordinates of slave_points in host_mesh if
        known.
    max_it (optional): maximum number of fitting iterations.
    xtol (optional): Relative error desired in the approximate solution.
    sob_d (optional): number of gauss points for host mesh sobelov smoothing
        calculation
    sob_w (optional): weighting for host mesh sobelov smoothing
    fixed_points (optional): a list of slave point numbers for slave points
        to be fixed during the fit
    verbose (optional): print extra info

    Returns:
    host_x_opt: fitted host mesh
    slave_points_opt: fitted slave point coordinats
    slave_xi: material coordinates of slave point in host mesh
    slave_rmse_opt: RMS of fitted slave_func error vector
    """
    log.debug('host mesh fit...')
    # calc slave node xi in host
    if slave_xi is None:
        if verbose:
            log.debug('calculating slave xi...')
        slave_xi = host_mesh.find_closest_material_points(
            slave_points,
            init_gd=[100, 100, 100],
            verbose=verbose,
        )[0]

    # make slave coordinates evaluator function
    eval_slave = geometric_field.makeGeometricFieldEvaluatorSparse(
        host_mesh, [1, 1], mat_points=slave_xi
    )

    # initialise smoothing for host mesh
    sobolev_weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                2.0, 2.0,
                                3.0
                                ])
    host_x_0 = host_mesh.field_parameters.copy()
    host_smoother = GFF.makeSobelovPenalty3D(
        host_mesh, sob_d, sobolev_weights * sob_w
    )

    # handle fixed slave nodes
    if fixed_points is not None:
        fixed_point_coords = slave_points[fixed_points, :]
        has_fixed_points = True
    else:
        has_fixed_points = False

    c = itertools.count(0)

    # hostmesh obj function
    def host_func(host_x):
        host_x = host_x.reshape(3, -1, 1)
        host_mesh.set_field_parameters(host_x)
        slave_points_it = eval_slave(host_x).T
        if has_fixed_points:
            slave_points_it[fixed_points, :] = fixed_point_coords
        slave_err = slave_func(slave_points_it)

        smooth_err = host_smoother(host_x)
        err = np.hstack([slave_err, smooth_err])
        if verbose:
            sys.stdout.write(
                'it: {it:d}, slaveRMS: {srms:8.6f}, combinedRMS: {crms:8.6f}\r'.format(
                    it=next(c),
                    srms=np.sqrt(slave_err.mean()),
                    crms=np.sqrt(err.mean())
                ))
            sys.stdout.flush()
        return err

    maxf = max_it * (host_mesh.get_number_of_points() * 3)

    if verbose:
        log.debug(('HMF initial rms: {:6.4f}'.format(np.sqrt(host_func(host_x_0).mean()))))

    # do fit
    host_x_opt = leastsq(
        host_func, host_x_0.ravel(), xtol=xtol, maxfev=maxf
    )[0].reshape((3, -1, 1))
    host_mesh.set_field_parameters(host_x_opt)
    slave_points_opt = eval_slave(host_x_opt).T
    if has_fixed_points:
        slave_points_opt[fixed_points, :] = fixed_point_coords

    host_rmse_opt = np.sqrt(host_func(host_x_opt.ravel().copy()).mean())
    slave_rmse_opt = np.sqrt(slave_func(slave_points_opt).mean())
    if verbose:
        log.debug(('final host rms: {:6.4f}, final slave rms: {:6.4f}'.format(
            host_rmse_opt,
            slave_rmse_opt
        )
        ))

    return host_x_opt, slave_points_opt, slave_xi, slave_rmse_opt


def getClosestDataPoints(data, L, d, n, DUB):
    """ given a curve L, finds the n closest points in data to each ep 
    sampled off L at discretisation d
    """

    ep = L.evaluate_geometric_field(d).T
    dataTree = cKDTree(data)

    closestI = dataTree.query(list(ep), k=n, distance_upper_bound=DUB)[1]
    closestI = closestI[np.where(closestI < data.shape[0])]
    return data[np.unique(closestI)]


def fitterFit(GF, epD, data, fit=None, max_it=100, drms=0.0, output=True, do_fit=True):
    originalEFF = GF.ensemble_field_function
    if not GF.ensemble_field_function.is_flat():
        GF.ensemble_field_function = GF.ensemble_field_function.flatten()[0]

    if fit is None:
        fit = fitter.Fit()
        GF.setFitterElementD(epD)
        GF.addElementPointsToFitter(fit)
        fit.generate(GF)

    fit.set_data(data, mode='closest')  # if you have more data than element points.

    if do_fit:
        rmsErr = fit.solve(GF.getFitterParameters(), maxiter=max_it, drms=drms, output=output)
        GF.set_field_parameters(fit.x.T[:, :, np.newaxis])
    else:
        rmsErr = None

    GF.ensemble_field_function = originalEFF

    return fit, rmsErr


def projectToDataGF(dataGF, GPC, init_rot, modes):
    """
    calculate the rigid transforms and projected weights of a dataGF
    on the shape model GPC
    """

    targ = dataGF.get_field_parameters().reshape((3, -1)).T
    data = GPC.getMean().reshape((3, -1)).T
    initTrans = targ.mean(0) - data.mean(0)
    rigidX0 = np.hstack([initTrans, init_rot])

    rigidXOpt, rigidFittedData = fitRigid(data, targ, t0=rigidX0, xtol=1e-3, maxfev=0, verbose=0)

    rigidXOptBack, rigidFittedDataTarg = fitRigid(targ, data, t0=-rigidX0, xtol=1e-3, maxfev=0, verbose=0)
    projWeights = GPC.project(rigidFittedDataTarg.T.ravel() - GPC.getMean(), modes)
    projSD = GPC.calcSDFromWeights(modes, projWeights)
    return np.hstack([rigidXOpt, projSD])


# ======================================================================#
# Datacloud fitting error calculation functions
def calcDPEPErrors(data, GF):
    """
    find closest material point to each data point through minimisation
    """
    GF.flatten_ensemble_field_function()
    mp, p, d = GF.find_closest_material_points(data, init_gd=[10, 10], verbose=True)
    GF.ensemble_field_function = GF.ensemble_field_function_old
    rms = calcRMS(d)
    return d, rms


def calcEPDPEPErrors(data, GF, ep_d):
    """
    find the closest datapoints to material points, then find
    the closest point on mesh of those datapoints
    """

    # find closest datapoint to each EP
    ep = GF.evaluate_geometric_field(ep_d).T
    EPDPDist, EPDPi = cKDTree(data).query(list(ep), k=1)
    closestData = data[EPDPi]

    # find closest material points to closestData
    GF.flatten_ensemble_field_function()
    mp, p, d = GF.find_closest_material_points(closestData, init_gd=[10, 10], verbose=True)
    GF.ensemble_field_function = GF.ensemble_field_function_old
    rms = calcRMS(d)
    return d, rms


def calcDPDPErrors(data_gt, data):
    """
    for each point in data cloud dataGT, find distance to closest point 
    in data cloud data
    """

    d, dataInd = cKDTree(data).query(list(data_gt), k=1)
    rms = calcRMS(d)
    return d, rms


def calcRMS(x):
    return np.sqrt((x ** 2.0).mean())
