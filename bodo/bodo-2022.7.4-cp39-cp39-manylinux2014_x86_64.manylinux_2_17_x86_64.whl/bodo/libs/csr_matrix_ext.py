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
        kvyz__seid = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, kvyz__seid)


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
        cffmt__lqk, bhd__pcuah, vvndi__hjojx, wnpi__xrs = args
        dfbmf__gawtz = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        dfbmf__gawtz.data = cffmt__lqk
        dfbmf__gawtz.indices = bhd__pcuah
        dfbmf__gawtz.indptr = vvndi__hjojx
        dfbmf__gawtz.shape = wnpi__xrs
        context.nrt.incref(builder, signature.args[0], cffmt__lqk)
        context.nrt.incref(builder, signature.args[1], bhd__pcuah)
        context.nrt.incref(builder, signature.args[2], vvndi__hjojx)
        return dfbmf__gawtz._getvalue()
    ydgke__uwob = CSRMatrixType(data_t.dtype, indices_t.dtype)
    hjbc__jghp = ydgke__uwob(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return hjbc__jghp, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    dfbmf__gawtz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    minq__cvosf = c.pyapi.object_getattr_string(val, 'data')
    yjn__amp = c.pyapi.object_getattr_string(val, 'indices')
    ozxg__taz = c.pyapi.object_getattr_string(val, 'indptr')
    pyhqx__brppk = c.pyapi.object_getattr_string(val, 'shape')
    dfbmf__gawtz.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), minq__cvosf).value
    dfbmf__gawtz.indices = c.pyapi.to_native_value(types.Array(typ.
        idx_dtype, 1, 'C'), yjn__amp).value
    dfbmf__gawtz.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), ozxg__taz).value
    dfbmf__gawtz.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), pyhqx__brppk).value
    c.pyapi.decref(minq__cvosf)
    c.pyapi.decref(yjn__amp)
    c.pyapi.decref(ozxg__taz)
    c.pyapi.decref(pyhqx__brppk)
    reixv__bdgld = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(dfbmf__gawtz._getvalue(), is_error=reixv__bdgld)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    jhrt__intp = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    mrh__rpkoc = c.pyapi.import_module_noblock(jhrt__intp)
    dfbmf__gawtz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        dfbmf__gawtz.data)
    minq__cvosf = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        dfbmf__gawtz.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        dfbmf__gawtz.indices)
    yjn__amp = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'),
        dfbmf__gawtz.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        dfbmf__gawtz.indptr)
    ozxg__taz = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), dfbmf__gawtz.indptr, c.env_manager)
    pyhqx__brppk = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        dfbmf__gawtz.shape, c.env_manager)
    ccjir__kwmx = c.pyapi.tuple_pack([minq__cvosf, yjn__amp, ozxg__taz])
    dmsq__lixkd = c.pyapi.call_method(mrh__rpkoc, 'csr_matrix', (
        ccjir__kwmx, pyhqx__brppk))
    c.pyapi.decref(ccjir__kwmx)
    c.pyapi.decref(minq__cvosf)
    c.pyapi.decref(yjn__amp)
    c.pyapi.decref(ozxg__taz)
    c.pyapi.decref(pyhqx__brppk)
    c.pyapi.decref(mrh__rpkoc)
    c.context.nrt.decref(c.builder, typ, val)
    return dmsq__lixkd


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
    pbkbp__axkvx = A.dtype
    uchn__lvct = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            lhhve__fafd, bweej__tbv = A.shape
            mgwjf__sia = numba.cpython.unicode._normalize_slice(idx[0],
                lhhve__fafd)
            ahpmv__hlvnc = numba.cpython.unicode._normalize_slice(idx[1],
                bweej__tbv)
            if mgwjf__sia.step != 1 or ahpmv__hlvnc.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            dzs__hda = mgwjf__sia.start
            yti__dpr = mgwjf__sia.stop
            gcitg__xhfku = ahpmv__hlvnc.start
            wwuin__azxw = ahpmv__hlvnc.stop
            qdn__ibl = A.indptr
            eiotg__onxe = A.indices
            drqun__vynz = A.data
            gaxn__pucg = yti__dpr - dzs__hda
            vyiw__qho = wwuin__azxw - gcitg__xhfku
            vtvh__rvp = 0
            dzxkp__avgk = 0
            for hsc__fwy in range(gaxn__pucg):
                gbr__ulbqp = qdn__ibl[dzs__hda + hsc__fwy]
                vwjz__cqtx = qdn__ibl[dzs__hda + hsc__fwy + 1]
                for czpy__yryjf in range(gbr__ulbqp, vwjz__cqtx):
                    if eiotg__onxe[czpy__yryjf
                        ] >= gcitg__xhfku and eiotg__onxe[czpy__yryjf
                        ] < wwuin__azxw:
                        vtvh__rvp += 1
            furxo__uno = np.empty(gaxn__pucg + 1, uchn__lvct)
            pbmdr__frhvq = np.empty(vtvh__rvp, uchn__lvct)
            dbd__pjd = np.empty(vtvh__rvp, pbkbp__axkvx)
            furxo__uno[0] = 0
            for hsc__fwy in range(gaxn__pucg):
                gbr__ulbqp = qdn__ibl[dzs__hda + hsc__fwy]
                vwjz__cqtx = qdn__ibl[dzs__hda + hsc__fwy + 1]
                for czpy__yryjf in range(gbr__ulbqp, vwjz__cqtx):
                    if eiotg__onxe[czpy__yryjf
                        ] >= gcitg__xhfku and eiotg__onxe[czpy__yryjf
                        ] < wwuin__azxw:
                        pbmdr__frhvq[dzxkp__avgk] = eiotg__onxe[czpy__yryjf
                            ] - gcitg__xhfku
                        dbd__pjd[dzxkp__avgk] = drqun__vynz[czpy__yryjf]
                        dzxkp__avgk += 1
                furxo__uno[hsc__fwy + 1] = dzxkp__avgk
            return init_csr_matrix(dbd__pjd, pbmdr__frhvq, furxo__uno, (
                gaxn__pucg, vyiw__qho))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == uchn__lvct:

        def impl(A, idx):
            lhhve__fafd, bweej__tbv = A.shape
            qdn__ibl = A.indptr
            eiotg__onxe = A.indices
            drqun__vynz = A.data
            gaxn__pucg = len(idx)
            vtvh__rvp = 0
            dzxkp__avgk = 0
            for hsc__fwy in range(gaxn__pucg):
                eyfyx__bonz = idx[hsc__fwy]
                gbr__ulbqp = qdn__ibl[eyfyx__bonz]
                vwjz__cqtx = qdn__ibl[eyfyx__bonz + 1]
                vtvh__rvp += vwjz__cqtx - gbr__ulbqp
            furxo__uno = np.empty(gaxn__pucg + 1, uchn__lvct)
            pbmdr__frhvq = np.empty(vtvh__rvp, uchn__lvct)
            dbd__pjd = np.empty(vtvh__rvp, pbkbp__axkvx)
            furxo__uno[0] = 0
            for hsc__fwy in range(gaxn__pucg):
                eyfyx__bonz = idx[hsc__fwy]
                gbr__ulbqp = qdn__ibl[eyfyx__bonz]
                vwjz__cqtx = qdn__ibl[eyfyx__bonz + 1]
                pbmdr__frhvq[dzxkp__avgk:dzxkp__avgk + vwjz__cqtx - gbr__ulbqp
                    ] = eiotg__onxe[gbr__ulbqp:vwjz__cqtx]
                dbd__pjd[dzxkp__avgk:dzxkp__avgk + vwjz__cqtx - gbr__ulbqp
                    ] = drqun__vynz[gbr__ulbqp:vwjz__cqtx]
                dzxkp__avgk += vwjz__cqtx - gbr__ulbqp
                furxo__uno[hsc__fwy + 1] = dzxkp__avgk
            fuw__jwbm = init_csr_matrix(dbd__pjd, pbmdr__frhvq, furxo__uno,
                (gaxn__pucg, bweej__tbv))
            return fuw__jwbm
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
