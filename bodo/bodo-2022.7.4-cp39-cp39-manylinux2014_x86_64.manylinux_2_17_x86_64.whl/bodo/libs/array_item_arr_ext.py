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
        yip__seenp = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, yip__seenp)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        yip__seenp = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, yip__seenp)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    lbp__siof = builder.module
    nqx__jhgpd = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ansl__ragxg = cgutils.get_or_insert_function(lbp__siof, nqx__jhgpd,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not ansl__ragxg.is_declaration:
        return ansl__ragxg
    ansl__ragxg.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ansl__ragxg.append_basic_block())
    mqxs__zxc = ansl__ragxg.args[0]
    fuy__owm = context.get_value_type(payload_type).as_pointer()
    cnbfu__fbrif = builder.bitcast(mqxs__zxc, fuy__owm)
    gikey__sjff = context.make_helper(builder, payload_type, ref=cnbfu__fbrif)
    context.nrt.decref(builder, array_item_type.dtype, gikey__sjff.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        gikey__sjff.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        gikey__sjff.null_bitmap)
    builder.ret_void()
    return ansl__ragxg


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    zrjx__rnbtk = context.get_value_type(payload_type)
    nuyr__hpejh = context.get_abi_sizeof(zrjx__rnbtk)
    tjcb__ztbtm = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    gnc__wbnk = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, nuyr__hpejh), tjcb__ztbtm)
    ixvw__rogwg = context.nrt.meminfo_data(builder, gnc__wbnk)
    ybkgq__tifby = builder.bitcast(ixvw__rogwg, zrjx__rnbtk.as_pointer())
    gikey__sjff = cgutils.create_struct_proxy(payload_type)(context, builder)
    gikey__sjff.n_arrays = n_arrays
    szqy__rtfp = n_elems.type.count
    nswyh__ykp = builder.extract_value(n_elems, 0)
    ulf__yyk = cgutils.alloca_once_value(builder, nswyh__ykp)
    lwgul__iagq = builder.icmp_signed('==', nswyh__ykp, lir.Constant(
        nswyh__ykp.type, -1))
    with builder.if_then(lwgul__iagq):
        builder.store(n_arrays, ulf__yyk)
    n_elems = cgutils.pack_array(builder, [builder.load(ulf__yyk)] + [
        builder.extract_value(n_elems, gtv__kdwgn) for gtv__kdwgn in range(
        1, szqy__rtfp)])
    gikey__sjff.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    enbw__qfc = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    knz__cplz = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [enbw__qfc])
    offsets_ptr = knz__cplz.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    gikey__sjff.offsets = knz__cplz._getvalue()
    cze__sgpe = builder.udiv(builder.add(n_arrays, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    fsqy__qtb = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [cze__sgpe])
    null_bitmap_ptr = fsqy__qtb.data
    gikey__sjff.null_bitmap = fsqy__qtb._getvalue()
    builder.store(gikey__sjff._getvalue(), ybkgq__tifby)
    return gnc__wbnk, gikey__sjff.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    hdop__ttxdc, zjvdo__dysy = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    bnkzt__vhym = context.insert_const_string(builder.module, 'pandas')
    rjej__xsztx = c.pyapi.import_module_noblock(bnkzt__vhym)
    tfk__dyfkr = c.pyapi.object_getattr_string(rjej__xsztx, 'NA')
    jpdcn__evac = c.context.get_constant(offset_type, 0)
    builder.store(jpdcn__evac, offsets_ptr)
    ofoz__rud = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as cae__zwxe:
        rvbe__ven = cae__zwxe.index
        item_ind = builder.load(ofoz__rud)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [rvbe__ven]))
        arr_obj = seq_getitem(builder, context, val, rvbe__ven)
        set_bitmap_bit(builder, null_bitmap_ptr, rvbe__ven, 0)
        waun__kgr = is_na_value(builder, context, arr_obj, tfk__dyfkr)
        rell__nua = builder.icmp_unsigned('!=', waun__kgr, lir.Constant(
            waun__kgr.type, 1))
        with builder.if_then(rell__nua):
            set_bitmap_bit(builder, null_bitmap_ptr, rvbe__ven, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), ofoz__rud)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(ofoz__rud), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(rjej__xsztx)
    c.pyapi.decref(tfk__dyfkr)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    yxj__adxox = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if yxj__adxox:
        nqx__jhgpd = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        ieva__rzn = cgutils.get_or_insert_function(c.builder.module,
            nqx__jhgpd, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(ieva__rzn,
            [val])])
    else:
        bujs__egtef = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            bujs__egtef, gtv__kdwgn) for gtv__kdwgn in range(1, bujs__egtef
            .type.count)])
    gnc__wbnk, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if yxj__adxox:
        rzl__nnxyn = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        qxdn__xeqbg = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        nqx__jhgpd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        ansl__ragxg = cgutils.get_or_insert_function(c.builder.module,
            nqx__jhgpd, name='array_item_array_from_sequence')
        c.builder.call(ansl__ragxg, [val, c.builder.bitcast(qxdn__xeqbg,
            lir.IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir
            .Constant(lir.IntType(32), rzl__nnxyn)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    rcxaf__ijoo = c.context.make_helper(c.builder, typ)
    rcxaf__ijoo.meminfo = gnc__wbnk
    mfbh__ark = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rcxaf__ijoo._getvalue(), is_error=mfbh__ark)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    rcxaf__ijoo = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    ixvw__rogwg = context.nrt.meminfo_data(builder, rcxaf__ijoo.meminfo)
    ybkgq__tifby = builder.bitcast(ixvw__rogwg, context.get_value_type(
        payload_type).as_pointer())
    gikey__sjff = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(ybkgq__tifby))
    return gikey__sjff


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    bnkzt__vhym = context.insert_const_string(builder.module, 'numpy')
    bbkv__ohnct = c.pyapi.import_module_noblock(bnkzt__vhym)
    xwsd__jlqwf = c.pyapi.object_getattr_string(bbkv__ohnct, 'object_')
    nnj__ktgp = c.pyapi.long_from_longlong(n_arrays)
    bkw__rafis = c.pyapi.call_method(bbkv__ohnct, 'ndarray', (nnj__ktgp,
        xwsd__jlqwf))
    yhrdr__kyvz = c.pyapi.object_getattr_string(bbkv__ohnct, 'nan')
    ofoz__rud = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_arrays) as cae__zwxe:
        rvbe__ven = cae__zwxe.index
        pyarray_setitem(builder, context, bkw__rafis, rvbe__ven, yhrdr__kyvz)
        losy__quzl = get_bitmap_bit(builder, null_bitmap_ptr, rvbe__ven)
        cryy__qnodh = builder.icmp_unsigned('!=', losy__quzl, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(cryy__qnodh):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(rvbe__ven, lir.Constant(rvbe__ven
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                rvbe__ven]))), lir.IntType(64))
            item_ind = builder.load(ofoz__rud)
            hdop__ttxdc, fjyq__fcz = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), ofoz__rud)
            arr_obj = c.pyapi.from_native_value(typ.dtype, fjyq__fcz, c.
                env_manager)
            pyarray_setitem(builder, context, bkw__rafis, rvbe__ven, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(bbkv__ohnct)
    c.pyapi.decref(xwsd__jlqwf)
    c.pyapi.decref(nnj__ktgp)
    c.pyapi.decref(yhrdr__kyvz)
    return bkw__rafis


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    gikey__sjff = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = gikey__sjff.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), gikey__sjff.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), gikey__sjff.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        rzl__nnxyn = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        qxdn__xeqbg = c.context.make_helper(c.builder, typ.dtype, data_arr
            ).data
        nqx__jhgpd = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        cep__occbw = cgutils.get_or_insert_function(c.builder.module,
            nqx__jhgpd, name='np_array_from_array_item_array')
        arr = c.builder.call(cep__occbw, [gikey__sjff.n_arrays, c.builder.
            bitcast(qxdn__xeqbg, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), rzl__nnxyn)])
    else:
        arr = _box_array_item_array_generic(typ, c, gikey__sjff.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    oit__lpzv, sgnv__oqst, cyd__qubz = args
    qevx__nxfe = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    uqk__ftro = sig.args[1]
    if not isinstance(uqk__ftro, types.UniTuple):
        sgnv__oqst = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for cyd__qubz in range(qevx__nxfe)])
    elif uqk__ftro.count < qevx__nxfe:
        sgnv__oqst = cgutils.pack_array(builder, [builder.extract_value(
            sgnv__oqst, gtv__kdwgn) for gtv__kdwgn in range(uqk__ftro.count
            )] + [lir.Constant(lir.IntType(64), -1) for cyd__qubz in range(
            qevx__nxfe - uqk__ftro.count)])
    gnc__wbnk, cyd__qubz, cyd__qubz, cyd__qubz = construct_array_item_array(
        context, builder, array_item_type, oit__lpzv, sgnv__oqst)
    rcxaf__ijoo = context.make_helper(builder, array_item_type)
    rcxaf__ijoo.meminfo = gnc__wbnk
    return rcxaf__ijoo._getvalue()


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
    n_arrays, mpia__wzrqy, knz__cplz, fsqy__qtb = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    zrjx__rnbtk = context.get_value_type(payload_type)
    nuyr__hpejh = context.get_abi_sizeof(zrjx__rnbtk)
    tjcb__ztbtm = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    gnc__wbnk = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, nuyr__hpejh), tjcb__ztbtm)
    ixvw__rogwg = context.nrt.meminfo_data(builder, gnc__wbnk)
    ybkgq__tifby = builder.bitcast(ixvw__rogwg, zrjx__rnbtk.as_pointer())
    gikey__sjff = cgutils.create_struct_proxy(payload_type)(context, builder)
    gikey__sjff.n_arrays = n_arrays
    gikey__sjff.data = mpia__wzrqy
    gikey__sjff.offsets = knz__cplz
    gikey__sjff.null_bitmap = fsqy__qtb
    builder.store(gikey__sjff._getvalue(), ybkgq__tifby)
    context.nrt.incref(builder, signature.args[1], mpia__wzrqy)
    context.nrt.incref(builder, signature.args[2], knz__cplz)
    context.nrt.incref(builder, signature.args[3], fsqy__qtb)
    rcxaf__ijoo = context.make_helper(builder, array_item_type)
    rcxaf__ijoo.meminfo = gnc__wbnk
    return rcxaf__ijoo._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    ssx__zzlh = ArrayItemArrayType(data_type)
    sig = ssx__zzlh(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        gikey__sjff = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gikey__sjff.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        gikey__sjff = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        qxdn__xeqbg = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, gikey__sjff.offsets).data
        knz__cplz = builder.bitcast(qxdn__xeqbg, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(knz__cplz, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        gikey__sjff = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gikey__sjff.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        gikey__sjff = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gikey__sjff.null_bitmap)
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
        gikey__sjff = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return gikey__sjff.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, qarg__cfoq = args
        rcxaf__ijoo = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        ixvw__rogwg = context.nrt.meminfo_data(builder, rcxaf__ijoo.meminfo)
        ybkgq__tifby = builder.bitcast(ixvw__rogwg, context.get_value_type(
            payload_type).as_pointer())
        gikey__sjff = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(ybkgq__tifby))
        context.nrt.decref(builder, data_typ, gikey__sjff.data)
        gikey__sjff.data = qarg__cfoq
        context.nrt.incref(builder, data_typ, qarg__cfoq)
        builder.store(gikey__sjff._getvalue(), ybkgq__tifby)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    mpia__wzrqy = get_data(arr)
    mga__ycvhn = len(mpia__wzrqy)
    if mga__ycvhn < new_size:
        pfgh__ypbu = max(2 * mga__ycvhn, new_size)
        qarg__cfoq = bodo.libs.array_kernels.resize_and_copy(mpia__wzrqy,
            old_size, pfgh__ypbu)
        replace_data_arr(arr, qarg__cfoq)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    mpia__wzrqy = get_data(arr)
    knz__cplz = get_offsets(arr)
    fmj__wplw = len(mpia__wzrqy)
    yusrv__efw = knz__cplz[-1]
    if fmj__wplw != yusrv__efw:
        qarg__cfoq = bodo.libs.array_kernels.resize_and_copy(mpia__wzrqy,
            yusrv__efw, yusrv__efw)
        replace_data_arr(arr, qarg__cfoq)


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
            knz__cplz = get_offsets(arr)
            mpia__wzrqy = get_data(arr)
            qaweh__bte = knz__cplz[ind]
            sycuw__ujnsu = knz__cplz[ind + 1]
            return mpia__wzrqy[qaweh__bte:sycuw__ujnsu]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        lplw__erly = arr.dtype

        def impl_bool(arr, ind):
            usv__alts = len(arr)
            if usv__alts != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            fsqy__qtb = get_null_bitmap(arr)
            n_arrays = 0
            yxg__lbw = init_nested_counts(lplw__erly)
            for gtv__kdwgn in range(usv__alts):
                if ind[gtv__kdwgn]:
                    n_arrays += 1
                    jdt__vtucc = arr[gtv__kdwgn]
                    yxg__lbw = add_nested_counts(yxg__lbw, jdt__vtucc)
            bkw__rafis = pre_alloc_array_item_array(n_arrays, yxg__lbw,
                lplw__erly)
            wjftc__pmwsl = get_null_bitmap(bkw__rafis)
            bmg__gry = 0
            for vhuy__yblu in range(usv__alts):
                if ind[vhuy__yblu]:
                    bkw__rafis[bmg__gry] = arr[vhuy__yblu]
                    zmmbl__rfnti = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        fsqy__qtb, vhuy__yblu)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wjftc__pmwsl,
                        bmg__gry, zmmbl__rfnti)
                    bmg__gry += 1
            return bkw__rafis
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        lplw__erly = arr.dtype

        def impl_int(arr, ind):
            fsqy__qtb = get_null_bitmap(arr)
            usv__alts = len(ind)
            n_arrays = usv__alts
            yxg__lbw = init_nested_counts(lplw__erly)
            for spra__efyrj in range(usv__alts):
                gtv__kdwgn = ind[spra__efyrj]
                jdt__vtucc = arr[gtv__kdwgn]
                yxg__lbw = add_nested_counts(yxg__lbw, jdt__vtucc)
            bkw__rafis = pre_alloc_array_item_array(n_arrays, yxg__lbw,
                lplw__erly)
            wjftc__pmwsl = get_null_bitmap(bkw__rafis)
            for sqt__scau in range(usv__alts):
                vhuy__yblu = ind[sqt__scau]
                bkw__rafis[sqt__scau] = arr[vhuy__yblu]
                zmmbl__rfnti = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    fsqy__qtb, vhuy__yblu)
                bodo.libs.int_arr_ext.set_bit_to_arr(wjftc__pmwsl,
                    sqt__scau, zmmbl__rfnti)
            return bkw__rafis
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            usv__alts = len(arr)
            vitzr__fyv = numba.cpython.unicode._normalize_slice(ind, usv__alts)
            nbja__iiim = np.arange(vitzr__fyv.start, vitzr__fyv.stop,
                vitzr__fyv.step)
            return arr[nbja__iiim]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            knz__cplz = get_offsets(A)
            fsqy__qtb = get_null_bitmap(A)
            if idx == 0:
                knz__cplz[0] = 0
            n_items = len(val)
            jxke__irvwi = knz__cplz[idx] + n_items
            ensure_data_capacity(A, knz__cplz[idx], jxke__irvwi)
            mpia__wzrqy = get_data(A)
            knz__cplz[idx + 1] = knz__cplz[idx] + n_items
            mpia__wzrqy[knz__cplz[idx]:knz__cplz[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(fsqy__qtb, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            vitzr__fyv = numba.cpython.unicode._normalize_slice(idx, len(A))
            for gtv__kdwgn in range(vitzr__fyv.start, vitzr__fyv.stop,
                vitzr__fyv.step):
                A[gtv__kdwgn] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            knz__cplz = get_offsets(A)
            fsqy__qtb = get_null_bitmap(A)
            gptba__yzwqs = get_offsets(val)
            ekrno__rigqo = get_data(val)
            fvl__dpul = get_null_bitmap(val)
            usv__alts = len(A)
            vitzr__fyv = numba.cpython.unicode._normalize_slice(idx, usv__alts)
            ttmv__tui, nraiy__xcgx = vitzr__fyv.start, vitzr__fyv.stop
            assert vitzr__fyv.step == 1
            if ttmv__tui == 0:
                knz__cplz[ttmv__tui] = 0
            aii__wtz = knz__cplz[ttmv__tui]
            jxke__irvwi = aii__wtz + len(ekrno__rigqo)
            ensure_data_capacity(A, aii__wtz, jxke__irvwi)
            mpia__wzrqy = get_data(A)
            mpia__wzrqy[aii__wtz:aii__wtz + len(ekrno__rigqo)] = ekrno__rigqo
            knz__cplz[ttmv__tui:nraiy__xcgx + 1] = gptba__yzwqs + aii__wtz
            bni__ryyl = 0
            for gtv__kdwgn in range(ttmv__tui, nraiy__xcgx):
                zmmbl__rfnti = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    fvl__dpul, bni__ryyl)
                bodo.libs.int_arr_ext.set_bit_to_arr(fsqy__qtb, gtv__kdwgn,
                    zmmbl__rfnti)
                bni__ryyl += 1
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
