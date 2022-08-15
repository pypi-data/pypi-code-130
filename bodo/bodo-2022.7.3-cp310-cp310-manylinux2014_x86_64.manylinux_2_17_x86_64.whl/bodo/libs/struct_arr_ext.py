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
            .utils.is_array_typ(asxz__ujhe, False) for asxz__ujhe in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(asxz__ujhe,
                str) for asxz__ujhe in names) and len(names) == len(data)
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
        return StructType(tuple(pqbq__skxlt.dtype for pqbq__skxlt in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(asxz__ujhe) for asxz__ujhe in d.keys())
        data = tuple(dtype_to_array_type(pqbq__skxlt) for pqbq__skxlt in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(asxz__ujhe, False) for asxz__ujhe in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqy__nge = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, zqy__nge)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        zqy__nge = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, zqy__nge)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    jocg__vfb = builder.module
    rikac__lmb = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vucd__tbwna = cgutils.get_or_insert_function(jocg__vfb, rikac__lmb,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not vucd__tbwna.is_declaration:
        return vucd__tbwna
    vucd__tbwna.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vucd__tbwna.append_basic_block())
    jns__tupn = vucd__tbwna.args[0]
    eaep__pwna = context.get_value_type(payload_type).as_pointer()
    mzpob__xsbaj = builder.bitcast(jns__tupn, eaep__pwna)
    hhnys__xdeb = context.make_helper(builder, payload_type, ref=mzpob__xsbaj)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), hhnys__xdeb.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        hhnys__xdeb.null_bitmap)
    builder.ret_void()
    return vucd__tbwna


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    eqqpm__zsqph = context.get_value_type(payload_type)
    onuem__loi = context.get_abi_sizeof(eqqpm__zsqph)
    itrwy__nmg = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    adb__psmxe = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, onuem__loi), itrwy__nmg)
    tjvk__wjg = context.nrt.meminfo_data(builder, adb__psmxe)
    zoiax__dgmv = builder.bitcast(tjvk__wjg, eqqpm__zsqph.as_pointer())
    hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    exkx__lpesf = 0
    for arr_typ in struct_arr_type.data:
        vzrr__kqwid = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        pqc__fbon = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(exkx__lpesf, 
            exkx__lpesf + vzrr__kqwid)])
        arr = gen_allocate_array(context, builder, arr_typ, pqc__fbon, c)
        arrs.append(arr)
        exkx__lpesf += vzrr__kqwid
    hhnys__xdeb.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    yec__ftdcs = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    chw__ommq = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [yec__ftdcs])
    null_bitmap_ptr = chw__ommq.data
    hhnys__xdeb.null_bitmap = chw__ommq._getvalue()
    builder.store(hhnys__xdeb._getvalue(), zoiax__dgmv)
    return adb__psmxe, hhnys__xdeb.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    ibh__epef = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        jln__nfya = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            jln__nfya)
        ibh__epef.append(arr.data)
    itomk__qubp = cgutils.pack_array(c.builder, ibh__epef
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, ibh__epef)
    cnhz__atw = cgutils.alloca_once_value(c.builder, itomk__qubp)
    gwqh__zpsl = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(asxz__ujhe.dtype)) for asxz__ujhe in data_typ]
    eyuy__lrxtx = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, gwqh__zpsl))
    mowju__vxzo = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, asxz__ujhe) for asxz__ujhe in
        names])
    yndr__xlvf = cgutils.alloca_once_value(c.builder, mowju__vxzo)
    return cnhz__atw, eyuy__lrxtx, yndr__xlvf


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    oaj__vhh = all(isinstance(pqbq__skxlt, types.Array) and pqbq__skxlt.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for pqbq__skxlt in typ.data)
    if oaj__vhh:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        klqb__qefxh = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            klqb__qefxh, i) for i in range(1, klqb__qefxh.type.count)], lir
            .IntType(64))
    adb__psmxe, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if oaj__vhh:
        cnhz__atw, eyuy__lrxtx, yndr__xlvf = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        rikac__lmb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        vucd__tbwna = cgutils.get_or_insert_function(c.builder.module,
            rikac__lmb, name='struct_array_from_sequence')
        c.builder.call(vucd__tbwna, [val, c.context.get_constant(types.
            int32, len(typ.data)), c.builder.bitcast(cnhz__atw, lir.IntType
            (8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            eyuy__lrxtx, lir.IntType(8).as_pointer()), c.builder.bitcast(
            yndr__xlvf, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    wyu__bhk = c.context.make_helper(c.builder, typ)
    wyu__bhk.meminfo = adb__psmxe
    wupmg__dco = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wyu__bhk._getvalue(), is_error=wupmg__dco)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    toqtb__lshdy = context.insert_const_string(builder.module, 'pandas')
    npai__rsyyc = c.pyapi.import_module_noblock(toqtb__lshdy)
    ygc__bii = c.pyapi.object_getattr_string(npai__rsyyc, 'NA')
    with cgutils.for_range(builder, n_structs) as haio__comae:
        kozec__lkksg = haio__comae.index
        rmjl__icutw = seq_getitem(builder, context, val, kozec__lkksg)
        set_bitmap_bit(builder, null_bitmap_ptr, kozec__lkksg, 0)
        for nykca__dls in range(len(typ.data)):
            arr_typ = typ.data[nykca__dls]
            data_arr = builder.extract_value(data_tup, nykca__dls)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            kffsw__rqwoy, qggs__aoawh = c.pyapi.call_jit_code(set_na, sig,
                [data_arr, kozec__lkksg])
        osnl__avz = is_na_value(builder, context, rmjl__icutw, ygc__bii)
        olox__dael = builder.icmp_unsigned('!=', osnl__avz, lir.Constant(
            osnl__avz.type, 1))
        with builder.if_then(olox__dael):
            set_bitmap_bit(builder, null_bitmap_ptr, kozec__lkksg, 1)
            for nykca__dls in range(len(typ.data)):
                arr_typ = typ.data[nykca__dls]
                if is_tuple_array:
                    iiobu__ety = c.pyapi.tuple_getitem(rmjl__icutw, nykca__dls)
                else:
                    iiobu__ety = c.pyapi.dict_getitem_string(rmjl__icutw,
                        typ.names[nykca__dls])
                osnl__avz = is_na_value(builder, context, iiobu__ety, ygc__bii)
                olox__dael = builder.icmp_unsigned('!=', osnl__avz, lir.
                    Constant(osnl__avz.type, 1))
                with builder.if_then(olox__dael):
                    iiobu__ety = to_arr_obj_if_list_obj(c, context, builder,
                        iiobu__ety, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        iiobu__ety).value
                    data_arr = builder.extract_value(data_tup, nykca__dls)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    kffsw__rqwoy, qggs__aoawh = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, kozec__lkksg, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(rmjl__icutw)
    c.pyapi.decref(npai__rsyyc)
    c.pyapi.decref(ygc__bii)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    wyu__bhk = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    tjvk__wjg = context.nrt.meminfo_data(builder, wyu__bhk.meminfo)
    zoiax__dgmv = builder.bitcast(tjvk__wjg, context.get_value_type(
        payload_type).as_pointer())
    hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(zoiax__dgmv))
    return hhnys__xdeb


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    hhnys__xdeb = _get_struct_arr_payload(c.context, c.builder, typ, val)
    kffsw__rqwoy, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), hhnys__xdeb.null_bitmap).data
    oaj__vhh = all(isinstance(pqbq__skxlt, types.Array) and pqbq__skxlt.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for pqbq__skxlt in typ.data)
    if oaj__vhh:
        cnhz__atw, eyuy__lrxtx, yndr__xlvf = _get_C_API_ptrs(c, hhnys__xdeb
            .data, typ.data, typ.names)
        rikac__lmb = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        nec__koz = cgutils.get_or_insert_function(c.builder.module,
            rikac__lmb, name='np_array_from_struct_array')
        arr = c.builder.call(nec__koz, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(cnhz__atw, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            eyuy__lrxtx, lir.IntType(8).as_pointer()), c.builder.bitcast(
            yndr__xlvf, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, hhnys__xdeb.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    toqtb__lshdy = context.insert_const_string(builder.module, 'numpy')
    vhod__bcpbf = c.pyapi.import_module_noblock(toqtb__lshdy)
    bqwn__qcz = c.pyapi.object_getattr_string(vhod__bcpbf, 'object_')
    iyitc__wlm = c.pyapi.long_from_longlong(length)
    lpbe__jsxl = c.pyapi.call_method(vhod__bcpbf, 'ndarray', (iyitc__wlm,
        bqwn__qcz))
    hxtzy__kawt = c.pyapi.object_getattr_string(vhod__bcpbf, 'nan')
    with cgutils.for_range(builder, length) as haio__comae:
        kozec__lkksg = haio__comae.index
        pyarray_setitem(builder, context, lpbe__jsxl, kozec__lkksg, hxtzy__kawt
            )
        vgt__kbyb = get_bitmap_bit(builder, null_bitmap_ptr, kozec__lkksg)
        yikbe__lsvkg = builder.icmp_unsigned('!=', vgt__kbyb, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(yikbe__lsvkg):
            if is_tuple_array:
                rmjl__icutw = c.pyapi.tuple_new(len(typ.data))
            else:
                rmjl__icutw = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(hxtzy__kawt)
                    c.pyapi.tuple_setitem(rmjl__icutw, i, hxtzy__kawt)
                else:
                    c.pyapi.dict_setitem_string(rmjl__icutw, typ.names[i],
                        hxtzy__kawt)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                kffsw__rqwoy, gaiwx__jhxzd = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, kozec__lkksg])
                with builder.if_then(gaiwx__jhxzd):
                    kffsw__rqwoy, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, kozec__lkksg])
                    cljh__qpyhe = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(rmjl__icutw, i, cljh__qpyhe)
                    else:
                        c.pyapi.dict_setitem_string(rmjl__icutw, typ.names[
                            i], cljh__qpyhe)
                        c.pyapi.decref(cljh__qpyhe)
            pyarray_setitem(builder, context, lpbe__jsxl, kozec__lkksg,
                rmjl__icutw)
            c.pyapi.decref(rmjl__icutw)
    c.pyapi.decref(vhod__bcpbf)
    c.pyapi.decref(bqwn__qcz)
    c.pyapi.decref(iyitc__wlm)
    c.pyapi.decref(hxtzy__kawt)
    return lpbe__jsxl


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    cteq__ybugf = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if cteq__ybugf == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for bbc__ntcik in range(cteq__ybugf)])
    elif nested_counts_type.count < cteq__ybugf:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for bbc__ntcik in range(
            cteq__ybugf - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(pqbq__skxlt) for pqbq__skxlt in
            names_typ.types)
    yxs__mmoj = tuple(pqbq__skxlt.instance_type for pqbq__skxlt in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(yxs__mmoj, names)

    def codegen(context, builder, sig, args):
        liq__dnju, nested_counts, bbc__ntcik, bbc__ntcik = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        adb__psmxe, bbc__ntcik, bbc__ntcik = construct_struct_array(context,
            builder, struct_arr_type, liq__dnju, nested_counts)
        wyu__bhk = context.make_helper(builder, struct_arr_type)
        wyu__bhk.meminfo = adb__psmxe
        return wyu__bhk._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(asxz__ujhe, str) for
            asxz__ujhe in names) and len(names) == len(data)
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
        zqy__nge = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, zqy__nge)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        zqy__nge = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, zqy__nge)


def define_struct_dtor(context, builder, struct_type, payload_type):
    jocg__vfb = builder.module
    rikac__lmb = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vucd__tbwna = cgutils.get_or_insert_function(jocg__vfb, rikac__lmb,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not vucd__tbwna.is_declaration:
        return vucd__tbwna
    vucd__tbwna.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vucd__tbwna.append_basic_block())
    jns__tupn = vucd__tbwna.args[0]
    eaep__pwna = context.get_value_type(payload_type).as_pointer()
    mzpob__xsbaj = builder.bitcast(jns__tupn, eaep__pwna)
    hhnys__xdeb = context.make_helper(builder, payload_type, ref=mzpob__xsbaj)
    for i in range(len(struct_type.data)):
        ppce__tbdlz = builder.extract_value(hhnys__xdeb.null_bitmap, i)
        yikbe__lsvkg = builder.icmp_unsigned('==', ppce__tbdlz, lir.
            Constant(ppce__tbdlz.type, 1))
        with builder.if_then(yikbe__lsvkg):
            val = builder.extract_value(hhnys__xdeb.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return vucd__tbwna


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    tjvk__wjg = context.nrt.meminfo_data(builder, struct.meminfo)
    zoiax__dgmv = builder.bitcast(tjvk__wjg, context.get_value_type(
        payload_type).as_pointer())
    hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(zoiax__dgmv))
    return hhnys__xdeb, zoiax__dgmv


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    toqtb__lshdy = context.insert_const_string(builder.module, 'pandas')
    npai__rsyyc = c.pyapi.import_module_noblock(toqtb__lshdy)
    ygc__bii = c.pyapi.object_getattr_string(npai__rsyyc, 'NA')
    xbx__wsxp = []
    nulls = []
    for i, pqbq__skxlt in enumerate(typ.data):
        cljh__qpyhe = c.pyapi.dict_getitem_string(val, typ.names[i])
        cbmgy__dkx = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        ichaa__ifh = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(pqbq__skxlt)))
        osnl__avz = is_na_value(builder, context, cljh__qpyhe, ygc__bii)
        yikbe__lsvkg = builder.icmp_unsigned('!=', osnl__avz, lir.Constant(
            osnl__avz.type, 1))
        with builder.if_then(yikbe__lsvkg):
            builder.store(context.get_constant(types.uint8, 1), cbmgy__dkx)
            field_val = c.pyapi.to_native_value(pqbq__skxlt, cljh__qpyhe).value
            builder.store(field_val, ichaa__ifh)
        xbx__wsxp.append(builder.load(ichaa__ifh))
        nulls.append(builder.load(cbmgy__dkx))
    c.pyapi.decref(npai__rsyyc)
    c.pyapi.decref(ygc__bii)
    adb__psmxe = construct_struct(context, builder, typ, xbx__wsxp, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = adb__psmxe
    wupmg__dco = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=wupmg__dco)


@box(StructType)
def box_struct(typ, val, c):
    kms__luauh = c.pyapi.dict_new(len(typ.data))
    hhnys__xdeb, bbc__ntcik = _get_struct_payload(c.context, c.builder, typ,
        val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(kms__luauh, typ.names[i], c.pyapi.
            borrow_none())
        ppce__tbdlz = c.builder.extract_value(hhnys__xdeb.null_bitmap, i)
        yikbe__lsvkg = c.builder.icmp_unsigned('==', ppce__tbdlz, lir.
            Constant(ppce__tbdlz.type, 1))
        with c.builder.if_then(yikbe__lsvkg):
            bxgrc__yjep = c.builder.extract_value(hhnys__xdeb.data, i)
            c.context.nrt.incref(c.builder, val_typ, bxgrc__yjep)
            iiobu__ety = c.pyapi.from_native_value(val_typ, bxgrc__yjep, c.
                env_manager)
            c.pyapi.dict_setitem_string(kms__luauh, typ.names[i], iiobu__ety)
            c.pyapi.decref(iiobu__ety)
    c.context.nrt.decref(c.builder, typ, val)
    return kms__luauh


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(pqbq__skxlt) for pqbq__skxlt in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, sdpdk__mdy = args
        payload_type = StructPayloadType(struct_type.data)
        eqqpm__zsqph = context.get_value_type(payload_type)
        onuem__loi = context.get_abi_sizeof(eqqpm__zsqph)
        itrwy__nmg = define_struct_dtor(context, builder, struct_type,
            payload_type)
        adb__psmxe = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, onuem__loi), itrwy__nmg)
        tjvk__wjg = context.nrt.meminfo_data(builder, adb__psmxe)
        zoiax__dgmv = builder.bitcast(tjvk__wjg, eqqpm__zsqph.as_pointer())
        hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        hhnys__xdeb.data = data
        hhnys__xdeb.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for bbc__ntcik in range(len(
            data_typ.types))])
        builder.store(hhnys__xdeb._getvalue(), zoiax__dgmv)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = adb__psmxe
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hhnys__xdeb, bbc__ntcik = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hhnys__xdeb.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hhnys__xdeb, bbc__ntcik = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hhnys__xdeb.null_bitmap)
    ygmm__zyw = types.UniTuple(types.int8, len(struct_typ.data))
    return ygmm__zyw(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, bbc__ntcik, val = args
        hhnys__xdeb, zoiax__dgmv = _get_struct_payload(context, builder,
            struct_typ, struct)
        eofbv__ijsw = hhnys__xdeb.data
        igm__mivs = builder.insert_value(eofbv__ijsw, val, field_ind)
        bmpv__sjvq = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, bmpv__sjvq, eofbv__ijsw)
        context.nrt.incref(builder, bmpv__sjvq, igm__mivs)
        hhnys__xdeb.data = igm__mivs
        builder.store(hhnys__xdeb._getvalue(), zoiax__dgmv)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    wvdca__bcj = get_overload_const_str(ind)
    if wvdca__bcj not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            wvdca__bcj, struct))
    return struct.names.index(wvdca__bcj)


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
    eqqpm__zsqph = context.get_value_type(payload_type)
    onuem__loi = context.get_abi_sizeof(eqqpm__zsqph)
    itrwy__nmg = define_struct_dtor(context, builder, struct_type, payload_type
        )
    adb__psmxe = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, onuem__loi), itrwy__nmg)
    tjvk__wjg = context.nrt.meminfo_data(builder, adb__psmxe)
    zoiax__dgmv = builder.bitcast(tjvk__wjg, eqqpm__zsqph.as_pointer())
    hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context, builder)
    hhnys__xdeb.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    hhnys__xdeb.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(hhnys__xdeb._getvalue(), zoiax__dgmv)
    return adb__psmxe


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    dno__lcuho = tuple(d.dtype for d in struct_arr_typ.data)
    bcxq__kscdi = StructType(dno__lcuho, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        ueh__lmqvi, ind = args
        hhnys__xdeb = _get_struct_arr_payload(context, builder,
            struct_arr_typ, ueh__lmqvi)
        xbx__wsxp = []
        tqfr__wufn = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            jln__nfya = builder.extract_value(hhnys__xdeb.data, i)
            ljsr__dfrry = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [jln__nfya,
                ind])
            tqfr__wufn.append(ljsr__dfrry)
            xqcfp__nfmhi = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            yikbe__lsvkg = builder.icmp_unsigned('==', ljsr__dfrry, lir.
                Constant(ljsr__dfrry.type, 1))
            with builder.if_then(yikbe__lsvkg):
                mgxc__rmqvx = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    jln__nfya, ind])
                builder.store(mgxc__rmqvx, xqcfp__nfmhi)
            xbx__wsxp.append(builder.load(xqcfp__nfmhi))
        if isinstance(bcxq__kscdi, types.DictType):
            wre__xcp = [context.insert_const_string(builder.module,
                eosjm__tizjc) for eosjm__tizjc in struct_arr_typ.names]
            ltn__tpis = cgutils.pack_array(builder, xbx__wsxp)
            dpf__xtdq = cgutils.pack_array(builder, wre__xcp)

            def impl(names, vals):
                d = {}
                for i, eosjm__tizjc in enumerate(names):
                    d[eosjm__tizjc] = vals[i]
                return d
            rduo__vhk = context.compile_internal(builder, impl, bcxq__kscdi
                (types.Tuple(tuple(types.StringLiteral(eosjm__tizjc) for
                eosjm__tizjc in struct_arr_typ.names)), types.Tuple(
                dno__lcuho)), [dpf__xtdq, ltn__tpis])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                dno__lcuho), ltn__tpis)
            return rduo__vhk
        adb__psmxe = construct_struct(context, builder, bcxq__kscdi,
            xbx__wsxp, tqfr__wufn)
        struct = context.make_helper(builder, bcxq__kscdi)
        struct.meminfo = adb__psmxe
        return struct._getvalue()
    return bcxq__kscdi(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hhnys__xdeb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hhnys__xdeb.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hhnys__xdeb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hhnys__xdeb.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(pqbq__skxlt) for pqbq__skxlt in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, chw__ommq, sdpdk__mdy = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        eqqpm__zsqph = context.get_value_type(payload_type)
        onuem__loi = context.get_abi_sizeof(eqqpm__zsqph)
        itrwy__nmg = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        adb__psmxe = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, onuem__loi), itrwy__nmg)
        tjvk__wjg = context.nrt.meminfo_data(builder, adb__psmxe)
        zoiax__dgmv = builder.bitcast(tjvk__wjg, eqqpm__zsqph.as_pointer())
        hhnys__xdeb = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        hhnys__xdeb.data = data
        hhnys__xdeb.null_bitmap = chw__ommq
        builder.store(hhnys__xdeb._getvalue(), zoiax__dgmv)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, chw__ommq)
        wyu__bhk = context.make_helper(builder, struct_arr_type)
        wyu__bhk.meminfo = adb__psmxe
        return wyu__bhk._getvalue()
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
    bll__eymw = len(arr.data)
    irlgu__nnola = 'def impl(arr, ind):\n'
    irlgu__nnola += '  data = get_data(arr)\n'
    irlgu__nnola += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        irlgu__nnola += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        irlgu__nnola += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        irlgu__nnola += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    irlgu__nnola += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(bll__eymw)), ', '.join("'{}'".format(eosjm__tizjc) for
        eosjm__tizjc in arr.names)))
    icvb__jeo = {}
    exec(irlgu__nnola, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, icvb__jeo)
    impl = icvb__jeo['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        bll__eymw = len(arr.data)
        irlgu__nnola = 'def impl(arr, ind, val):\n'
        irlgu__nnola += '  data = get_data(arr)\n'
        irlgu__nnola += '  null_bitmap = get_null_bitmap(arr)\n'
        irlgu__nnola += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(bll__eymw):
            if isinstance(val, StructType):
                irlgu__nnola += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                irlgu__nnola += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                irlgu__nnola += '  else:\n'
                irlgu__nnola += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                irlgu__nnola += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        icvb__jeo = {}
        exec(irlgu__nnola, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, icvb__jeo)
        impl = icvb__jeo['impl']
        return impl
    if isinstance(ind, types.SliceType):
        bll__eymw = len(arr.data)
        irlgu__nnola = 'def impl(arr, ind, val):\n'
        irlgu__nnola += '  data = get_data(arr)\n'
        irlgu__nnola += '  null_bitmap = get_null_bitmap(arr)\n'
        irlgu__nnola += '  val_data = get_data(val)\n'
        irlgu__nnola += '  val_null_bitmap = get_null_bitmap(val)\n'
        irlgu__nnola += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(bll__eymw):
            irlgu__nnola += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        icvb__jeo = {}
        exec(irlgu__nnola, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, icvb__jeo)
        impl = icvb__jeo['impl']
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
    irlgu__nnola = 'def impl(A):\n'
    irlgu__nnola += '  total_nbytes = 0\n'
    irlgu__nnola += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        irlgu__nnola += f'  total_nbytes += data[{i}].nbytes\n'
    irlgu__nnola += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    irlgu__nnola += '  return total_nbytes\n'
    icvb__jeo = {}
    exec(irlgu__nnola, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, icvb__jeo)
    impl = icvb__jeo['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        chw__ommq = get_null_bitmap(A)
        xvb__rcwn = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        gznom__kej = chw__ommq.copy()
        return init_struct_arr(xvb__rcwn, gznom__kej, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(asxz__ujhe.copy() for asxz__ujhe in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    lph__srzt = arrs.count
    irlgu__nnola = 'def f(arrs):\n'
    irlgu__nnola += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(lph__srzt)))
    icvb__jeo = {}
    exec(irlgu__nnola, {}, icvb__jeo)
    impl = icvb__jeo['f']
    return impl
