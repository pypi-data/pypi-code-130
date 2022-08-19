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
            .utils.is_array_typ(bbzqv__qvioq, False) for bbzqv__qvioq in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(bbzqv__qvioq,
                str) for bbzqv__qvioq in names) and len(names) == len(data)
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
        return StructType(tuple(uvfr__jjy.dtype for uvfr__jjy in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(bbzqv__qvioq) for bbzqv__qvioq in d.keys())
        data = tuple(dtype_to_array_type(uvfr__jjy) for uvfr__jjy in d.values()
            )
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(bbzqv__qvioq, False) for bbzqv__qvioq in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lyn__bvyq = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, lyn__bvyq)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        lyn__bvyq = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, lyn__bvyq)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    srm__tzej = builder.module
    syxgf__nvba = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gqn__humm = cgutils.get_or_insert_function(srm__tzej, syxgf__nvba, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not gqn__humm.is_declaration:
        return gqn__humm
    gqn__humm.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gqn__humm.append_basic_block())
    iab__edde = gqn__humm.args[0]
    rmpen__kxa = context.get_value_type(payload_type).as_pointer()
    lzzzi__gtejm = builder.bitcast(iab__edde, rmpen__kxa)
    uwjn__atzx = context.make_helper(builder, payload_type, ref=lzzzi__gtejm)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), uwjn__atzx.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        uwjn__atzx.null_bitmap)
    builder.ret_void()
    return gqn__humm


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    pyiu__atbtn = context.get_value_type(payload_type)
    azze__avk = context.get_abi_sizeof(pyiu__atbtn)
    gwzic__phfwg = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    ogy__xhlt = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, azze__avk), gwzic__phfwg)
    keugi__asy = context.nrt.meminfo_data(builder, ogy__xhlt)
    vmksf__hupqd = builder.bitcast(keugi__asy, pyiu__atbtn.as_pointer())
    uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    mzmez__rmah = 0
    for arr_typ in struct_arr_type.data:
        liwjk__opqi = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        ckra__wqfaa = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(mzmez__rmah, 
            mzmez__rmah + liwjk__opqi)])
        arr = gen_allocate_array(context, builder, arr_typ, ckra__wqfaa, c)
        arrs.append(arr)
        mzmez__rmah += liwjk__opqi
    uwjn__atzx.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    cth__dzwi = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    yyl__vpn = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [cth__dzwi])
    null_bitmap_ptr = yyl__vpn.data
    uwjn__atzx.null_bitmap = yyl__vpn._getvalue()
    builder.store(uwjn__atzx._getvalue(), vmksf__hupqd)
    return ogy__xhlt, uwjn__atzx.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    mzl__apzzi = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        stf__qxsob = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            stf__qxsob)
        mzl__apzzi.append(arr.data)
    ists__kcnp = cgutils.pack_array(c.builder, mzl__apzzi
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, mzl__apzzi)
    ewcvv__gnjaf = cgutils.alloca_once_value(c.builder, ists__kcnp)
    vajwo__hwc = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(bbzqv__qvioq.dtype)) for bbzqv__qvioq in data_typ]
    ihkf__wttv = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, vajwo__hwc))
    vnr__eqa = cgutils.pack_array(c.builder, [c.context.insert_const_string
        (c.builder.module, bbzqv__qvioq) for bbzqv__qvioq in names])
    rdbmv__vptk = cgutils.alloca_once_value(c.builder, vnr__eqa)
    return ewcvv__gnjaf, ihkf__wttv, rdbmv__vptk


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    jpk__xuvv = all(isinstance(uvfr__jjy, types.Array) and (uvfr__jjy.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) or
        isinstance(uvfr__jjy.dtype, TimeType)) for uvfr__jjy in typ.data)
    if jpk__xuvv:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        zlhtw__hgp = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            zlhtw__hgp, i) for i in range(1, zlhtw__hgp.type.count)], lir.
            IntType(64))
    ogy__xhlt, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if jpk__xuvv:
        ewcvv__gnjaf, ihkf__wttv, rdbmv__vptk = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        syxgf__nvba = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        gqn__humm = cgutils.get_or_insert_function(c.builder.module,
            syxgf__nvba, name='struct_array_from_sequence')
        c.builder.call(gqn__humm, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(ewcvv__gnjaf, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(ihkf__wttv,
            lir.IntType(8).as_pointer()), c.builder.bitcast(rdbmv__vptk,
            lir.IntType(8).as_pointer()), c.context.get_constant(types.
            bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    uxb__ipj = c.context.make_helper(c.builder, typ)
    uxb__ipj.meminfo = ogy__xhlt
    ksrc__iuery = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uxb__ipj._getvalue(), is_error=ksrc__iuery)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sni__rqjz = context.insert_const_string(builder.module, 'pandas')
    ece__ndsz = c.pyapi.import_module_noblock(sni__rqjz)
    ncgu__fisb = c.pyapi.object_getattr_string(ece__ndsz, 'NA')
    with cgutils.for_range(builder, n_structs) as uuy__yotki:
        iykm__qub = uuy__yotki.index
        vjjy__fado = seq_getitem(builder, context, val, iykm__qub)
        set_bitmap_bit(builder, null_bitmap_ptr, iykm__qub, 0)
        for niu__fpyog in range(len(typ.data)):
            arr_typ = typ.data[niu__fpyog]
            data_arr = builder.extract_value(data_tup, niu__fpyog)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            czon__kux, ecrqm__qoqpm = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, iykm__qub])
        jobgu__fcgea = is_na_value(builder, context, vjjy__fado, ncgu__fisb)
        iis__afr = builder.icmp_unsigned('!=', jobgu__fcgea, lir.Constant(
            jobgu__fcgea.type, 1))
        with builder.if_then(iis__afr):
            set_bitmap_bit(builder, null_bitmap_ptr, iykm__qub, 1)
            for niu__fpyog in range(len(typ.data)):
                arr_typ = typ.data[niu__fpyog]
                if is_tuple_array:
                    fhn__ohy = c.pyapi.tuple_getitem(vjjy__fado, niu__fpyog)
                else:
                    fhn__ohy = c.pyapi.dict_getitem_string(vjjy__fado, typ.
                        names[niu__fpyog])
                jobgu__fcgea = is_na_value(builder, context, fhn__ohy,
                    ncgu__fisb)
                iis__afr = builder.icmp_unsigned('!=', jobgu__fcgea, lir.
                    Constant(jobgu__fcgea.type, 1))
                with builder.if_then(iis__afr):
                    fhn__ohy = to_arr_obj_if_list_obj(c, context, builder,
                        fhn__ohy, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype, fhn__ohy
                        ).value
                    data_arr = builder.extract_value(data_tup, niu__fpyog)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    czon__kux, ecrqm__qoqpm = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, iykm__qub, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(vjjy__fado)
    c.pyapi.decref(ece__ndsz)
    c.pyapi.decref(ncgu__fisb)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    uxb__ipj = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    keugi__asy = context.nrt.meminfo_data(builder, uxb__ipj.meminfo)
    vmksf__hupqd = builder.bitcast(keugi__asy, context.get_value_type(
        payload_type).as_pointer())
    uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(vmksf__hupqd))
    return uwjn__atzx


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    uwjn__atzx = _get_struct_arr_payload(c.context, c.builder, typ, val)
    czon__kux, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), uwjn__atzx.null_bitmap).data
    jpk__xuvv = all(isinstance(uvfr__jjy, types.Array) and (uvfr__jjy.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) or
        isinstance(uvfr__jjy.dtype, TimeType)) for uvfr__jjy in typ.data)
    if jpk__xuvv:
        ewcvv__gnjaf, ihkf__wttv, rdbmv__vptk = _get_C_API_ptrs(c,
            uwjn__atzx.data, typ.data, typ.names)
        syxgf__nvba = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        vxzw__vrn = cgutils.get_or_insert_function(c.builder.module,
            syxgf__nvba, name='np_array_from_struct_array')
        arr = c.builder.call(vxzw__vrn, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(ewcvv__gnjaf,
            lir.IntType(8).as_pointer()), null_bitmap_ptr, c.builder.
            bitcast(ihkf__wttv, lir.IntType(8).as_pointer()), c.builder.
            bitcast(rdbmv__vptk, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, uwjn__atzx.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sni__rqjz = context.insert_const_string(builder.module, 'numpy')
    dsh__vfkzy = c.pyapi.import_module_noblock(sni__rqjz)
    hmdr__ekxh = c.pyapi.object_getattr_string(dsh__vfkzy, 'object_')
    bnt__jtfdj = c.pyapi.long_from_longlong(length)
    crw__sis = c.pyapi.call_method(dsh__vfkzy, 'ndarray', (bnt__jtfdj,
        hmdr__ekxh))
    dwaty__lpwi = c.pyapi.object_getattr_string(dsh__vfkzy, 'nan')
    with cgutils.for_range(builder, length) as uuy__yotki:
        iykm__qub = uuy__yotki.index
        pyarray_setitem(builder, context, crw__sis, iykm__qub, dwaty__lpwi)
        xlo__qghz = get_bitmap_bit(builder, null_bitmap_ptr, iykm__qub)
        baqnd__reha = builder.icmp_unsigned('!=', xlo__qghz, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(baqnd__reha):
            if is_tuple_array:
                vjjy__fado = c.pyapi.tuple_new(len(typ.data))
            else:
                vjjy__fado = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(dwaty__lpwi)
                    c.pyapi.tuple_setitem(vjjy__fado, i, dwaty__lpwi)
                else:
                    c.pyapi.dict_setitem_string(vjjy__fado, typ.names[i],
                        dwaty__lpwi)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                czon__kux, xgipr__gypy = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, iykm__qub])
                with builder.if_then(xgipr__gypy):
                    czon__kux, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, iykm__qub])
                    wrti__qxd = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(vjjy__fado, i, wrti__qxd)
                    else:
                        c.pyapi.dict_setitem_string(vjjy__fado, typ.names[i
                            ], wrti__qxd)
                        c.pyapi.decref(wrti__qxd)
            pyarray_setitem(builder, context, crw__sis, iykm__qub, vjjy__fado)
            c.pyapi.decref(vjjy__fado)
    c.pyapi.decref(dsh__vfkzy)
    c.pyapi.decref(hmdr__ekxh)
    c.pyapi.decref(bnt__jtfdj)
    c.pyapi.decref(dwaty__lpwi)
    return crw__sis


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    zhed__qexwp = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if zhed__qexwp == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for acgj__xin in range(zhed__qexwp)])
    elif nested_counts_type.count < zhed__qexwp:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for acgj__xin in range(
            zhed__qexwp - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(uvfr__jjy) for uvfr__jjy in
            names_typ.types)
    exhd__divb = tuple(uvfr__jjy.instance_type for uvfr__jjy in dtypes_typ.
        types)
    struct_arr_type = StructArrayType(exhd__divb, names)

    def codegen(context, builder, sig, args):
        wuvm__khgr, nested_counts, acgj__xin, acgj__xin = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        ogy__xhlt, acgj__xin, acgj__xin = construct_struct_array(context,
            builder, struct_arr_type, wuvm__khgr, nested_counts)
        uxb__ipj = context.make_helper(builder, struct_arr_type)
        uxb__ipj.meminfo = ogy__xhlt
        return uxb__ipj._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(bbzqv__qvioq,
            str) for bbzqv__qvioq in names) and len(names) == len(data)
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
        lyn__bvyq = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, lyn__bvyq)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        lyn__bvyq = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, lyn__bvyq)


def define_struct_dtor(context, builder, struct_type, payload_type):
    srm__tzej = builder.module
    syxgf__nvba = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gqn__humm = cgutils.get_or_insert_function(srm__tzej, syxgf__nvba, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not gqn__humm.is_declaration:
        return gqn__humm
    gqn__humm.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gqn__humm.append_basic_block())
    iab__edde = gqn__humm.args[0]
    rmpen__kxa = context.get_value_type(payload_type).as_pointer()
    lzzzi__gtejm = builder.bitcast(iab__edde, rmpen__kxa)
    uwjn__atzx = context.make_helper(builder, payload_type, ref=lzzzi__gtejm)
    for i in range(len(struct_type.data)):
        ywwl__smjw = builder.extract_value(uwjn__atzx.null_bitmap, i)
        baqnd__reha = builder.icmp_unsigned('==', ywwl__smjw, lir.Constant(
            ywwl__smjw.type, 1))
        with builder.if_then(baqnd__reha):
            val = builder.extract_value(uwjn__atzx.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return gqn__humm


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    keugi__asy = context.nrt.meminfo_data(builder, struct.meminfo)
    vmksf__hupqd = builder.bitcast(keugi__asy, context.get_value_type(
        payload_type).as_pointer())
    uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(vmksf__hupqd))
    return uwjn__atzx, vmksf__hupqd


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    sni__rqjz = context.insert_const_string(builder.module, 'pandas')
    ece__ndsz = c.pyapi.import_module_noblock(sni__rqjz)
    ncgu__fisb = c.pyapi.object_getattr_string(ece__ndsz, 'NA')
    pohwf__giw = []
    nulls = []
    for i, uvfr__jjy in enumerate(typ.data):
        wrti__qxd = c.pyapi.dict_getitem_string(val, typ.names[i])
        xgxy__gawfj = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        bamuk__oybb = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(uvfr__jjy)))
        jobgu__fcgea = is_na_value(builder, context, wrti__qxd, ncgu__fisb)
        baqnd__reha = builder.icmp_unsigned('!=', jobgu__fcgea, lir.
            Constant(jobgu__fcgea.type, 1))
        with builder.if_then(baqnd__reha):
            builder.store(context.get_constant(types.uint8, 1), xgxy__gawfj)
            field_val = c.pyapi.to_native_value(uvfr__jjy, wrti__qxd).value
            builder.store(field_val, bamuk__oybb)
        pohwf__giw.append(builder.load(bamuk__oybb))
        nulls.append(builder.load(xgxy__gawfj))
    c.pyapi.decref(ece__ndsz)
    c.pyapi.decref(ncgu__fisb)
    ogy__xhlt = construct_struct(context, builder, typ, pohwf__giw, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = ogy__xhlt
    ksrc__iuery = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=ksrc__iuery)


@box(StructType)
def box_struct(typ, val, c):
    kqz__juump = c.pyapi.dict_new(len(typ.data))
    uwjn__atzx, acgj__xin = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(kqz__juump, typ.names[i], c.pyapi.
            borrow_none())
        ywwl__smjw = c.builder.extract_value(uwjn__atzx.null_bitmap, i)
        baqnd__reha = c.builder.icmp_unsigned('==', ywwl__smjw, lir.
            Constant(ywwl__smjw.type, 1))
        with c.builder.if_then(baqnd__reha):
            kqahe__okqa = c.builder.extract_value(uwjn__atzx.data, i)
            c.context.nrt.incref(c.builder, val_typ, kqahe__okqa)
            fhn__ohy = c.pyapi.from_native_value(val_typ, kqahe__okqa, c.
                env_manager)
            c.pyapi.dict_setitem_string(kqz__juump, typ.names[i], fhn__ohy)
            c.pyapi.decref(fhn__ohy)
    c.context.nrt.decref(c.builder, typ, val)
    return kqz__juump


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(uvfr__jjy) for uvfr__jjy in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, pjj__ublhs = args
        payload_type = StructPayloadType(struct_type.data)
        pyiu__atbtn = context.get_value_type(payload_type)
        azze__avk = context.get_abi_sizeof(pyiu__atbtn)
        gwzic__phfwg = define_struct_dtor(context, builder, struct_type,
            payload_type)
        ogy__xhlt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, azze__avk), gwzic__phfwg)
        keugi__asy = context.nrt.meminfo_data(builder, ogy__xhlt)
        vmksf__hupqd = builder.bitcast(keugi__asy, pyiu__atbtn.as_pointer())
        uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        uwjn__atzx.data = data
        uwjn__atzx.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for acgj__xin in range(len(
            data_typ.types))])
        builder.store(uwjn__atzx._getvalue(), vmksf__hupqd)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = ogy__xhlt
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        uwjn__atzx, acgj__xin = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            uwjn__atzx.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        uwjn__atzx, acgj__xin = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            uwjn__atzx.null_bitmap)
    vdlih__edp = types.UniTuple(types.int8, len(struct_typ.data))
    return vdlih__edp(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, acgj__xin, val = args
        uwjn__atzx, vmksf__hupqd = _get_struct_payload(context, builder,
            struct_typ, struct)
        zeqs__nmnfq = uwjn__atzx.data
        uxlzc__apb = builder.insert_value(zeqs__nmnfq, val, field_ind)
        iqamj__hunx = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, iqamj__hunx, zeqs__nmnfq)
        context.nrt.incref(builder, iqamj__hunx, uxlzc__apb)
        uwjn__atzx.data = uxlzc__apb
        builder.store(uwjn__atzx._getvalue(), vmksf__hupqd)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    xhqvh__zpjto = get_overload_const_str(ind)
    if xhqvh__zpjto not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            xhqvh__zpjto, struct))
    return struct.names.index(xhqvh__zpjto)


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
    pyiu__atbtn = context.get_value_type(payload_type)
    azze__avk = context.get_abi_sizeof(pyiu__atbtn)
    gwzic__phfwg = define_struct_dtor(context, builder, struct_type,
        payload_type)
    ogy__xhlt = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, azze__avk), gwzic__phfwg)
    keugi__asy = context.nrt.meminfo_data(builder, ogy__xhlt)
    vmksf__hupqd = builder.bitcast(keugi__asy, pyiu__atbtn.as_pointer())
    uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder)
    uwjn__atzx.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    uwjn__atzx.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(uwjn__atzx._getvalue(), vmksf__hupqd)
    return ogy__xhlt


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    mhheo__owuw = tuple(d.dtype for d in struct_arr_typ.data)
    hmm__yen = StructType(mhheo__owuw, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        iqrw__gmi, ind = args
        uwjn__atzx = _get_struct_arr_payload(context, builder,
            struct_arr_typ, iqrw__gmi)
        pohwf__giw = []
        fpe__frszf = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            stf__qxsob = builder.extract_value(uwjn__atzx.data, i)
            xkitn__wla = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [stf__qxsob,
                ind])
            fpe__frszf.append(xkitn__wla)
            lpc__byp = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            baqnd__reha = builder.icmp_unsigned('==', xkitn__wla, lir.
                Constant(xkitn__wla.type, 1))
            with builder.if_then(baqnd__reha):
                fyig__soy = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    stf__qxsob, ind])
                builder.store(fyig__soy, lpc__byp)
            pohwf__giw.append(builder.load(lpc__byp))
        if isinstance(hmm__yen, types.DictType):
            wosvf__hwr = [context.insert_const_string(builder.module,
                uapgi__lzhul) for uapgi__lzhul in struct_arr_typ.names]
            tmr__cys = cgutils.pack_array(builder, pohwf__giw)
            iqsj__raxu = cgutils.pack_array(builder, wosvf__hwr)

            def impl(names, vals):
                d = {}
                for i, uapgi__lzhul in enumerate(names):
                    d[uapgi__lzhul] = vals[i]
                return d
            adlh__hhfzw = context.compile_internal(builder, impl, hmm__yen(
                types.Tuple(tuple(types.StringLiteral(uapgi__lzhul) for
                uapgi__lzhul in struct_arr_typ.names)), types.Tuple(
                mhheo__owuw)), [iqsj__raxu, tmr__cys])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                mhheo__owuw), tmr__cys)
            return adlh__hhfzw
        ogy__xhlt = construct_struct(context, builder, hmm__yen, pohwf__giw,
            fpe__frszf)
        struct = context.make_helper(builder, hmm__yen)
        struct.meminfo = ogy__xhlt
        return struct._getvalue()
    return hmm__yen(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        uwjn__atzx = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            uwjn__atzx.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        uwjn__atzx = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            uwjn__atzx.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(uvfr__jjy) for uvfr__jjy in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, yyl__vpn, pjj__ublhs = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        pyiu__atbtn = context.get_value_type(payload_type)
        azze__avk = context.get_abi_sizeof(pyiu__atbtn)
        gwzic__phfwg = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        ogy__xhlt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, azze__avk), gwzic__phfwg)
        keugi__asy = context.nrt.meminfo_data(builder, ogy__xhlt)
        vmksf__hupqd = builder.bitcast(keugi__asy, pyiu__atbtn.as_pointer())
        uwjn__atzx = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        uwjn__atzx.data = data
        uwjn__atzx.null_bitmap = yyl__vpn
        builder.store(uwjn__atzx._getvalue(), vmksf__hupqd)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, yyl__vpn)
        uxb__ipj = context.make_helper(builder, struct_arr_type)
        uxb__ipj.meminfo = ogy__xhlt
        return uxb__ipj._getvalue()
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
    xycz__uhxk = len(arr.data)
    xvog__ase = 'def impl(arr, ind):\n'
    xvog__ase += '  data = get_data(arr)\n'
    xvog__ase += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        xvog__ase += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        xvog__ase += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        xvog__ase += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    xvog__ase += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(xycz__uhxk)), ', '.join("'{}'".format(uapgi__lzhul) for
        uapgi__lzhul in arr.names)))
    cdu__qbtf = {}
    exec(xvog__ase, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, cdu__qbtf)
    impl = cdu__qbtf['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        xycz__uhxk = len(arr.data)
        xvog__ase = 'def impl(arr, ind, val):\n'
        xvog__ase += '  data = get_data(arr)\n'
        xvog__ase += '  null_bitmap = get_null_bitmap(arr)\n'
        xvog__ase += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(xycz__uhxk):
            if isinstance(val, StructType):
                xvog__ase += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                xvog__ase += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                xvog__ase += '  else:\n'
                xvog__ase += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                xvog__ase += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        cdu__qbtf = {}
        exec(xvog__ase, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, cdu__qbtf)
        impl = cdu__qbtf['impl']
        return impl
    if isinstance(ind, types.SliceType):
        xycz__uhxk = len(arr.data)
        xvog__ase = 'def impl(arr, ind, val):\n'
        xvog__ase += '  data = get_data(arr)\n'
        xvog__ase += '  null_bitmap = get_null_bitmap(arr)\n'
        xvog__ase += '  val_data = get_data(val)\n'
        xvog__ase += '  val_null_bitmap = get_null_bitmap(val)\n'
        xvog__ase += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(xycz__uhxk):
            xvog__ase += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        cdu__qbtf = {}
        exec(xvog__ase, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, cdu__qbtf)
        impl = cdu__qbtf['impl']
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
    xvog__ase = 'def impl(A):\n'
    xvog__ase += '  total_nbytes = 0\n'
    xvog__ase += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        xvog__ase += f'  total_nbytes += data[{i}].nbytes\n'
    xvog__ase += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    xvog__ase += '  return total_nbytes\n'
    cdu__qbtf = {}
    exec(xvog__ase, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, cdu__qbtf)
    impl = cdu__qbtf['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        yyl__vpn = get_null_bitmap(A)
        wyz__jxdwv = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        xcph__vmg = yyl__vpn.copy()
        return init_struct_arr(wyz__jxdwv, xcph__vmg, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(bbzqv__qvioq.copy() for bbzqv__qvioq in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    rst__aqw = arrs.count
    xvog__ase = 'def f(arrs):\n'
    xvog__ase += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(rst__aqw)))
    cdu__qbtf = {}
    exec(xvog__ase, {}, cdu__qbtf)
    impl = cdu__qbtf['f']
    return impl
