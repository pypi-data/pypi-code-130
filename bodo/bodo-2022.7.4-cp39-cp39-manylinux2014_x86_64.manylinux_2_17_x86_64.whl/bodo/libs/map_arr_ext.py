"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    ilds__czsd = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(ilds__czsd)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vreuh__dugw = _get_map_arr_data_type(fe_type)
        rsjba__nyap = [('data', vreuh__dugw)]
        models.StructModel.__init__(self, dmm, fe_type, rsjba__nyap)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    sfo__lbtrb = all(isinstance(amdd__ziqts, types.Array) and amdd__ziqts.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for amdd__ziqts in (typ.key_arr_type, typ.
        value_arr_type))
    if sfo__lbtrb:
        nrgbc__rrpze = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        sqb__rtivw = cgutils.get_or_insert_function(c.builder.module,
            nrgbc__rrpze, name='count_total_elems_list_array')
        wkb__vtlel = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            sqb__rtivw, [val])])
    else:
        wkb__vtlel = get_array_elem_counts(c, c.builder, c.context, val, typ)
    vreuh__dugw = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, vreuh__dugw,
        wkb__vtlel, c)
    vwi__ysede = _get_array_item_arr_payload(c.context, c.builder,
        vreuh__dugw, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, vwi__ysede.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, vwi__ysede.offsets).data
    snl__acha = _get_struct_arr_payload(c.context, c.builder, vreuh__dugw.
        dtype, vwi__ysede.data)
    key_arr = c.builder.extract_value(snl__acha.data, 0)
    value_arr = c.builder.extract_value(snl__acha.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ebxu__zkpou, sfx__cxoww = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [snl__acha.null_bitmap])
    if sfo__lbtrb:
        tpt__tmsz = c.context.make_array(vreuh__dugw.dtype.data[0])(c.
            context, c.builder, key_arr).data
        opk__teuer = c.context.make_array(vreuh__dugw.dtype.data[1])(c.
            context, c.builder, value_arr).data
        nrgbc__rrpze = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        yye__rjn = cgutils.get_or_insert_function(c.builder.module,
            nrgbc__rrpze, name='map_array_from_sequence')
        qpjrc__vmra = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ghzrj__llt = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(yye__rjn, [val, c.builder.bitcast(tpt__tmsz, lir.
            IntType(8).as_pointer()), c.builder.bitcast(opk__teuer, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), qpjrc__vmra), lir.Constant(lir.
            IntType(32), ghzrj__llt)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    mlui__bwkmv = c.context.make_helper(c.builder, typ)
    mlui__bwkmv.data = data_arr
    drl__qlbe = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mlui__bwkmv._getvalue(), is_error=drl__qlbe)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    iwn__bpwjs = context.insert_const_string(builder.module, 'pandas')
    cvzw__iwsp = c.pyapi.import_module_noblock(iwn__bpwjs)
    mqu__god = c.pyapi.object_getattr_string(cvzw__iwsp, 'NA')
    wkfl__sofm = c.context.get_constant(offset_type, 0)
    builder.store(wkfl__sofm, offsets_ptr)
    agtad__cvh = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as dcw__qvbt:
        zjm__koiwl = dcw__qvbt.index
        item_ind = builder.load(agtad__cvh)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [zjm__koiwl]))
        zjgww__xgzja = seq_getitem(builder, context, val, zjm__koiwl)
        set_bitmap_bit(builder, null_bitmap_ptr, zjm__koiwl, 0)
        ytvix__cegve = is_na_value(builder, context, zjgww__xgzja, mqu__god)
        ogi__pyrp = builder.icmp_unsigned('!=', ytvix__cegve, lir.Constant(
            ytvix__cegve.type, 1))
        with builder.if_then(ogi__pyrp):
            set_bitmap_bit(builder, null_bitmap_ptr, zjm__koiwl, 1)
            wvmg__jqe = dict_keys(builder, context, zjgww__xgzja)
            jpeei__mgk = dict_values(builder, context, zjgww__xgzja)
            n_items = bodo.utils.utils.object_length(c, wvmg__jqe)
            _unbox_array_item_array_copy_data(typ.key_arr_type, wvmg__jqe,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                jpeei__mgk, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), agtad__cvh)
            c.pyapi.decref(wvmg__jqe)
            c.pyapi.decref(jpeei__mgk)
        c.pyapi.decref(zjgww__xgzja)
    builder.store(builder.trunc(builder.load(agtad__cvh), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(cvzw__iwsp)
    c.pyapi.decref(mqu__god)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    mlui__bwkmv = c.context.make_helper(c.builder, typ, val)
    data_arr = mlui__bwkmv.data
    vreuh__dugw = _get_map_arr_data_type(typ)
    vwi__ysede = _get_array_item_arr_payload(c.context, c.builder,
        vreuh__dugw, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, vwi__ysede.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, vwi__ysede.offsets).data
    snl__acha = _get_struct_arr_payload(c.context, c.builder, vreuh__dugw.
        dtype, vwi__ysede.data)
    key_arr = c.builder.extract_value(snl__acha.data, 0)
    value_arr = c.builder.extract_value(snl__acha.data, 1)
    if all(isinstance(amdd__ziqts, types.Array) and amdd__ziqts.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        amdd__ziqts in (typ.key_arr_type, typ.value_arr_type)):
        tpt__tmsz = c.context.make_array(vreuh__dugw.dtype.data[0])(c.
            context, c.builder, key_arr).data
        opk__teuer = c.context.make_array(vreuh__dugw.dtype.data[1])(c.
            context, c.builder, value_arr).data
        nrgbc__rrpze = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        dlfby__nefz = cgutils.get_or_insert_function(c.builder.module,
            nrgbc__rrpze, name='np_array_from_map_array')
        qpjrc__vmra = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ghzrj__llt = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(dlfby__nefz, [vwi__ysede.n_arrays, c.builder.
            bitcast(tpt__tmsz, lir.IntType(8).as_pointer()), c.builder.
            bitcast(opk__teuer, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), qpjrc__vmra),
            lir.Constant(lir.IntType(32), ghzrj__llt)])
    else:
        arr = _box_map_array_generic(typ, c, vwi__ysede.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    iwn__bpwjs = context.insert_const_string(builder.module, 'numpy')
    dzaz__gyk = c.pyapi.import_module_noblock(iwn__bpwjs)
    jnqu__pdxnh = c.pyapi.object_getattr_string(dzaz__gyk, 'object_')
    eemo__cyx = c.pyapi.long_from_longlong(n_maps)
    rfoca__cnu = c.pyapi.call_method(dzaz__gyk, 'ndarray', (eemo__cyx,
        jnqu__pdxnh))
    ccqd__coffu = c.pyapi.object_getattr_string(dzaz__gyk, 'nan')
    iziu__urnl = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    agtad__cvh = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as dcw__qvbt:
        dlda__arni = dcw__qvbt.index
        pyarray_setitem(builder, context, rfoca__cnu, dlda__arni, ccqd__coffu)
        ioi__wsdkc = get_bitmap_bit(builder, null_bitmap_ptr, dlda__arni)
        uwd__dryrv = builder.icmp_unsigned('!=', ioi__wsdkc, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(uwd__dryrv):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(dlda__arni, lir.Constant(
                dlda__arni.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [dlda__arni]))), lir.IntType(64))
            item_ind = builder.load(agtad__cvh)
            zjgww__xgzja = c.pyapi.dict_new()
            eskao__rbi = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ebxu__zkpou, qeuot__aoph = c.pyapi.call_jit_code(eskao__rbi,
                typ.key_arr_type(typ.key_arr_type, types.int64, types.int64
                ), [key_arr, item_ind, n_items])
            ebxu__zkpou, asesi__jcp = c.pyapi.call_jit_code(eskao__rbi, typ
                .value_arr_type(typ.value_arr_type, types.int64, types.
                int64), [value_arr, item_ind, n_items])
            fmdhq__zrx = c.pyapi.from_native_value(typ.key_arr_type,
                qeuot__aoph, c.env_manager)
            shd__klg = c.pyapi.from_native_value(typ.value_arr_type,
                asesi__jcp, c.env_manager)
            tzhf__ljr = c.pyapi.call_function_objargs(iziu__urnl, (
                fmdhq__zrx, shd__klg))
            dict_merge_from_seq2(builder, context, zjgww__xgzja, tzhf__ljr)
            builder.store(builder.add(item_ind, n_items), agtad__cvh)
            pyarray_setitem(builder, context, rfoca__cnu, dlda__arni,
                zjgww__xgzja)
            c.pyapi.decref(tzhf__ljr)
            c.pyapi.decref(fmdhq__zrx)
            c.pyapi.decref(shd__klg)
            c.pyapi.decref(zjgww__xgzja)
    c.pyapi.decref(iziu__urnl)
    c.pyapi.decref(dzaz__gyk)
    c.pyapi.decref(jnqu__pdxnh)
    c.pyapi.decref(eemo__cyx)
    c.pyapi.decref(ccqd__coffu)
    return rfoca__cnu


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    mlui__bwkmv = context.make_helper(builder, sig.return_type)
    mlui__bwkmv.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return mlui__bwkmv._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    zwlr__npkvh = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return zwlr__npkvh(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    viv__rwi = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(num_maps
        , nested_counts, struct_typ)
    return init_map_arr(viv__rwi)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    zutu__obb = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            gmea__tdguf = val.keys()
            pgtp__cfmx = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), zutu__obb, ('key', 'value'))
            for hoz__ukod, fkd__hte in enumerate(gmea__tdguf):
                pgtp__cfmx[hoz__ukod] = bodo.libs.struct_arr_ext.init_struct((
                    fkd__hte, val[fkd__hte]), ('key', 'value'))
            arr._data[ind] = pgtp__cfmx
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            nal__hkgtq = dict()
            ahay__ggzue = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            pgtp__cfmx = bodo.libs.array_item_arr_ext.get_data(arr._data)
            lwu__avh, lygi__ljjv = bodo.libs.struct_arr_ext.get_data(pgtp__cfmx
                )
            zmxzj__pnahs = ahay__ggzue[ind]
            iega__iqede = ahay__ggzue[ind + 1]
            for hoz__ukod in range(zmxzj__pnahs, iega__iqede):
                nal__hkgtq[lwu__avh[hoz__ukod]] = lygi__ljjv[hoz__ukod]
            return nal__hkgtq
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
