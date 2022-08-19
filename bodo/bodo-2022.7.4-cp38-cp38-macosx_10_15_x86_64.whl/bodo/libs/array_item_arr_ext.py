"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ouamx__aemqx = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ouamx__aemqx)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        ouamx__aemqx = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ouamx__aemqx)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    suj__twzxk = builder.module
    dry__ousd = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    qekfr__jfnka = cgutils.get_or_insert_function(suj__twzxk, dry__ousd,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not qekfr__jfnka.is_declaration:
        return qekfr__jfnka
    qekfr__jfnka.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(qekfr__jfnka.append_basic_block())
    ios__rrf = qekfr__jfnka.args[0]
    jcspn__yjmbq = context.get_value_type(payload_type).as_pointer()
    aprhm__tcx = builder.bitcast(ios__rrf, jcspn__yjmbq)
    liie__vqr = context.make_helper(builder, payload_type, ref=aprhm__tcx)
    context.nrt.decref(builder, array_item_type.dtype, liie__vqr.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), liie__vqr
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), liie__vqr
        .null_bitmap)
    builder.ret_void()
    return qekfr__jfnka


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    gysa__aob = context.get_value_type(payload_type)
    zkbu__gkr = context.get_abi_sizeof(gysa__aob)
    jfox__llxh = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    jzdrc__hilfa = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zkbu__gkr), jfox__llxh)
    qllc__kaw = context.nrt.meminfo_data(builder, jzdrc__hilfa)
    bfft__zit = builder.bitcast(qllc__kaw, gysa__aob.as_pointer())
    liie__vqr = cgutils.create_struct_proxy(payload_type)(context, builder)
    liie__vqr.n_arrays = n_arrays
    brdm__dxx = n_elems.type.count
    kjbdc__frbg = builder.extract_value(n_elems, 0)
    gct__clla = cgutils.alloca_once_value(builder, kjbdc__frbg)
    hge__jpo = builder.icmp_signed('==', kjbdc__frbg, lir.Constant(
        kjbdc__frbg.type, -1))
    with builder.if_then(hge__jpo):
        builder.store(n_arrays, gct__clla)
    n_elems = cgutils.pack_array(builder, [builder.load(gct__clla)] + [
        builder.extract_value(n_elems, njc__oejcd) for njc__oejcd in range(
        1, brdm__dxx)])
    liie__vqr.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    daib__ifr = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    rti__iaejc = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [daib__ifr])
    offsets_ptr = rti__iaejc.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    liie__vqr.offsets = rti__iaejc._getvalue()
    kzz__rwa = builder.udiv(builder.add(n_arrays, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    yppku__nbay = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [kzz__rwa])
    null_bitmap_ptr = yppku__nbay.data
    liie__vqr.null_bitmap = yppku__nbay._getvalue()
    builder.store(liie__vqr._getvalue(), bfft__zit)
    return jzdrc__hilfa, liie__vqr.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    gbgj__vxr, qfrtv__khd = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    rpyoc__rbq = context.insert_const_string(builder.module, 'pandas')
    gtdrw__qul = c.pyapi.import_module_noblock(rpyoc__rbq)
    sqb__fpk = c.pyapi.object_getattr_string(gtdrw__qul, 'NA')
    mri__hcbqn = c.context.get_constant(offset_type, 0)
    builder.store(mri__hcbqn, offsets_ptr)
    vgxwf__app = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as atxpm__ebt:
        dfsn__cvm = atxpm__ebt.index
        item_ind = builder.load(vgxwf__app)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [dfsn__cvm]))
        arr_obj = seq_getitem(builder, context, val, dfsn__cvm)
        set_bitmap_bit(builder, null_bitmap_ptr, dfsn__cvm, 0)
        kpu__bwit = is_na_value(builder, context, arr_obj, sqb__fpk)
        xnxne__vdq = builder.icmp_unsigned('!=', kpu__bwit, lir.Constant(
            kpu__bwit.type, 1))
        with builder.if_then(xnxne__vdq):
            set_bitmap_bit(builder, null_bitmap_ptr, dfsn__cvm, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), vgxwf__app)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(vgxwf__app), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(gtdrw__qul)
    c.pyapi.decref(sqb__fpk)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    cyrj__ramgb = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if cyrj__ramgb:
        dry__ousd = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        kevhh__obb = cgutils.get_or_insert_function(c.builder.module,
            dry__ousd, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(kevhh__obb,
            [val])])
    else:
        ywqa__xma = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            ywqa__xma, njc__oejcd) for njc__oejcd in range(1, ywqa__xma.
            type.count)])
    jzdrc__hilfa, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if cyrj__ramgb:
        pyhps__jxe = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        yljse__cxl = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        dry__ousd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        qekfr__jfnka = cgutils.get_or_insert_function(c.builder.module,
            dry__ousd, name='array_item_array_from_sequence')
        c.builder.call(qekfr__jfnka, [val, c.builder.bitcast(yljse__cxl,
            lir.IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir
            .Constant(lir.IntType(32), pyhps__jxe)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    acovw__das = c.context.make_helper(c.builder, typ)
    acovw__das.meminfo = jzdrc__hilfa
    rqcc__gzo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(acovw__das._getvalue(), is_error=rqcc__gzo)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    acovw__das = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    qllc__kaw = context.nrt.meminfo_data(builder, acovw__das.meminfo)
    bfft__zit = builder.bitcast(qllc__kaw, context.get_value_type(
        payload_type).as_pointer())
    liie__vqr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(bfft__zit))
    return liie__vqr


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    rpyoc__rbq = context.insert_const_string(builder.module, 'numpy')
    rthww__ctiap = c.pyapi.import_module_noblock(rpyoc__rbq)
    bnpy__qeuy = c.pyapi.object_getattr_string(rthww__ctiap, 'object_')
    pad__tlu = c.pyapi.long_from_longlong(n_arrays)
    ogo__ndbzq = c.pyapi.call_method(rthww__ctiap, 'ndarray', (pad__tlu,
        bnpy__qeuy))
    nlyg__poqe = c.pyapi.object_getattr_string(rthww__ctiap, 'nan')
    vgxwf__app = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as atxpm__ebt:
        dfsn__cvm = atxpm__ebt.index
        pyarray_setitem(builder, context, ogo__ndbzq, dfsn__cvm, nlyg__poqe)
        dpqr__bwqex = get_bitmap_bit(builder, null_bitmap_ptr, dfsn__cvm)
        goir__niyi = builder.icmp_unsigned('!=', dpqr__bwqex, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(goir__niyi):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(dfsn__cvm, lir.Constant(dfsn__cvm
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                dfsn__cvm]))), lir.IntType(64))
            item_ind = builder.load(vgxwf__app)
            gbgj__vxr, zefvg__wiyg = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), vgxwf__app)
            arr_obj = c.pyapi.from_native_value(typ.dtype, zefvg__wiyg, c.
                env_manager)
            pyarray_setitem(builder, context, ogo__ndbzq, dfsn__cvm, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(rthww__ctiap)
    c.pyapi.decref(bnpy__qeuy)
    c.pyapi.decref(pad__tlu)
    c.pyapi.decref(nlyg__poqe)
    return ogo__ndbzq


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    liie__vqr = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = liie__vqr.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), liie__vqr.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), liie__vqr.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        pyhps__jxe = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        yljse__cxl = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        dry__ousd = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        gnjn__hwiu = cgutils.get_or_insert_function(c.builder.module,
            dry__ousd, name='np_array_from_array_item_array')
        arr = c.builder.call(gnjn__hwiu, [liie__vqr.n_arrays, c.builder.
            bitcast(yljse__cxl, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), pyhps__jxe)])
    else:
        arr = _box_array_item_array_generic(typ, c, liie__vqr.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    ugyq__usij, gpde__imifs, gkow__wjia = args
    tfqf__bgjpe = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    coj__xga = sig.args[1]
    if not isinstance(coj__xga, types.UniTuple):
        gpde__imifs = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), -1) for gkow__wjia in range(tfqf__bgjpe)])
    elif coj__xga.count < tfqf__bgjpe:
        gpde__imifs = cgutils.pack_array(builder, [builder.extract_value(
            gpde__imifs, njc__oejcd) for njc__oejcd in range(coj__xga.count
            )] + [lir.Constant(lir.IntType(64), -1) for gkow__wjia in range
            (tfqf__bgjpe - coj__xga.count)])
    jzdrc__hilfa, gkow__wjia, gkow__wjia, gkow__wjia = (
        construct_array_item_array(context, builder, array_item_type,
        ugyq__usij, gpde__imifs))
    acovw__das = context.make_helper(builder, array_item_type)
    acovw__das.meminfo = jzdrc__hilfa
    return acovw__das._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, lzet__niewz, rti__iaejc, yppku__nbay = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    gysa__aob = context.get_value_type(payload_type)
    zkbu__gkr = context.get_abi_sizeof(gysa__aob)
    jfox__llxh = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    jzdrc__hilfa = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zkbu__gkr), jfox__llxh)
    qllc__kaw = context.nrt.meminfo_data(builder, jzdrc__hilfa)
    bfft__zit = builder.bitcast(qllc__kaw, gysa__aob.as_pointer())
    liie__vqr = cgutils.create_struct_proxy(payload_type)(context, builder)
    liie__vqr.n_arrays = n_arrays
    liie__vqr.data = lzet__niewz
    liie__vqr.offsets = rti__iaejc
    liie__vqr.null_bitmap = yppku__nbay
    builder.store(liie__vqr._getvalue(), bfft__zit)
    context.nrt.incref(builder, signature.args[1], lzet__niewz)
    context.nrt.incref(builder, signature.args[2], rti__iaejc)
    context.nrt.incref(builder, signature.args[3], yppku__nbay)
    acovw__das = context.make_helper(builder, array_item_type)
    acovw__das.meminfo = jzdrc__hilfa
    return acovw__das._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    uay__zyekl = ArrayItemArrayType(data_type)
    sig = uay__zyekl(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        liie__vqr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            liie__vqr.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        liie__vqr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        yljse__cxl = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, liie__vqr.offsets).data
        rti__iaejc = builder.bitcast(yljse__cxl, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(rti__iaejc, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        liie__vqr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            liie__vqr.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        liie__vqr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            liie__vqr.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        liie__vqr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return liie__vqr.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, pcwv__dent = args
        acovw__das = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        qllc__kaw = context.nrt.meminfo_data(builder, acovw__das.meminfo)
        bfft__zit = builder.bitcast(qllc__kaw, context.get_value_type(
            payload_type).as_pointer())
        liie__vqr = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(bfft__zit))
        context.nrt.decref(builder, data_typ, liie__vqr.data)
        liie__vqr.data = pcwv__dent
        context.nrt.incref(builder, data_typ, pcwv__dent)
        builder.store(liie__vqr._getvalue(), bfft__zit)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    lzet__niewz = get_data(arr)
    kgfq__yrwoy = len(lzet__niewz)
    if kgfq__yrwoy < new_size:
        bpon__jtlvx = max(2 * kgfq__yrwoy, new_size)
        pcwv__dent = bodo.libs.array_kernels.resize_and_copy(lzet__niewz,
            old_size, bpon__jtlvx)
        replace_data_arr(arr, pcwv__dent)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    lzet__niewz = get_data(arr)
    rti__iaejc = get_offsets(arr)
    vzu__oquj = len(lzet__niewz)
    gpkxs__jjt = rti__iaejc[-1]
    if vzu__oquj != gpkxs__jjt:
        pcwv__dent = bodo.libs.array_kernels.resize_and_copy(lzet__niewz,
            gpkxs__jjt, gpkxs__jjt)
        replace_data_arr(arr, pcwv__dent)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            rti__iaejc = get_offsets(arr)
            lzet__niewz = get_data(arr)
            elczy__kug = rti__iaejc[ind]
            nggh__laof = rti__iaejc[ind + 1]
            return lzet__niewz[elczy__kug:nggh__laof]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        oldat__vxk = arr.dtype

        def impl_bool(arr, ind):
            bga__bfkx = len(arr)
            if bga__bfkx != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            yppku__nbay = get_null_bitmap(arr)
            n_arrays = 0
            ywnjc__jeuil = init_nested_counts(oldat__vxk)
            for njc__oejcd in range(bga__bfkx):
                if ind[njc__oejcd]:
                    n_arrays += 1
                    ntis__jtt = arr[njc__oejcd]
                    ywnjc__jeuil = add_nested_counts(ywnjc__jeuil, ntis__jtt)
            ogo__ndbzq = pre_alloc_array_item_array(n_arrays, ywnjc__jeuil,
                oldat__vxk)
            jojnl__gmao = get_null_bitmap(ogo__ndbzq)
            cqryi__pddt = 0
            for qez__vpem in range(bga__bfkx):
                if ind[qez__vpem]:
                    ogo__ndbzq[cqryi__pddt] = arr[qez__vpem]
                    rgf__dkkad = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        yppku__nbay, qez__vpem)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jojnl__gmao,
                        cqryi__pddt, rgf__dkkad)
                    cqryi__pddt += 1
            return ogo__ndbzq
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        oldat__vxk = arr.dtype

        def impl_int(arr, ind):
            yppku__nbay = get_null_bitmap(arr)
            bga__bfkx = len(ind)
            n_arrays = bga__bfkx
            ywnjc__jeuil = init_nested_counts(oldat__vxk)
            for qya__klvzo in range(bga__bfkx):
                njc__oejcd = ind[qya__klvzo]
                ntis__jtt = arr[njc__oejcd]
                ywnjc__jeuil = add_nested_counts(ywnjc__jeuil, ntis__jtt)
            ogo__ndbzq = pre_alloc_array_item_array(n_arrays, ywnjc__jeuil,
                oldat__vxk)
            jojnl__gmao = get_null_bitmap(ogo__ndbzq)
            for ypzrw__cldj in range(bga__bfkx):
                qez__vpem = ind[ypzrw__cldj]
                ogo__ndbzq[ypzrw__cldj] = arr[qez__vpem]
                rgf__dkkad = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    yppku__nbay, qez__vpem)
                bodo.libs.int_arr_ext.set_bit_to_arr(jojnl__gmao,
                    ypzrw__cldj, rgf__dkkad)
            return ogo__ndbzq
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            bga__bfkx = len(arr)
            esyld__mmf = numba.cpython.unicode._normalize_slice(ind, bga__bfkx)
            clcv__kfsfu = np.arange(esyld__mmf.start, esyld__mmf.stop,
                esyld__mmf.step)
            return arr[clcv__kfsfu]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            rti__iaejc = get_offsets(A)
            yppku__nbay = get_null_bitmap(A)
            if idx == 0:
                rti__iaejc[0] = 0
            n_items = len(val)
            znyny__qlh = rti__iaejc[idx] + n_items
            ensure_data_capacity(A, rti__iaejc[idx], znyny__qlh)
            lzet__niewz = get_data(A)
            rti__iaejc[idx + 1] = rti__iaejc[idx] + n_items
            lzet__niewz[rti__iaejc[idx]:rti__iaejc[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(yppku__nbay, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            esyld__mmf = numba.cpython.unicode._normalize_slice(idx, len(A))
            for njc__oejcd in range(esyld__mmf.start, esyld__mmf.stop,
                esyld__mmf.step):
                A[njc__oejcd] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            rti__iaejc = get_offsets(A)
            yppku__nbay = get_null_bitmap(A)
            mnw__sji = get_offsets(val)
            xyi__uag = get_data(val)
            hpj__ggwnp = get_null_bitmap(val)
            bga__bfkx = len(A)
            esyld__mmf = numba.cpython.unicode._normalize_slice(idx, bga__bfkx)
            alktl__knyfu, vspam__otxsw = esyld__mmf.start, esyld__mmf.stop
            assert esyld__mmf.step == 1
            if alktl__knyfu == 0:
                rti__iaejc[alktl__knyfu] = 0
            zlpwt__krhsc = rti__iaejc[alktl__knyfu]
            znyny__qlh = zlpwt__krhsc + len(xyi__uag)
            ensure_data_capacity(A, zlpwt__krhsc, znyny__qlh)
            lzet__niewz = get_data(A)
            lzet__niewz[zlpwt__krhsc:zlpwt__krhsc + len(xyi__uag)] = xyi__uag
            rti__iaejc[alktl__knyfu:vspam__otxsw + 1] = mnw__sji + zlpwt__krhsc
            niu__zzw = 0
            for njc__oejcd in range(alktl__knyfu, vspam__otxsw):
                rgf__dkkad = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    hpj__ggwnp, niu__zzw)
                bodo.libs.int_arr_ext.set_bit_to_arr(yppku__nbay,
                    njc__oejcd, rgf__dkkad)
                niu__zzw += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
