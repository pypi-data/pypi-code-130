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
    hnln__edkm = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(hnln__edkm)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        czp__nykzs = _get_map_arr_data_type(fe_type)
        yoe__kkm = [('data', czp__nykzs)]
        models.StructModel.__init__(self, dmm, fe_type, yoe__kkm)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    xpcv__uvffc = all(isinstance(bmb__lotr, types.Array) and bmb__lotr.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for bmb__lotr in (typ.key_arr_type, typ.
        value_arr_type))
    if xpcv__uvffc:
        qmw__duf = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        bzr__txk = cgutils.get_or_insert_function(c.builder.module,
            qmw__duf, name='count_total_elems_list_array')
        rbnhk__gydjc = cgutils.pack_array(c.builder, [n_maps, c.builder.
            call(bzr__txk, [val])])
    else:
        rbnhk__gydjc = get_array_elem_counts(c, c.builder, c.context, val, typ)
    czp__nykzs = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, czp__nykzs,
        rbnhk__gydjc, c)
    muvxf__vxmxf = _get_array_item_arr_payload(c.context, c.builder,
        czp__nykzs, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, muvxf__vxmxf.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, muvxf__vxmxf.offsets).data
    rhong__ilzuu = _get_struct_arr_payload(c.context, c.builder, czp__nykzs
        .dtype, muvxf__vxmxf.data)
    key_arr = c.builder.extract_value(rhong__ilzuu.data, 0)
    value_arr = c.builder.extract_value(rhong__ilzuu.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    dwo__smbmb, xex__ybysc = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [rhong__ilzuu.null_bitmap])
    if xpcv__uvffc:
        cbctp__rjtx = c.context.make_array(czp__nykzs.dtype.data[0])(c.
            context, c.builder, key_arr).data
        odsb__wzm = c.context.make_array(czp__nykzs.dtype.data[1])(c.
            context, c.builder, value_arr).data
        qmw__duf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        mdzr__kjza = cgutils.get_or_insert_function(c.builder.module,
            qmw__duf, name='map_array_from_sequence')
        ktaq__obji = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        xzlwn__jzti = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        c.builder.call(mdzr__kjza, [val, c.builder.bitcast(cbctp__rjtx, lir
            .IntType(8).as_pointer()), c.builder.bitcast(odsb__wzm, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), ktaq__obji), lir.Constant(lir.IntType
            (32), xzlwn__jzti)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    buvpw__bzn = c.context.make_helper(c.builder, typ)
    buvpw__bzn.data = data_arr
    jes__yocqn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(buvpw__bzn._getvalue(), is_error=jes__yocqn)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    flk__cohm = context.insert_const_string(builder.module, 'pandas')
    hym__oft = c.pyapi.import_module_noblock(flk__cohm)
    bmcz__ofgfs = c.pyapi.object_getattr_string(hym__oft, 'NA')
    qdyob__xdwok = c.context.get_constant(offset_type, 0)
    builder.store(qdyob__xdwok, offsets_ptr)
    hqdvf__bkod = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as mnukm__kboq:
        qkuv__ahb = mnukm__kboq.index
        item_ind = builder.load(hqdvf__bkod)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [qkuv__ahb]))
        dowtb__vart = seq_getitem(builder, context, val, qkuv__ahb)
        set_bitmap_bit(builder, null_bitmap_ptr, qkuv__ahb, 0)
        qpkz__zbrl = is_na_value(builder, context, dowtb__vart, bmcz__ofgfs)
        ohn__cht = builder.icmp_unsigned('!=', qpkz__zbrl, lir.Constant(
            qpkz__zbrl.type, 1))
        with builder.if_then(ohn__cht):
            set_bitmap_bit(builder, null_bitmap_ptr, qkuv__ahb, 1)
            avcx__caoiy = dict_keys(builder, context, dowtb__vart)
            arrm__syxpp = dict_values(builder, context, dowtb__vart)
            n_items = bodo.utils.utils.object_length(c, avcx__caoiy)
            _unbox_array_item_array_copy_data(typ.key_arr_type, avcx__caoiy,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                arrm__syxpp, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), hqdvf__bkod)
            c.pyapi.decref(avcx__caoiy)
            c.pyapi.decref(arrm__syxpp)
        c.pyapi.decref(dowtb__vart)
    builder.store(builder.trunc(builder.load(hqdvf__bkod), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(hym__oft)
    c.pyapi.decref(bmcz__ofgfs)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    buvpw__bzn = c.context.make_helper(c.builder, typ, val)
    data_arr = buvpw__bzn.data
    czp__nykzs = _get_map_arr_data_type(typ)
    muvxf__vxmxf = _get_array_item_arr_payload(c.context, c.builder,
        czp__nykzs, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, muvxf__vxmxf.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, muvxf__vxmxf.offsets).data
    rhong__ilzuu = _get_struct_arr_payload(c.context, c.builder, czp__nykzs
        .dtype, muvxf__vxmxf.data)
    key_arr = c.builder.extract_value(rhong__ilzuu.data, 0)
    value_arr = c.builder.extract_value(rhong__ilzuu.data, 1)
    if all(isinstance(bmb__lotr, types.Array) and bmb__lotr.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        bmb__lotr in (typ.key_arr_type, typ.value_arr_type)):
        cbctp__rjtx = c.context.make_array(czp__nykzs.dtype.data[0])(c.
            context, c.builder, key_arr).data
        odsb__wzm = c.context.make_array(czp__nykzs.dtype.data[1])(c.
            context, c.builder, value_arr).data
        qmw__duf = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        wxst__wcq = cgutils.get_or_insert_function(c.builder.module,
            qmw__duf, name='np_array_from_map_array')
        ktaq__obji = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        xzlwn__jzti = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        arr = c.builder.call(wxst__wcq, [muvxf__vxmxf.n_arrays, c.builder.
            bitcast(cbctp__rjtx, lir.IntType(8).as_pointer()), c.builder.
            bitcast(odsb__wzm, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), ktaq__obji), lir
            .Constant(lir.IntType(32), xzlwn__jzti)])
    else:
        arr = _box_map_array_generic(typ, c, muvxf__vxmxf.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    flk__cohm = context.insert_const_string(builder.module, 'numpy')
    cxr__dpoy = c.pyapi.import_module_noblock(flk__cohm)
    rtdhu__ygq = c.pyapi.object_getattr_string(cxr__dpoy, 'object_')
    vee__wtet = c.pyapi.long_from_longlong(n_maps)
    rmpep__ght = c.pyapi.call_method(cxr__dpoy, 'ndarray', (vee__wtet,
        rtdhu__ygq))
    qxivg__nholm = c.pyapi.object_getattr_string(cxr__dpoy, 'nan')
    wkncw__tdj = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    hqdvf__bkod = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as mnukm__kboq:
        sqx__iaos = mnukm__kboq.index
        pyarray_setitem(builder, context, rmpep__ght, sqx__iaos, qxivg__nholm)
        ulva__qrh = get_bitmap_bit(builder, null_bitmap_ptr, sqx__iaos)
        xmt__dbt = builder.icmp_unsigned('!=', ulva__qrh, lir.Constant(lir.
            IntType(8), 0))
        with builder.if_then(xmt__dbt):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(sqx__iaos, lir.Constant(sqx__iaos
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                sqx__iaos]))), lir.IntType(64))
            item_ind = builder.load(hqdvf__bkod)
            dowtb__vart = c.pyapi.dict_new()
            knwf__ttb = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            dwo__smbmb, dtw__wewuv = c.pyapi.call_jit_code(knwf__ttb, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            dwo__smbmb, ace__xtd = c.pyapi.call_jit_code(knwf__ttb, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            ohvox__joa = c.pyapi.from_native_value(typ.key_arr_type,
                dtw__wewuv, c.env_manager)
            sfz__hezfp = c.pyapi.from_native_value(typ.value_arr_type,
                ace__xtd, c.env_manager)
            ren__cfi = c.pyapi.call_function_objargs(wkncw__tdj, (
                ohvox__joa, sfz__hezfp))
            dict_merge_from_seq2(builder, context, dowtb__vart, ren__cfi)
            builder.store(builder.add(item_ind, n_items), hqdvf__bkod)
            pyarray_setitem(builder, context, rmpep__ght, sqx__iaos,
                dowtb__vart)
            c.pyapi.decref(ren__cfi)
            c.pyapi.decref(ohvox__joa)
            c.pyapi.decref(sfz__hezfp)
            c.pyapi.decref(dowtb__vart)
    c.pyapi.decref(wkncw__tdj)
    c.pyapi.decref(cxr__dpoy)
    c.pyapi.decref(rtdhu__ygq)
    c.pyapi.decref(vee__wtet)
    c.pyapi.decref(qxivg__nholm)
    return rmpep__ght


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    buvpw__bzn = context.make_helper(builder, sig.return_type)
    buvpw__bzn.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return buvpw__bzn._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    xkpjm__mtmf = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return xkpjm__mtmf(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    tbu__kzci = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(tbu__kzci)


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
    abzd__cemw = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            fluqb__lyd = val.keys()
            sunnq__lsez = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), abzd__cemw, ('key', 'value'))
            for laty__xdh, pnbjb__japcx in enumerate(fluqb__lyd):
                sunnq__lsez[laty__xdh] = bodo.libs.struct_arr_ext.init_struct((
                    pnbjb__japcx, val[pnbjb__japcx]), ('key', 'value'))
            arr._data[ind] = sunnq__lsez
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
            vpf__ksof = dict()
            eavdi__rikv = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            sunnq__lsez = bodo.libs.array_item_arr_ext.get_data(arr._data)
            ave__qpn, eet__ythgz = bodo.libs.struct_arr_ext.get_data(
                sunnq__lsez)
            hnr__uhkwn = eavdi__rikv[ind]
            xodh__jmqy = eavdi__rikv[ind + 1]
            for laty__xdh in range(hnr__uhkwn, xodh__jmqy):
                vpf__ksof[ave__qpn[laty__xdh]] = eet__ythgz[laty__xdh]
            return vpf__ksof
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
