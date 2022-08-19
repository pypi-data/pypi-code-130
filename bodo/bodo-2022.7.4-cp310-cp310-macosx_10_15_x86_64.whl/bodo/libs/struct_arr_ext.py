"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.time_ext import TimeType
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(yqrw__yxv, False) for yqrw__yxv in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(yqrw__yxv,
                str) for yqrw__yxv in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(tkehn__tobhb.dtype for tkehn__tobhb in self
            .data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(yqrw__yxv) for yqrw__yxv in d.keys())
        data = tuple(dtype_to_array_type(tkehn__tobhb) for tkehn__tobhb in
            d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(yqrw__yxv, False) for yqrw__yxv in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bvun__dhhj = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, bvun__dhhj)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        bvun__dhhj = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, bvun__dhhj)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    txyoh__tdaeo = builder.module
    tsmn__venfv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    jcx__sfx = cgutils.get_or_insert_function(txyoh__tdaeo, tsmn__venfv,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not jcx__sfx.is_declaration:
        return jcx__sfx
    jcx__sfx.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(jcx__sfx.append_basic_block())
    jden__ztuy = jcx__sfx.args[0]
    dyoez__snrj = context.get_value_type(payload_type).as_pointer()
    dlpmu__xxp = builder.bitcast(jden__ztuy, dyoez__snrj)
    mwqg__pzs = context.make_helper(builder, payload_type, ref=dlpmu__xxp)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), mwqg__pzs.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), mwqg__pzs
        .null_bitmap)
    builder.ret_void()
    return jcx__sfx


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    trjv__iyayx = context.get_value_type(payload_type)
    tmk__yag = context.get_abi_sizeof(trjv__iyayx)
    jghrd__ufsbk = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    dlgfo__etsfo = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tmk__yag), jghrd__ufsbk)
    haxx__ncg = context.nrt.meminfo_data(builder, dlgfo__etsfo)
    wkp__namev = builder.bitcast(haxx__ncg, trjv__iyayx.as_pointer())
    mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    owne__hqow = 0
    for arr_typ in struct_arr_type.data:
        eek__nkrrl = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        blr__fhll = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(owne__hqow, owne__hqow +
            eek__nkrrl)])
        arr = gen_allocate_array(context, builder, arr_typ, blr__fhll, c)
        arrs.append(arr)
        owne__hqow += eek__nkrrl
    mwqg__pzs.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    jqwx__zptc = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    yeeo__xlxn = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [jqwx__zptc])
    null_bitmap_ptr = yeeo__xlxn.data
    mwqg__pzs.null_bitmap = yeeo__xlxn._getvalue()
    builder.store(mwqg__pzs._getvalue(), wkp__namev)
    return dlgfo__etsfo, mwqg__pzs.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    uajjw__akl = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        uyca__cubls = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            uyca__cubls)
        uajjw__akl.append(arr.data)
    qiypk__acijo = cgutils.pack_array(c.builder, uajjw__akl
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, uajjw__akl)
    eck__uge = cgutils.alloca_once_value(c.builder, qiypk__acijo)
    qzqoj__yumx = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(yqrw__yxv.dtype)) for yqrw__yxv in data_typ]
    fgfxw__kxta = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, qzqoj__yumx))
    tjpt__dueiy = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, yqrw__yxv) for yqrw__yxv in
        names])
    ymem__lfy = cgutils.alloca_once_value(c.builder, tjpt__dueiy)
    return eck__uge, fgfxw__kxta, ymem__lfy


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    bwsc__lrp = all(isinstance(tkehn__tobhb, types.Array) and (tkehn__tobhb
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) or isinstance(tkehn__tobhb.dtype, TimeType)) for
        tkehn__tobhb in typ.data)
    if bwsc__lrp:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        snw__buo = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            snw__buo, i) for i in range(1, snw__buo.type.count)], lir.
            IntType(64))
    dlgfo__etsfo, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if bwsc__lrp:
        eck__uge, fgfxw__kxta, ymem__lfy = _get_C_API_ptrs(c, data_tup, typ
            .data, typ.names)
        tsmn__venfv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        jcx__sfx = cgutils.get_or_insert_function(c.builder.module,
            tsmn__venfv, name='struct_array_from_sequence')
        c.builder.call(jcx__sfx, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(eck__uge, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(fgfxw__kxta,
            lir.IntType(8).as_pointer()), c.builder.bitcast(ymem__lfy, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    khc__vptf = c.context.make_helper(c.builder, typ)
    khc__vptf.meminfo = dlgfo__etsfo
    ygdz__zbl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(khc__vptf._getvalue(), is_error=ygdz__zbl)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    algq__mzu = context.insert_const_string(builder.module, 'pandas')
    jdi__jtoep = c.pyapi.import_module_noblock(algq__mzu)
    sxx__xrojm = c.pyapi.object_getattr_string(jdi__jtoep, 'NA')
    with cgutils.for_range(builder, n_structs) as lcnsi__xhvph:
        nggbz__cptz = lcnsi__xhvph.index
        qhwzb__ahj = seq_getitem(builder, context, val, nggbz__cptz)
        set_bitmap_bit(builder, null_bitmap_ptr, nggbz__cptz, 0)
        for tnye__upmpo in range(len(typ.data)):
            arr_typ = typ.data[tnye__upmpo]
            data_arr = builder.extract_value(data_tup, tnye__upmpo)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            dcc__bwbc, yix__zfuc = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, nggbz__cptz])
        restj__ref = is_na_value(builder, context, qhwzb__ahj, sxx__xrojm)
        aese__ndtwb = builder.icmp_unsigned('!=', restj__ref, lir.Constant(
            restj__ref.type, 1))
        with builder.if_then(aese__ndtwb):
            set_bitmap_bit(builder, null_bitmap_ptr, nggbz__cptz, 1)
            for tnye__upmpo in range(len(typ.data)):
                arr_typ = typ.data[tnye__upmpo]
                if is_tuple_array:
                    shog__dcwy = c.pyapi.tuple_getitem(qhwzb__ahj, tnye__upmpo)
                else:
                    shog__dcwy = c.pyapi.dict_getitem_string(qhwzb__ahj,
                        typ.names[tnye__upmpo])
                restj__ref = is_na_value(builder, context, shog__dcwy,
                    sxx__xrojm)
                aese__ndtwb = builder.icmp_unsigned('!=', restj__ref, lir.
                    Constant(restj__ref.type, 1))
                with builder.if_then(aese__ndtwb):
                    shog__dcwy = to_arr_obj_if_list_obj(c, context, builder,
                        shog__dcwy, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        shog__dcwy).value
                    data_arr = builder.extract_value(data_tup, tnye__upmpo)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    dcc__bwbc, yix__zfuc = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, nggbz__cptz, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(qhwzb__ahj)
    c.pyapi.decref(jdi__jtoep)
    c.pyapi.decref(sxx__xrojm)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    khc__vptf = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    haxx__ncg = context.nrt.meminfo_data(builder, khc__vptf.meminfo)
    wkp__namev = builder.bitcast(haxx__ncg, context.get_value_type(
        payload_type).as_pointer())
    mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(wkp__namev))
    return mwqg__pzs


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    mwqg__pzs = _get_struct_arr_payload(c.context, c.builder, typ, val)
    dcc__bwbc, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), mwqg__pzs.null_bitmap).data
    bwsc__lrp = all(isinstance(tkehn__tobhb, types.Array) and (tkehn__tobhb
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) or isinstance(tkehn__tobhb.dtype, TimeType)) for
        tkehn__tobhb in typ.data)
    if bwsc__lrp:
        eck__uge, fgfxw__kxta, ymem__lfy = _get_C_API_ptrs(c, mwqg__pzs.
            data, typ.data, typ.names)
        tsmn__venfv = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        arf__wssn = cgutils.get_or_insert_function(c.builder.module,
            tsmn__venfv, name='np_array_from_struct_array')
        arr = c.builder.call(arf__wssn, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(eck__uge, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            fgfxw__kxta, lir.IntType(8).as_pointer()), c.builder.bitcast(
            ymem__lfy, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, mwqg__pzs.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    algq__mzu = context.insert_const_string(builder.module, 'numpy')
    vfnzd__zcwm = c.pyapi.import_module_noblock(algq__mzu)
    jkj__vbzw = c.pyapi.object_getattr_string(vfnzd__zcwm, 'object_')
    dajm__irav = c.pyapi.long_from_longlong(length)
    jyayt__cewu = c.pyapi.call_method(vfnzd__zcwm, 'ndarray', (dajm__irav,
        jkj__vbzw))
    klla__occ = c.pyapi.object_getattr_string(vfnzd__zcwm, 'nan')
    with cgutils.for_range(builder, length) as lcnsi__xhvph:
        nggbz__cptz = lcnsi__xhvph.index
        pyarray_setitem(builder, context, jyayt__cewu, nggbz__cptz, klla__occ)
        bbc__alv = get_bitmap_bit(builder, null_bitmap_ptr, nggbz__cptz)
        dexof__gtxp = builder.icmp_unsigned('!=', bbc__alv, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(dexof__gtxp):
            if is_tuple_array:
                qhwzb__ahj = c.pyapi.tuple_new(len(typ.data))
            else:
                qhwzb__ahj = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(klla__occ)
                    c.pyapi.tuple_setitem(qhwzb__ahj, i, klla__occ)
                else:
                    c.pyapi.dict_setitem_string(qhwzb__ahj, typ.names[i],
                        klla__occ)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                dcc__bwbc, dff__lpoqz = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, nggbz__cptz])
                with builder.if_then(dff__lpoqz):
                    dcc__bwbc, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, nggbz__cptz])
                    joj__ooyj = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(qhwzb__ahj, i, joj__ooyj)
                    else:
                        c.pyapi.dict_setitem_string(qhwzb__ahj, typ.names[i
                            ], joj__ooyj)
                        c.pyapi.decref(joj__ooyj)
            pyarray_setitem(builder, context, jyayt__cewu, nggbz__cptz,
                qhwzb__ahj)
            c.pyapi.decref(qhwzb__ahj)
    c.pyapi.decref(vfnzd__zcwm)
    c.pyapi.decref(jkj__vbzw)
    c.pyapi.decref(dajm__irav)
    c.pyapi.decref(klla__occ)
    return jyayt__cewu


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    zdv__rbs = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if zdv__rbs == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for rqfee__cqvtj in range(zdv__rbs)])
    elif nested_counts_type.count < zdv__rbs:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for rqfee__cqvtj in range(
            zdv__rbs - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(tkehn__tobhb) for tkehn__tobhb in
            names_typ.types)
    ximew__aqm = tuple(tkehn__tobhb.instance_type for tkehn__tobhb in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(ximew__aqm, names)

    def codegen(context, builder, sig, args):
        jfpc__mmy, nested_counts, rqfee__cqvtj, rqfee__cqvtj = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        dlgfo__etsfo, rqfee__cqvtj, rqfee__cqvtj = construct_struct_array(
            context, builder, struct_arr_type, jfpc__mmy, nested_counts)
        khc__vptf = context.make_helper(builder, struct_arr_type)
        khc__vptf.meminfo = dlgfo__etsfo
        return khc__vptf._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(yqrw__yxv, str) for
            yqrw__yxv in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bvun__dhhj = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, bvun__dhhj)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        bvun__dhhj = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, bvun__dhhj)


def define_struct_dtor(context, builder, struct_type, payload_type):
    txyoh__tdaeo = builder.module
    tsmn__venfv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    jcx__sfx = cgutils.get_or_insert_function(txyoh__tdaeo, tsmn__venfv,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not jcx__sfx.is_declaration:
        return jcx__sfx
    jcx__sfx.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(jcx__sfx.append_basic_block())
    jden__ztuy = jcx__sfx.args[0]
    dyoez__snrj = context.get_value_type(payload_type).as_pointer()
    dlpmu__xxp = builder.bitcast(jden__ztuy, dyoez__snrj)
    mwqg__pzs = context.make_helper(builder, payload_type, ref=dlpmu__xxp)
    for i in range(len(struct_type.data)):
        zxwz__fhi = builder.extract_value(mwqg__pzs.null_bitmap, i)
        dexof__gtxp = builder.icmp_unsigned('==', zxwz__fhi, lir.Constant(
            zxwz__fhi.type, 1))
        with builder.if_then(dexof__gtxp):
            val = builder.extract_value(mwqg__pzs.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return jcx__sfx


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    haxx__ncg = context.nrt.meminfo_data(builder, struct.meminfo)
    wkp__namev = builder.bitcast(haxx__ncg, context.get_value_type(
        payload_type).as_pointer())
    mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(wkp__namev))
    return mwqg__pzs, wkp__namev


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    algq__mzu = context.insert_const_string(builder.module, 'pandas')
    jdi__jtoep = c.pyapi.import_module_noblock(algq__mzu)
    sxx__xrojm = c.pyapi.object_getattr_string(jdi__jtoep, 'NA')
    wlgc__hevhg = []
    nulls = []
    for i, tkehn__tobhb in enumerate(typ.data):
        joj__ooyj = c.pyapi.dict_getitem_string(val, typ.names[i])
        vymb__lwau = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        xwp__ihwbz = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(tkehn__tobhb)))
        restj__ref = is_na_value(builder, context, joj__ooyj, sxx__xrojm)
        dexof__gtxp = builder.icmp_unsigned('!=', restj__ref, lir.Constant(
            restj__ref.type, 1))
        with builder.if_then(dexof__gtxp):
            builder.store(context.get_constant(types.uint8, 1), vymb__lwau)
            field_val = c.pyapi.to_native_value(tkehn__tobhb, joj__ooyj).value
            builder.store(field_val, xwp__ihwbz)
        wlgc__hevhg.append(builder.load(xwp__ihwbz))
        nulls.append(builder.load(vymb__lwau))
    c.pyapi.decref(jdi__jtoep)
    c.pyapi.decref(sxx__xrojm)
    dlgfo__etsfo = construct_struct(context, builder, typ, wlgc__hevhg, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = dlgfo__etsfo
    ygdz__zbl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=ygdz__zbl)


@box(StructType)
def box_struct(typ, val, c):
    wloea__sup = c.pyapi.dict_new(len(typ.data))
    mwqg__pzs, rqfee__cqvtj = _get_struct_payload(c.context, c.builder, typ,
        val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(wloea__sup, typ.names[i], c.pyapi.
            borrow_none())
        zxwz__fhi = c.builder.extract_value(mwqg__pzs.null_bitmap, i)
        dexof__gtxp = c.builder.icmp_unsigned('==', zxwz__fhi, lir.Constant
            (zxwz__fhi.type, 1))
        with c.builder.if_then(dexof__gtxp):
            boalp__dar = c.builder.extract_value(mwqg__pzs.data, i)
            c.context.nrt.incref(c.builder, val_typ, boalp__dar)
            shog__dcwy = c.pyapi.from_native_value(val_typ, boalp__dar, c.
                env_manager)
            c.pyapi.dict_setitem_string(wloea__sup, typ.names[i], shog__dcwy)
            c.pyapi.decref(shog__dcwy)
    c.context.nrt.decref(c.builder, typ, val)
    return wloea__sup


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(tkehn__tobhb) for tkehn__tobhb in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, eadkr__eeiy = args
        payload_type = StructPayloadType(struct_type.data)
        trjv__iyayx = context.get_value_type(payload_type)
        tmk__yag = context.get_abi_sizeof(trjv__iyayx)
        jghrd__ufsbk = define_struct_dtor(context, builder, struct_type,
            payload_type)
        dlgfo__etsfo = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tmk__yag), jghrd__ufsbk)
        haxx__ncg = context.nrt.meminfo_data(builder, dlgfo__etsfo)
        wkp__namev = builder.bitcast(haxx__ncg, trjv__iyayx.as_pointer())
        mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder)
        mwqg__pzs.data = data
        mwqg__pzs.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for rqfee__cqvtj in range(len(
            data_typ.types))])
        builder.store(mwqg__pzs._getvalue(), wkp__namev)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = dlgfo__etsfo
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        mwqg__pzs, rqfee__cqvtj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mwqg__pzs.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        mwqg__pzs, rqfee__cqvtj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mwqg__pzs.null_bitmap)
    vllz__cxy = types.UniTuple(types.int8, len(struct_typ.data))
    return vllz__cxy(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, rqfee__cqvtj, val = args
        mwqg__pzs, wkp__namev = _get_struct_payload(context, builder,
            struct_typ, struct)
        svmyh__kvlc = mwqg__pzs.data
        ehe__jqji = builder.insert_value(svmyh__kvlc, val, field_ind)
        wpm__bkw = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, wpm__bkw, svmyh__kvlc)
        context.nrt.incref(builder, wpm__bkw, ehe__jqji)
        mwqg__pzs.data = ehe__jqji
        builder.store(mwqg__pzs._getvalue(), wkp__namev)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    hrhu__tzkwm = get_overload_const_str(ind)
    if hrhu__tzkwm not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            hrhu__tzkwm, struct))
    return struct.names.index(hrhu__tzkwm)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    trjv__iyayx = context.get_value_type(payload_type)
    tmk__yag = context.get_abi_sizeof(trjv__iyayx)
    jghrd__ufsbk = define_struct_dtor(context, builder, struct_type,
        payload_type)
    dlgfo__etsfo = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tmk__yag), jghrd__ufsbk)
    haxx__ncg = context.nrt.meminfo_data(builder, dlgfo__etsfo)
    wkp__namev = builder.bitcast(haxx__ncg, trjv__iyayx.as_pointer())
    mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder)
    mwqg__pzs.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    mwqg__pzs.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(mwqg__pzs._getvalue(), wkp__namev)
    return dlgfo__etsfo


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    fgpjx__jfm = tuple(d.dtype for d in struct_arr_typ.data)
    fupsr__gzff = StructType(fgpjx__jfm, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        xuwok__qyi, ind = args
        mwqg__pzs = _get_struct_arr_payload(context, builder,
            struct_arr_typ, xuwok__qyi)
        wlgc__hevhg = []
        sdzhw__qinej = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            uyca__cubls = builder.extract_value(mwqg__pzs.data, i)
            mvl__dwjv = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                uyca__cubls, ind])
            sdzhw__qinej.append(mvl__dwjv)
            ngaf__srkrg = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            dexof__gtxp = builder.icmp_unsigned('==', mvl__dwjv, lir.
                Constant(mvl__dwjv.type, 1))
            with builder.if_then(dexof__gtxp):
                gvjb__ablp = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    uyca__cubls, ind])
                builder.store(gvjb__ablp, ngaf__srkrg)
            wlgc__hevhg.append(builder.load(ngaf__srkrg))
        if isinstance(fupsr__gzff, types.DictType):
            ugcgr__ore = [context.insert_const_string(builder.module,
                rxks__wwkf) for rxks__wwkf in struct_arr_typ.names]
            ulwdx__jowxg = cgutils.pack_array(builder, wlgc__hevhg)
            nrm__uoz = cgutils.pack_array(builder, ugcgr__ore)

            def impl(names, vals):
                d = {}
                for i, rxks__wwkf in enumerate(names):
                    d[rxks__wwkf] = vals[i]
                return d
            hkcok__ppqei = context.compile_internal(builder, impl,
                fupsr__gzff(types.Tuple(tuple(types.StringLiteral(
                rxks__wwkf) for rxks__wwkf in struct_arr_typ.names)), types
                .Tuple(fgpjx__jfm)), [nrm__uoz, ulwdx__jowxg])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                fgpjx__jfm), ulwdx__jowxg)
            return hkcok__ppqei
        dlgfo__etsfo = construct_struct(context, builder, fupsr__gzff,
            wlgc__hevhg, sdzhw__qinej)
        struct = context.make_helper(builder, fupsr__gzff)
        struct.meminfo = dlgfo__etsfo
        return struct._getvalue()
    return fupsr__gzff(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mwqg__pzs = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mwqg__pzs.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mwqg__pzs = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mwqg__pzs.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(tkehn__tobhb) for tkehn__tobhb in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, yeeo__xlxn, eadkr__eeiy = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        trjv__iyayx = context.get_value_type(payload_type)
        tmk__yag = context.get_abi_sizeof(trjv__iyayx)
        jghrd__ufsbk = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        dlgfo__etsfo = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tmk__yag), jghrd__ufsbk)
        haxx__ncg = context.nrt.meminfo_data(builder, dlgfo__etsfo)
        wkp__namev = builder.bitcast(haxx__ncg, trjv__iyayx.as_pointer())
        mwqg__pzs = cgutils.create_struct_proxy(payload_type)(context, builder)
        mwqg__pzs.data = data
        mwqg__pzs.null_bitmap = yeeo__xlxn
        builder.store(mwqg__pzs._getvalue(), wkp__namev)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, yeeo__xlxn)
        khc__vptf = context.make_helper(builder, struct_arr_type)
        khc__vptf.meminfo = dlgfo__etsfo
        return khc__vptf._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    xhz__znta = len(arr.data)
    sev__kuou = 'def impl(arr, ind):\n'
    sev__kuou += '  data = get_data(arr)\n'
    sev__kuou += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        sev__kuou += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        sev__kuou += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        sev__kuou += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    sev__kuou += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(xhz__znta)), ', '.join("'{}'".format(rxks__wwkf) for
        rxks__wwkf in arr.names)))
    cma__pbwax = {}
    exec(sev__kuou, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, cma__pbwax)
    impl = cma__pbwax['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        xhz__znta = len(arr.data)
        sev__kuou = 'def impl(arr, ind, val):\n'
        sev__kuou += '  data = get_data(arr)\n'
        sev__kuou += '  null_bitmap = get_null_bitmap(arr)\n'
        sev__kuou += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(xhz__znta):
            if isinstance(val, StructType):
                sev__kuou += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                sev__kuou += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                sev__kuou += '  else:\n'
                sev__kuou += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                sev__kuou += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        cma__pbwax = {}
        exec(sev__kuou, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, cma__pbwax)
        impl = cma__pbwax['impl']
        return impl
    if isinstance(ind, types.SliceType):
        xhz__znta = len(arr.data)
        sev__kuou = 'def impl(arr, ind, val):\n'
        sev__kuou += '  data = get_data(arr)\n'
        sev__kuou += '  null_bitmap = get_null_bitmap(arr)\n'
        sev__kuou += '  val_data = get_data(val)\n'
        sev__kuou += '  val_null_bitmap = get_null_bitmap(val)\n'
        sev__kuou += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(xhz__znta):
            sev__kuou += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        cma__pbwax = {}
        exec(sev__kuou, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, cma__pbwax)
        impl = cma__pbwax['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    sev__kuou = 'def impl(A):\n'
    sev__kuou += '  total_nbytes = 0\n'
    sev__kuou += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        sev__kuou += f'  total_nbytes += data[{i}].nbytes\n'
    sev__kuou += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    sev__kuou += '  return total_nbytes\n'
    cma__pbwax = {}
    exec(sev__kuou, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, cma__pbwax)
    impl = cma__pbwax['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        yeeo__xlxn = get_null_bitmap(A)
        hyw__murcu = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        zia__wxr = yeeo__xlxn.copy()
        return init_struct_arr(hyw__murcu, zia__wxr, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(yqrw__yxv.copy() for yqrw__yxv in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    kgom__rmk = arrs.count
    sev__kuou = 'def f(arrs):\n'
    sev__kuou += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(kgom__rmk)))
    cma__pbwax = {}
    exec(sev__kuou, {}, cma__pbwax)
    impl = cma__pbwax['f']
    return impl
