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
        oqmln__vksw = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, oqmln__vksw)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        oqmln__vksw = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, oqmln__vksw)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    yxya__vlzo = builder.module
    glm__ozovj = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    hmy__hdfp = cgutils.get_or_insert_function(yxya__vlzo, glm__ozovj, name
        ='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not hmy__hdfp.is_declaration:
        return hmy__hdfp
    hmy__hdfp.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(hmy__hdfp.append_basic_block())
    ltb__nrl = hmy__hdfp.args[0]
    fnon__aygvu = context.get_value_type(payload_type).as_pointer()
    ewc__tlfa = builder.bitcast(ltb__nrl, fnon__aygvu)
    esxga__elwa = context.make_helper(builder, payload_type, ref=ewc__tlfa)
    context.nrt.decref(builder, array_item_type.dtype, esxga__elwa.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        esxga__elwa.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        esxga__elwa.null_bitmap)
    builder.ret_void()
    return hmy__hdfp


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    vprm__ems = context.get_value_type(payload_type)
    kulu__fndmr = context.get_abi_sizeof(vprm__ems)
    zorro__tty = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    vnz__upcay = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, kulu__fndmr), zorro__tty)
    nhsul__mgsyk = context.nrt.meminfo_data(builder, vnz__upcay)
    hvbch__xup = builder.bitcast(nhsul__mgsyk, vprm__ems.as_pointer())
    esxga__elwa = cgutils.create_struct_proxy(payload_type)(context, builder)
    esxga__elwa.n_arrays = n_arrays
    ukzqi__ing = n_elems.type.count
    mexy__drm = builder.extract_value(n_elems, 0)
    odlze__ghb = cgutils.alloca_once_value(builder, mexy__drm)
    ufhx__jeynj = builder.icmp_signed('==', mexy__drm, lir.Constant(
        mexy__drm.type, -1))
    with builder.if_then(ufhx__jeynj):
        builder.store(n_arrays, odlze__ghb)
    n_elems = cgutils.pack_array(builder, [builder.load(odlze__ghb)] + [
        builder.extract_value(n_elems, nbzh__joy) for nbzh__joy in range(1,
        ukzqi__ing)])
    esxga__elwa.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    gng__ruer = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    knyf__othvg = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [gng__ruer])
    offsets_ptr = knyf__othvg.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    esxga__elwa.offsets = knyf__othvg._getvalue()
    sjvxg__klcyp = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    mkxm__vxr = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [sjvxg__klcyp])
    null_bitmap_ptr = mkxm__vxr.data
    esxga__elwa.null_bitmap = mkxm__vxr._getvalue()
    builder.store(esxga__elwa._getvalue(), hvbch__xup)
    return vnz__upcay, esxga__elwa.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    eoab__cviy, kyo__qeu = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mlzta__ohbt = context.insert_const_string(builder.module, 'pandas')
    kdcm__qeex = c.pyapi.import_module_noblock(mlzta__ohbt)
    rqq__gsxqx = c.pyapi.object_getattr_string(kdcm__qeex, 'NA')
    xatl__coofr = c.context.get_constant(offset_type, 0)
    builder.store(xatl__coofr, offsets_ptr)
    oshd__uspxp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as vbykt__xwwc:
        njb__lyoz = vbykt__xwwc.index
        item_ind = builder.load(oshd__uspxp)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [njb__lyoz]))
        arr_obj = seq_getitem(builder, context, val, njb__lyoz)
        set_bitmap_bit(builder, null_bitmap_ptr, njb__lyoz, 0)
        wxmbc__zqh = is_na_value(builder, context, arr_obj, rqq__gsxqx)
        vdj__clg = builder.icmp_unsigned('!=', wxmbc__zqh, lir.Constant(
            wxmbc__zqh.type, 1))
        with builder.if_then(vdj__clg):
            set_bitmap_bit(builder, null_bitmap_ptr, njb__lyoz, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), oshd__uspxp)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(oshd__uspxp), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(kdcm__qeex)
    c.pyapi.decref(rqq__gsxqx)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    xty__csh = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if xty__csh:
        glm__ozovj = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        abq__ggnam = cgutils.get_or_insert_function(c.builder.module,
            glm__ozovj, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(abq__ggnam,
            [val])])
    else:
        yjcev__brmlh = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            yjcev__brmlh, nbzh__joy) for nbzh__joy in range(1, yjcev__brmlh
            .type.count)])
    vnz__upcay, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if xty__csh:
        urt__hzo = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        dfg__ywd = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        glm__ozovj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        hmy__hdfp = cgutils.get_or_insert_function(c.builder.module,
            glm__ozovj, name='array_item_array_from_sequence')
        c.builder.call(hmy__hdfp, [val, c.builder.bitcast(dfg__ywd, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), urt__hzo)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    jfzdx__dihob = c.context.make_helper(c.builder, typ)
    jfzdx__dihob.meminfo = vnz__upcay
    fvmms__rqvo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jfzdx__dihob._getvalue(), is_error=fvmms__rqvo)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    jfzdx__dihob = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    nhsul__mgsyk = context.nrt.meminfo_data(builder, jfzdx__dihob.meminfo)
    hvbch__xup = builder.bitcast(nhsul__mgsyk, context.get_value_type(
        payload_type).as_pointer())
    esxga__elwa = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(hvbch__xup))
    return esxga__elwa


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mlzta__ohbt = context.insert_const_string(builder.module, 'numpy')
    his__npl = c.pyapi.import_module_noblock(mlzta__ohbt)
    exq__bhyye = c.pyapi.object_getattr_string(his__npl, 'object_')
    jcaq__ieyyd = c.pyapi.long_from_longlong(n_arrays)
    wmj__pkoy = c.pyapi.call_method(his__npl, 'ndarray', (jcaq__ieyyd,
        exq__bhyye))
    esh__ghge = c.pyapi.object_getattr_string(his__npl, 'nan')
    oshd__uspxp = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as vbykt__xwwc:
        njb__lyoz = vbykt__xwwc.index
        pyarray_setitem(builder, context, wmj__pkoy, njb__lyoz, esh__ghge)
        jzrdu__gnvi = get_bitmap_bit(builder, null_bitmap_ptr, njb__lyoz)
        sru__jos = builder.icmp_unsigned('!=', jzrdu__gnvi, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(sru__jos):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(njb__lyoz, lir.Constant(njb__lyoz
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                njb__lyoz]))), lir.IntType(64))
            item_ind = builder.load(oshd__uspxp)
            eoab__cviy, bbve__vudkx = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), oshd__uspxp)
            arr_obj = c.pyapi.from_native_value(typ.dtype, bbve__vudkx, c.
                env_manager)
            pyarray_setitem(builder, context, wmj__pkoy, njb__lyoz, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(his__npl)
    c.pyapi.decref(exq__bhyye)
    c.pyapi.decref(jcaq__ieyyd)
    c.pyapi.decref(esh__ghge)
    return wmj__pkoy


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    esxga__elwa = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = esxga__elwa.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), esxga__elwa.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), esxga__elwa.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        urt__hzo = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        dfg__ywd = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        glm__ozovj = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        njx__opqo = cgutils.get_or_insert_function(c.builder.module,
            glm__ozovj, name='np_array_from_array_item_array')
        arr = c.builder.call(njx__opqo, [esxga__elwa.n_arrays, c.builder.
            bitcast(dfg__ywd, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), urt__hzo)])
    else:
        arr = _box_array_item_array_generic(typ, c, esxga__elwa.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    jmyf__jfz, rmtc__upr, kbrpj__eyolo = args
    sdhun__bwddk = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    rkrc__necv = sig.args[1]
    if not isinstance(rkrc__necv, types.UniTuple):
        rmtc__upr = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for kbrpj__eyolo in range(sdhun__bwddk)])
    elif rkrc__necv.count < sdhun__bwddk:
        rmtc__upr = cgutils.pack_array(builder, [builder.extract_value(
            rmtc__upr, nbzh__joy) for nbzh__joy in range(rkrc__necv.count)] +
            [lir.Constant(lir.IntType(64), -1) for kbrpj__eyolo in range(
            sdhun__bwddk - rkrc__necv.count)])
    vnz__upcay, kbrpj__eyolo, kbrpj__eyolo, kbrpj__eyolo = (
        construct_array_item_array(context, builder, array_item_type,
        jmyf__jfz, rmtc__upr))
    jfzdx__dihob = context.make_helper(builder, array_item_type)
    jfzdx__dihob.meminfo = vnz__upcay
    return jfzdx__dihob._getvalue()


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
    n_arrays, ijasc__ete, knyf__othvg, mkxm__vxr = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    vprm__ems = context.get_value_type(payload_type)
    kulu__fndmr = context.get_abi_sizeof(vprm__ems)
    zorro__tty = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    vnz__upcay = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, kulu__fndmr), zorro__tty)
    nhsul__mgsyk = context.nrt.meminfo_data(builder, vnz__upcay)
    hvbch__xup = builder.bitcast(nhsul__mgsyk, vprm__ems.as_pointer())
    esxga__elwa = cgutils.create_struct_proxy(payload_type)(context, builder)
    esxga__elwa.n_arrays = n_arrays
    esxga__elwa.data = ijasc__ete
    esxga__elwa.offsets = knyf__othvg
    esxga__elwa.null_bitmap = mkxm__vxr
    builder.store(esxga__elwa._getvalue(), hvbch__xup)
    context.nrt.incref(builder, signature.args[1], ijasc__ete)
    context.nrt.incref(builder, signature.args[2], knyf__othvg)
    context.nrt.incref(builder, signature.args[3], mkxm__vxr)
    jfzdx__dihob = context.make_helper(builder, array_item_type)
    jfzdx__dihob.meminfo = vnz__upcay
    return jfzdx__dihob._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    fdw__bozh = ArrayItemArrayType(data_type)
    sig = fdw__bozh(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        esxga__elwa = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            esxga__elwa.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        esxga__elwa = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        dfg__ywd = context.make_array(types.Array(offset_type, 1, 'C'))(context
            , builder, esxga__elwa.offsets).data
        knyf__othvg = builder.bitcast(dfg__ywd, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(knyf__othvg, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        esxga__elwa = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            esxga__elwa.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        esxga__elwa = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            esxga__elwa.null_bitmap)
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
        esxga__elwa = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return esxga__elwa.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, hnmq__ubop = args
        jfzdx__dihob = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        nhsul__mgsyk = context.nrt.meminfo_data(builder, jfzdx__dihob.meminfo)
        hvbch__xup = builder.bitcast(nhsul__mgsyk, context.get_value_type(
            payload_type).as_pointer())
        esxga__elwa = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(hvbch__xup))
        context.nrt.decref(builder, data_typ, esxga__elwa.data)
        esxga__elwa.data = hnmq__ubop
        context.nrt.incref(builder, data_typ, hnmq__ubop)
        builder.store(esxga__elwa._getvalue(), hvbch__xup)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    ijasc__ete = get_data(arr)
    lwgx__zkksw = len(ijasc__ete)
    if lwgx__zkksw < new_size:
        bwedx__swm = max(2 * lwgx__zkksw, new_size)
        hnmq__ubop = bodo.libs.array_kernels.resize_and_copy(ijasc__ete,
            old_size, bwedx__swm)
        replace_data_arr(arr, hnmq__ubop)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    ijasc__ete = get_data(arr)
    knyf__othvg = get_offsets(arr)
    ykhgf__asxtn = len(ijasc__ete)
    uotk__indlr = knyf__othvg[-1]
    if ykhgf__asxtn != uotk__indlr:
        hnmq__ubop = bodo.libs.array_kernels.resize_and_copy(ijasc__ete,
            uotk__indlr, uotk__indlr)
        replace_data_arr(arr, hnmq__ubop)


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
            knyf__othvg = get_offsets(arr)
            ijasc__ete = get_data(arr)
            lkhv__ewac = knyf__othvg[ind]
            xef__wue = knyf__othvg[ind + 1]
            return ijasc__ete[lkhv__ewac:xef__wue]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        fhfrp__akeik = arr.dtype

        def impl_bool(arr, ind):
            wdgvd__drq = len(arr)
            if wdgvd__drq != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            mkxm__vxr = get_null_bitmap(arr)
            n_arrays = 0
            auv__wgel = init_nested_counts(fhfrp__akeik)
            for nbzh__joy in range(wdgvd__drq):
                if ind[nbzh__joy]:
                    n_arrays += 1
                    jnoou__lru = arr[nbzh__joy]
                    auv__wgel = add_nested_counts(auv__wgel, jnoou__lru)
            wmj__pkoy = pre_alloc_array_item_array(n_arrays, auv__wgel,
                fhfrp__akeik)
            juu__qdgj = get_null_bitmap(wmj__pkoy)
            pkw__igrl = 0
            for ezgz__kny in range(wdgvd__drq):
                if ind[ezgz__kny]:
                    wmj__pkoy[pkw__igrl] = arr[ezgz__kny]
                    rsv__cyywp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        mkxm__vxr, ezgz__kny)
                    bodo.libs.int_arr_ext.set_bit_to_arr(juu__qdgj,
                        pkw__igrl, rsv__cyywp)
                    pkw__igrl += 1
            return wmj__pkoy
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        fhfrp__akeik = arr.dtype

        def impl_int(arr, ind):
            mkxm__vxr = get_null_bitmap(arr)
            wdgvd__drq = len(ind)
            n_arrays = wdgvd__drq
            auv__wgel = init_nested_counts(fhfrp__akeik)
            for tvhoy__nscr in range(wdgvd__drq):
                nbzh__joy = ind[tvhoy__nscr]
                jnoou__lru = arr[nbzh__joy]
                auv__wgel = add_nested_counts(auv__wgel, jnoou__lru)
            wmj__pkoy = pre_alloc_array_item_array(n_arrays, auv__wgel,
                fhfrp__akeik)
            juu__qdgj = get_null_bitmap(wmj__pkoy)
            for owb__bihsr in range(wdgvd__drq):
                ezgz__kny = ind[owb__bihsr]
                wmj__pkoy[owb__bihsr] = arr[ezgz__kny]
                rsv__cyywp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(mkxm__vxr
                    , ezgz__kny)
                bodo.libs.int_arr_ext.set_bit_to_arr(juu__qdgj, owb__bihsr,
                    rsv__cyywp)
            return wmj__pkoy
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            wdgvd__drq = len(arr)
            ezrb__fvu = numba.cpython.unicode._normalize_slice(ind, wdgvd__drq)
            esi__dqc = np.arange(ezrb__fvu.start, ezrb__fvu.stop, ezrb__fvu
                .step)
            return arr[esi__dqc]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            knyf__othvg = get_offsets(A)
            mkxm__vxr = get_null_bitmap(A)
            if idx == 0:
                knyf__othvg[0] = 0
            n_items = len(val)
            qejs__gbb = knyf__othvg[idx] + n_items
            ensure_data_capacity(A, knyf__othvg[idx], qejs__gbb)
            ijasc__ete = get_data(A)
            knyf__othvg[idx + 1] = knyf__othvg[idx] + n_items
            ijasc__ete[knyf__othvg[idx]:knyf__othvg[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(mkxm__vxr, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            ezrb__fvu = numba.cpython.unicode._normalize_slice(idx, len(A))
            for nbzh__joy in range(ezrb__fvu.start, ezrb__fvu.stop,
                ezrb__fvu.step):
                A[nbzh__joy] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            knyf__othvg = get_offsets(A)
            mkxm__vxr = get_null_bitmap(A)
            zfad__yechb = get_offsets(val)
            jinzm__gyupc = get_data(val)
            hplw__dbqhs = get_null_bitmap(val)
            wdgvd__drq = len(A)
            ezrb__fvu = numba.cpython.unicode._normalize_slice(idx, wdgvd__drq)
            balb__nhkx, bqr__rnx = ezrb__fvu.start, ezrb__fvu.stop
            assert ezrb__fvu.step == 1
            if balb__nhkx == 0:
                knyf__othvg[balb__nhkx] = 0
            yot__gpypb = knyf__othvg[balb__nhkx]
            qejs__gbb = yot__gpypb + len(jinzm__gyupc)
            ensure_data_capacity(A, yot__gpypb, qejs__gbb)
            ijasc__ete = get_data(A)
            ijasc__ete[yot__gpypb:yot__gpypb + len(jinzm__gyupc)
                ] = jinzm__gyupc
            knyf__othvg[balb__nhkx:bqr__rnx + 1] = zfad__yechb + yot__gpypb
            mjqmd__lacxw = 0
            for nbzh__joy in range(balb__nhkx, bqr__rnx):
                rsv__cyywp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    hplw__dbqhs, mjqmd__lacxw)
                bodo.libs.int_arr_ext.set_bit_to_arr(mkxm__vxr, nbzh__joy,
                    rsv__cyywp)
                mjqmd__lacxw += 1
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
