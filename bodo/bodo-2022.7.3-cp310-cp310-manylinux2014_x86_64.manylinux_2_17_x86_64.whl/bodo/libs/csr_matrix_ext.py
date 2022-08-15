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
        ulzj__iqawk = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ulzj__iqawk)


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
        alev__vevo, cfuay__qrw, ghi__zmt, ram__iosh = args
        qcz__tnoss = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        qcz__tnoss.data = alev__vevo
        qcz__tnoss.indices = cfuay__qrw
        qcz__tnoss.indptr = ghi__zmt
        qcz__tnoss.shape = ram__iosh
        context.nrt.incref(builder, signature.args[0], alev__vevo)
        context.nrt.incref(builder, signature.args[1], cfuay__qrw)
        context.nrt.incref(builder, signature.args[2], ghi__zmt)
        return qcz__tnoss._getvalue()
    bljja__vzdba = CSRMatrixType(data_t.dtype, indices_t.dtype)
    cfpqo__gkfss = bljja__vzdba(data_t, indices_t, indptr_t, types.UniTuple
        (types.int64, 2))
    return cfpqo__gkfss, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    qcz__tnoss = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bek__nmbn = c.pyapi.object_getattr_string(val, 'data')
    ztdxa__mef = c.pyapi.object_getattr_string(val, 'indices')
    tkh__uxo = c.pyapi.object_getattr_string(val, 'indptr')
    hii__krnd = c.pyapi.object_getattr_string(val, 'shape')
    qcz__tnoss.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'
        ), bek__nmbn).value
    qcz__tnoss.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), ztdxa__mef).value
    qcz__tnoss.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), tkh__uxo).value
    qcz__tnoss.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 
        2), hii__krnd).value
    c.pyapi.decref(bek__nmbn)
    c.pyapi.decref(ztdxa__mef)
    c.pyapi.decref(tkh__uxo)
    c.pyapi.decref(hii__krnd)
    hza__uwlzz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qcz__tnoss._getvalue(), is_error=hza__uwlzz)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    wgijl__zxs = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    hzy__wpl = c.pyapi.import_module_noblock(wgijl__zxs)
    qcz__tnoss = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        qcz__tnoss.data)
    bek__nmbn = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        qcz__tnoss.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        qcz__tnoss.indices)
    ztdxa__mef = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), qcz__tnoss.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        qcz__tnoss.indptr)
    tkh__uxo = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'),
        qcz__tnoss.indptr, c.env_manager)
    hii__krnd = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        qcz__tnoss.shape, c.env_manager)
    hdlxv__qrqp = c.pyapi.tuple_pack([bek__nmbn, ztdxa__mef, tkh__uxo])
    ltzeb__sjib = c.pyapi.call_method(hzy__wpl, 'csr_matrix', (hdlxv__qrqp,
        hii__krnd))
    c.pyapi.decref(hdlxv__qrqp)
    c.pyapi.decref(bek__nmbn)
    c.pyapi.decref(ztdxa__mef)
    c.pyapi.decref(tkh__uxo)
    c.pyapi.decref(hii__krnd)
    c.pyapi.decref(hzy__wpl)
    c.context.nrt.decref(c.builder, typ, val)
    return ltzeb__sjib


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
    jbhtf__vwq = A.dtype
    giyp__astao = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            dvm__uzenl, dmben__xprb = A.shape
            udizu__izuca = numba.cpython.unicode._normalize_slice(idx[0],
                dvm__uzenl)
            zpor__ytcgk = numba.cpython.unicode._normalize_slice(idx[1],
                dmben__xprb)
            if udizu__izuca.step != 1 or zpor__ytcgk.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            rlj__qajp = udizu__izuca.start
            erkqe__bxn = udizu__izuca.stop
            ndwp__ekqnw = zpor__ytcgk.start
            yqth__nizci = zpor__ytcgk.stop
            jprqp__cahqx = A.indptr
            oovi__zwb = A.indices
            ssl__hnxjf = A.data
            bzxxa__xkf = erkqe__bxn - rlj__qajp
            bif__tjt = yqth__nizci - ndwp__ekqnw
            nvcoh__sjz = 0
            cunyy__aypum = 0
            for ctve__ihgw in range(bzxxa__xkf):
                vjl__myuk = jprqp__cahqx[rlj__qajp + ctve__ihgw]
                aeku__ivp = jprqp__cahqx[rlj__qajp + ctve__ihgw + 1]
                for vzld__yndd in range(vjl__myuk, aeku__ivp):
                    if oovi__zwb[vzld__yndd] >= ndwp__ekqnw and oovi__zwb[
                        vzld__yndd] < yqth__nizci:
                        nvcoh__sjz += 1
            xggg__gaxh = np.empty(bzxxa__xkf + 1, giyp__astao)
            abs__ded = np.empty(nvcoh__sjz, giyp__astao)
            vohuh__own = np.empty(nvcoh__sjz, jbhtf__vwq)
            xggg__gaxh[0] = 0
            for ctve__ihgw in range(bzxxa__xkf):
                vjl__myuk = jprqp__cahqx[rlj__qajp + ctve__ihgw]
                aeku__ivp = jprqp__cahqx[rlj__qajp + ctve__ihgw + 1]
                for vzld__yndd in range(vjl__myuk, aeku__ivp):
                    if oovi__zwb[vzld__yndd] >= ndwp__ekqnw and oovi__zwb[
                        vzld__yndd] < yqth__nizci:
                        abs__ded[cunyy__aypum] = oovi__zwb[vzld__yndd
                            ] - ndwp__ekqnw
                        vohuh__own[cunyy__aypum] = ssl__hnxjf[vzld__yndd]
                        cunyy__aypum += 1
                xggg__gaxh[ctve__ihgw + 1] = cunyy__aypum
            return init_csr_matrix(vohuh__own, abs__ded, xggg__gaxh, (
                bzxxa__xkf, bif__tjt))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == giyp__astao:

        def impl(A, idx):
            dvm__uzenl, dmben__xprb = A.shape
            jprqp__cahqx = A.indptr
            oovi__zwb = A.indices
            ssl__hnxjf = A.data
            bzxxa__xkf = len(idx)
            nvcoh__sjz = 0
            cunyy__aypum = 0
            for ctve__ihgw in range(bzxxa__xkf):
                qnjma__xsz = idx[ctve__ihgw]
                vjl__myuk = jprqp__cahqx[qnjma__xsz]
                aeku__ivp = jprqp__cahqx[qnjma__xsz + 1]
                nvcoh__sjz += aeku__ivp - vjl__myuk
            xggg__gaxh = np.empty(bzxxa__xkf + 1, giyp__astao)
            abs__ded = np.empty(nvcoh__sjz, giyp__astao)
            vohuh__own = np.empty(nvcoh__sjz, jbhtf__vwq)
            xggg__gaxh[0] = 0
            for ctve__ihgw in range(bzxxa__xkf):
                qnjma__xsz = idx[ctve__ihgw]
                vjl__myuk = jprqp__cahqx[qnjma__xsz]
                aeku__ivp = jprqp__cahqx[qnjma__xsz + 1]
                abs__ded[cunyy__aypum:cunyy__aypum + aeku__ivp - vjl__myuk
                    ] = oovi__zwb[vjl__myuk:aeku__ivp]
                vohuh__own[cunyy__aypum:cunyy__aypum + aeku__ivp - vjl__myuk
                    ] = ssl__hnxjf[vjl__myuk:aeku__ivp]
                cunyy__aypum += aeku__ivp - vjl__myuk
                xggg__gaxh[ctve__ihgw + 1] = cunyy__aypum
            yjr__bbgmx = init_csr_matrix(vohuh__own, abs__ded, xggg__gaxh,
                (bzxxa__xkf, dmben__xprb))
            return yjr__bbgmx
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
