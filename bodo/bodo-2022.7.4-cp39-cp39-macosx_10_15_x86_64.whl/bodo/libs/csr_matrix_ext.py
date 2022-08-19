"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rvp__rfec = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, rvp__rfec)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        ywgb__zzz, gbdki__xehpm, ffb__fne, wulfo__litq = args
        fosc__jdm = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        fosc__jdm.data = ywgb__zzz
        fosc__jdm.indices = gbdki__xehpm
        fosc__jdm.indptr = ffb__fne
        fosc__jdm.shape = wulfo__litq
        context.nrt.incref(builder, signature.args[0], ywgb__zzz)
        context.nrt.incref(builder, signature.args[1], gbdki__xehpm)
        context.nrt.incref(builder, signature.args[2], ffb__fne)
        return fosc__jdm._getvalue()
    ogr__daw = CSRMatrixType(data_t.dtype, indices_t.dtype)
    nsef__tqt = ogr__daw(data_t, indices_t, indptr_t, types.UniTuple(types.
        int64, 2))
    return nsef__tqt, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    fosc__jdm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ftpif__dnj = c.pyapi.object_getattr_string(val, 'data')
    glrv__ppxwe = c.pyapi.object_getattr_string(val, 'indices')
    ptt__hlil = c.pyapi.object_getattr_string(val, 'indptr')
    cuf__mvl = c.pyapi.object_getattr_string(val, 'shape')
    fosc__jdm.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        ftpif__dnj).value
    fosc__jdm.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), glrv__ppxwe).value
    fosc__jdm.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), ptt__hlil).value
    fosc__jdm.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), cuf__mvl).value
    c.pyapi.decref(ftpif__dnj)
    c.pyapi.decref(glrv__ppxwe)
    c.pyapi.decref(ptt__hlil)
    c.pyapi.decref(cuf__mvl)
    npswl__pnteh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fosc__jdm._getvalue(), is_error=npswl__pnteh)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    nbq__tdva = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    fxl__oqfcl = c.pyapi.import_module_noblock(nbq__tdva)
    fosc__jdm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        fosc__jdm.data)
    ftpif__dnj = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        fosc__jdm.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        fosc__jdm.indices)
    glrv__ppxwe = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), fosc__jdm.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        fosc__jdm.indptr)
    ptt__hlil = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), fosc__jdm.indptr, c.env_manager)
    cuf__mvl = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        fosc__jdm.shape, c.env_manager)
    sxv__wib = c.pyapi.tuple_pack([ftpif__dnj, glrv__ppxwe, ptt__hlil])
    usugw__bhzb = c.pyapi.call_method(fxl__oqfcl, 'csr_matrix', (sxv__wib,
        cuf__mvl))
    c.pyapi.decref(sxv__wib)
    c.pyapi.decref(ftpif__dnj)
    c.pyapi.decref(glrv__ppxwe)
    c.pyapi.decref(ptt__hlil)
    c.pyapi.decref(cuf__mvl)
    c.pyapi.decref(fxl__oqfcl)
    c.context.nrt.decref(c.builder, typ, val)
    return usugw__bhzb


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    gvvy__ahd = A.dtype
    nnxuk__uhi = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            orlsa__zvg, bkt__uhfn = A.shape
            yvvy__xne = numba.cpython.unicode._normalize_slice(idx[0],
                orlsa__zvg)
            agk__mgri = numba.cpython.unicode._normalize_slice(idx[1],
                bkt__uhfn)
            if yvvy__xne.step != 1 or agk__mgri.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            bls__micr = yvvy__xne.start
            gopw__xxem = yvvy__xne.stop
            lqj__xaa = agk__mgri.start
            bmjcb__gea = agk__mgri.stop
            quh__skrg = A.indptr
            qmy__chle = A.indices
            uvzr__xjb = A.data
            nkovs__oqv = gopw__xxem - bls__micr
            yfcu__dgktb = bmjcb__gea - lqj__xaa
            geprk__rjxj = 0
            cxrxp__jxy = 0
            for qwu__olu in range(nkovs__oqv):
                klmv__upby = quh__skrg[bls__micr + qwu__olu]
                nfrih__wbp = quh__skrg[bls__micr + qwu__olu + 1]
                for fcmge__cskf in range(klmv__upby, nfrih__wbp):
                    if qmy__chle[fcmge__cskf] >= lqj__xaa and qmy__chle[
                        fcmge__cskf] < bmjcb__gea:
                        geprk__rjxj += 1
            qwfxr__yqab = np.empty(nkovs__oqv + 1, nnxuk__uhi)
            glgc__wwhfw = np.empty(geprk__rjxj, nnxuk__uhi)
            eun__vku = np.empty(geprk__rjxj, gvvy__ahd)
            qwfxr__yqab[0] = 0
            for qwu__olu in range(nkovs__oqv):
                klmv__upby = quh__skrg[bls__micr + qwu__olu]
                nfrih__wbp = quh__skrg[bls__micr + qwu__olu + 1]
                for fcmge__cskf in range(klmv__upby, nfrih__wbp):
                    if qmy__chle[fcmge__cskf] >= lqj__xaa and qmy__chle[
                        fcmge__cskf] < bmjcb__gea:
                        glgc__wwhfw[cxrxp__jxy] = qmy__chle[fcmge__cskf
                            ] - lqj__xaa
                        eun__vku[cxrxp__jxy] = uvzr__xjb[fcmge__cskf]
                        cxrxp__jxy += 1
                qwfxr__yqab[qwu__olu + 1] = cxrxp__jxy
            return init_csr_matrix(eun__vku, glgc__wwhfw, qwfxr__yqab, (
                nkovs__oqv, yfcu__dgktb))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == nnxuk__uhi:

        def impl(A, idx):
            orlsa__zvg, bkt__uhfn = A.shape
            quh__skrg = A.indptr
            qmy__chle = A.indices
            uvzr__xjb = A.data
            nkovs__oqv = len(idx)
            geprk__rjxj = 0
            cxrxp__jxy = 0
            for qwu__olu in range(nkovs__oqv):
                nhuth__dunwo = idx[qwu__olu]
                klmv__upby = quh__skrg[nhuth__dunwo]
                nfrih__wbp = quh__skrg[nhuth__dunwo + 1]
                geprk__rjxj += nfrih__wbp - klmv__upby
            qwfxr__yqab = np.empty(nkovs__oqv + 1, nnxuk__uhi)
            glgc__wwhfw = np.empty(geprk__rjxj, nnxuk__uhi)
            eun__vku = np.empty(geprk__rjxj, gvvy__ahd)
            qwfxr__yqab[0] = 0
            for qwu__olu in range(nkovs__oqv):
                nhuth__dunwo = idx[qwu__olu]
                klmv__upby = quh__skrg[nhuth__dunwo]
                nfrih__wbp = quh__skrg[nhuth__dunwo + 1]
                glgc__wwhfw[cxrxp__jxy:cxrxp__jxy + nfrih__wbp - klmv__upby
                    ] = qmy__chle[klmv__upby:nfrih__wbp]
                eun__vku[cxrxp__jxy:cxrxp__jxy + nfrih__wbp - klmv__upby
                    ] = uvzr__xjb[klmv__upby:nfrih__wbp]
                cxrxp__jxy += nfrih__wbp - klmv__upby
                qwfxr__yqab[qwu__olu + 1] = cxrxp__jxy
            lnzwm__gmti = init_csr_matrix(eun__vku, glgc__wwhfw,
                qwfxr__yqab, (nkovs__oqv, bkt__uhfn))
            return lnzwm__gmti
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
