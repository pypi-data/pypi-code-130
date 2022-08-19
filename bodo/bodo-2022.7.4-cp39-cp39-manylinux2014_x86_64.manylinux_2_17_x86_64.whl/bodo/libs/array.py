"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
from collections import defaultdict
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.hiframes.time_ext import TimeArrayType, TimeType
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_overload_none, is_str_arr_type, raise_bodo_error, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('dict_str_array_to_info', array_ext.dict_str_array_to_info)
ll.add_symbol('get_nested_info', array_ext.get_nested_info)
ll.add_symbol('get_has_global_dictionary', array_ext.get_has_global_dictionary)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('time_array_to_info', array_ext.time_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('decref_table_array', array_ext.decref_table_array)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)
ll.add_symbol('array_info_getdata1', array_ext.array_info_getdata1)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args, incref=True):
    in_arr, = args
    arr_type = sig.args[0]
    if incref:
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, TupleArrayType):
        fxnyn__oxeqw = context.make_helper(builder, arr_type, in_arr)
        in_arr = fxnyn__oxeqw.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        uxa__tsw = context.make_helper(builder, arr_type, in_arr)
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='list_string_array_to_info')
        return builder.call(gudhw__ryn, [uxa__tsw.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                yyvi__dqux = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for skysa__wnhkt in arr_typ.data:
                    yyvi__dqux += get_types(skysa__wnhkt)
                return yyvi__dqux
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            sgg__rknz = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                xpepg__axgmb = context.make_helper(builder, arr_typ, value=arr)
                wmlwi__avtpg = get_lengths(_get_map_arr_data_type(arr_typ),
                    xpepg__axgmb.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                psoq__nzf = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                wmlwi__avtpg = get_lengths(arr_typ.dtype, psoq__nzf.data)
                wmlwi__avtpg = cgutils.pack_array(builder, [psoq__nzf.
                    n_arrays] + [builder.extract_value(wmlwi__avtpg,
                    vdgf__apesu) for vdgf__apesu in range(wmlwi__avtpg.type
                    .count)])
            elif isinstance(arr_typ, StructArrayType):
                psoq__nzf = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                wmlwi__avtpg = []
                for vdgf__apesu, skysa__wnhkt in enumerate(arr_typ.data):
                    dar__hrjzo = get_lengths(skysa__wnhkt, builder.
                        extract_value(psoq__nzf.data, vdgf__apesu))
                    wmlwi__avtpg += [builder.extract_value(dar__hrjzo,
                        dnhri__pyr) for dnhri__pyr in range(dar__hrjzo.type
                        .count)]
                wmlwi__avtpg = cgutils.pack_array(builder, [sgg__rknz,
                    context.get_constant(types.int64, -1)] + wmlwi__avtpg)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                wmlwi__avtpg = cgutils.pack_array(builder, [sgg__rknz])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return wmlwi__avtpg

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                xpepg__axgmb = context.make_helper(builder, arr_typ, value=arr)
                wck__hhgvn = get_buffers(_get_map_arr_data_type(arr_typ),
                    xpepg__axgmb.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                psoq__nzf = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                zxgrj__nncdl = get_buffers(arr_typ.dtype, psoq__nzf.data)
                kryog__otg = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, psoq__nzf.offsets)
                xdky__gjf = builder.bitcast(kryog__otg.data, lir.IntType(8)
                    .as_pointer())
                veu__qjrj = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, psoq__nzf.null_bitmap)
                cdcqt__adz = builder.bitcast(veu__qjrj.data, lir.IntType(8)
                    .as_pointer())
                wck__hhgvn = cgutils.pack_array(builder, [xdky__gjf,
                    cdcqt__adz] + [builder.extract_value(zxgrj__nncdl,
                    vdgf__apesu) for vdgf__apesu in range(zxgrj__nncdl.type
                    .count)])
            elif isinstance(arr_typ, StructArrayType):
                psoq__nzf = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                zxgrj__nncdl = []
                for vdgf__apesu, skysa__wnhkt in enumerate(arr_typ.data):
                    qkxt__xrnhz = get_buffers(skysa__wnhkt, builder.
                        extract_value(psoq__nzf.data, vdgf__apesu))
                    zxgrj__nncdl += [builder.extract_value(qkxt__xrnhz,
                        dnhri__pyr) for dnhri__pyr in range(qkxt__xrnhz.
                        type.count)]
                veu__qjrj = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, psoq__nzf.null_bitmap)
                cdcqt__adz = builder.bitcast(veu__qjrj.data, lir.IntType(8)
                    .as_pointer())
                wck__hhgvn = cgutils.pack_array(builder, [cdcqt__adz] +
                    zxgrj__nncdl)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                eadix__efb = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    eadix__efb = int128_type
                elif arr_typ == datetime_date_array_type:
                    eadix__efb = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                pkfv__bufxd = context.make_array(types.Array(eadix__efb, 1,
                    'C'))(context, builder, arr.data)
                veu__qjrj = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                jbr__bvao = builder.bitcast(pkfv__bufxd.data, lir.IntType(8
                    ).as_pointer())
                cdcqt__adz = builder.bitcast(veu__qjrj.data, lir.IntType(8)
                    .as_pointer())
                wck__hhgvn = cgutils.pack_array(builder, [cdcqt__adz,
                    jbr__bvao])
            elif arr_typ in (string_array_type, binary_array_type):
                psoq__nzf = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                ejffe__jykc = context.make_helper(builder, offset_arr_type,
                    psoq__nzf.offsets).data
                zwv__ddpr = context.make_helper(builder, char_arr_type,
                    psoq__nzf.data).data
                ialt__ipbr = context.make_helper(builder,
                    null_bitmap_arr_type, psoq__nzf.null_bitmap).data
                wck__hhgvn = cgutils.pack_array(builder, [builder.bitcast(
                    ejffe__jykc, lir.IntType(8).as_pointer()), builder.
                    bitcast(ialt__ipbr, lir.IntType(8).as_pointer()),
                    builder.bitcast(zwv__ddpr, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                jbr__bvao = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                bap__cyzi = lir.Constant(lir.IntType(8).as_pointer(), None)
                wck__hhgvn = cgutils.pack_array(builder, [bap__cyzi, jbr__bvao]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return wck__hhgvn

        def get_field_names(arr_typ):
            jxf__osvz = []
            if isinstance(arr_typ, StructArrayType):
                for bvhmt__cgye, uet__yzn in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    jxf__osvz.append(bvhmt__cgye)
                    jxf__osvz += get_field_names(uet__yzn)
            elif isinstance(arr_typ, ArrayItemArrayType):
                jxf__osvz += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                jxf__osvz += get_field_names(_get_map_arr_data_type(arr_typ))
            return jxf__osvz
        yyvi__dqux = get_types(arr_type)
        egx__ndiz = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in yyvi__dqux])
        czlni__fis = cgutils.alloca_once_value(builder, egx__ndiz)
        wmlwi__avtpg = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, wmlwi__avtpg)
        wck__hhgvn = get_buffers(arr_type, in_arr)
        hjbt__bei = cgutils.alloca_once_value(builder, wck__hhgvn)
        jxf__osvz = get_field_names(arr_type)
        if len(jxf__osvz) == 0:
            jxf__osvz = ['irrelevant']
        ghhoo__ziv = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in jxf__osvz])
        hvvod__edho = cgutils.alloca_once_value(builder, ghhoo__ziv)
        if isinstance(arr_type, MapArrayType):
            qpoxr__iwcxz = _get_map_arr_data_type(arr_type)
            szcmz__rcvx = context.make_helper(builder, arr_type, value=in_arr)
            psgk__bhb = szcmz__rcvx.data
        else:
            qpoxr__iwcxz = arr_type
            psgk__bhb = in_arr
        yifp__fmv = context.make_helper(builder, qpoxr__iwcxz, psgk__bhb)
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='nested_array_to_info')
        jofsq__cjnf = builder.call(gudhw__ryn, [builder.bitcast(czlni__fis,
            lir.IntType(32).as_pointer()), builder.bitcast(hjbt__bei, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            hvvod__edho, lir.IntType(8).as_pointer()), yifp__fmv.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    if arr_type in (string_array_type, binary_array_type):
        lymq__wqx = context.make_helper(builder, arr_type, in_arr)
        zzfl__dwo = ArrayItemArrayType(char_arr_type)
        uxa__tsw = context.make_helper(builder, zzfl__dwo, lymq__wqx.data)
        psoq__nzf = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        ejffe__jykc = context.make_helper(builder, offset_arr_type,
            psoq__nzf.offsets).data
        zwv__ddpr = context.make_helper(builder, char_arr_type, psoq__nzf.data
            ).data
        ialt__ipbr = context.make_helper(builder, null_bitmap_arr_type,
            psoq__nzf.null_bitmap).data
        ryfd__qjef = builder.zext(builder.load(builder.gep(ejffe__jykc, [
            psoq__nzf.n_arrays])), lir.IntType(64))
        sea__ythtr = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='string_array_to_info')
        return builder.call(gudhw__ryn, [psoq__nzf.n_arrays, ryfd__qjef,
            zwv__ddpr, ejffe__jykc, ialt__ipbr, uxa__tsw.meminfo, sea__ythtr])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        pmgkz__yyqq = arr.data
        mzm__bxgkt = arr.indices
        sig = array_info_type(arr_type.data)
        fyyke__sjgrp = array_to_info_codegen(context, builder, sig, (
            pmgkz__yyqq,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        ogwv__ibv = array_to_info_codegen(context, builder, sig, (
            mzm__bxgkt,), False)
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(32)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='dict_str_array_to_info')
        ilfz__gfx = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(gudhw__ryn, [fyyke__sjgrp, ogwv__ibv, ilfz__gfx])
    rpp__ygk = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        ltn__cqsl = context.compile_internal(builder, lambda a: len(a.dtype
            .categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        lorkg__rnc = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(lorkg__rnc, 1, 'C')
        rpp__ygk = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if rpp__ygk:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        sgg__rknz = builder.extract_value(arr.shape, 0)
        nifu__lipf = arr_type.dtype
        ksgxt__hzmn = numba_to_c_type(nifu__lipf)
        okjus__ocaq = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ksgxt__hzmn))
        if rpp__ygk:
            kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            gudhw__ryn = cgutils.get_or_insert_function(builder.module,
                kzrh__xaapj, name='categorical_array_to_info')
            return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                okjus__ocaq), ltn__cqsl, arr.meminfo])
        else:
            kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            gudhw__ryn = cgutils.get_or_insert_function(builder.module,
                kzrh__xaapj, name='numpy_array_to_info')
            return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                okjus__ocaq), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType, TimeArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        nifu__lipf = arr_type.dtype
        eadix__efb = nifu__lipf
        if isinstance(arr_type, DecimalArrayType):
            eadix__efb = int128_type
        if arr_type == datetime_date_array_type:
            eadix__efb = types.int64
        pkfv__bufxd = context.make_array(types.Array(eadix__efb, 1, 'C'))(
            context, builder, arr.data)
        sgg__rknz = builder.extract_value(pkfv__bufxd.shape, 0)
        fubel__dlld = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        ksgxt__hzmn = numba_to_c_type(nifu__lipf)
        okjus__ocaq = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ksgxt__hzmn))
        if isinstance(arr_type, DecimalArrayType):
            kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            gudhw__ryn = cgutils.get_or_insert_function(builder.module,
                kzrh__xaapj, name='decimal_array_to_info')
            return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(
                pkfv__bufxd.data, lir.IntType(8).as_pointer()), builder.
                load(okjus__ocaq), builder.bitcast(fubel__dlld.data, lir.
                IntType(8).as_pointer()), pkfv__bufxd.meminfo, fubel__dlld.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        elif isinstance(arr_type, TimeArrayType):
            kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32)])
            gudhw__ryn = cgutils.get_or_insert_function(builder.module,
                kzrh__xaapj, name='time_array_to_info')
            return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(
                pkfv__bufxd.data, lir.IntType(8).as_pointer()), builder.
                load(okjus__ocaq), builder.bitcast(fubel__dlld.data, lir.
                IntType(8).as_pointer()), pkfv__bufxd.meminfo, fubel__dlld.
                meminfo, lir.Constant(lir.IntType(32), arr_type.precision)])
        else:
            kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            gudhw__ryn = cgutils.get_or_insert_function(builder.module,
                kzrh__xaapj, name='nullable_array_to_info')
            return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(
                pkfv__bufxd.data, lir.IntType(8).as_pointer()), builder.
                load(okjus__ocaq), builder.bitcast(fubel__dlld.data, lir.
                IntType(8).as_pointer()), pkfv__bufxd.meminfo, fubel__dlld.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        zqzyl__vziu = context.make_array(arr_type.arr_type)(context,
            builder, arr.left)
        hjrv__rxg = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        sgg__rknz = builder.extract_value(zqzyl__vziu.shape, 0)
        ksgxt__hzmn = numba_to_c_type(arr_type.arr_type.dtype)
        okjus__ocaq = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ksgxt__hzmn))
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='interval_array_to_info')
        return builder.call(gudhw__ryn, [sgg__rknz, builder.bitcast(
            zqzyl__vziu.data, lir.IntType(8).as_pointer()), builder.bitcast
            (hjrv__rxg.data, lir.IntType(8).as_pointer()), builder.load(
            okjus__ocaq), zqzyl__vziu.meminfo, hjrv__rxg.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    ofck__rbs = cgutils.alloca_once(builder, lir.IntType(64))
    jbr__bvao = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    uxxo__koymm = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    gudhw__ryn = cgutils.get_or_insert_function(builder.module, kzrh__xaapj,
        name='info_to_numpy_array')
    builder.call(gudhw__ryn, [in_info, ofck__rbs, jbr__bvao, uxxo__koymm])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    dhsn__yex = context.get_value_type(types.intp)
    atwn__gta = cgutils.pack_array(builder, [builder.load(ofck__rbs)], ty=
        dhsn__yex)
    qlx__aarpi = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    jflvg__gbwm = cgutils.pack_array(builder, [qlx__aarpi], ty=dhsn__yex)
    zwv__ddpr = builder.bitcast(builder.load(jbr__bvao), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=zwv__ddpr, shape=atwn__gta,
        strides=jflvg__gbwm, itemsize=qlx__aarpi, meminfo=builder.load(
        uxxo__koymm))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    kdcf__yvlvh = context.make_helper(builder, arr_type)
    kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    gudhw__ryn = cgutils.get_or_insert_function(builder.module, kzrh__xaapj,
        name='info_to_list_string_array')
    builder.call(gudhw__ryn, [in_info, kdcf__yvlvh._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return kdcf__yvlvh._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    mgia__xfxr = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        hjjm__olqel = lengths_pos
        himc__jaw = infos_pos
        lqos__zvbm, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        qhw__rong = ArrayItemArrayPayloadType(arr_typ)
        qhbu__djuw = context.get_data_type(qhw__rong)
        vclo__ilzz = context.get_abi_sizeof(qhbu__djuw)
        tjy__gzq = define_array_item_dtor(context, builder, arr_typ, qhw__rong)
        lbip__yfk = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, vclo__ilzz), tjy__gzq)
        gmy__lmzru = context.nrt.meminfo_data(builder, lbip__yfk)
        jegc__ifhw = builder.bitcast(gmy__lmzru, qhbu__djuw.as_pointer())
        psoq__nzf = cgutils.create_struct_proxy(qhw__rong)(context, builder)
        psoq__nzf.n_arrays = builder.extract_value(builder.load(lengths_ptr
            ), hjjm__olqel)
        psoq__nzf.data = lqos__zvbm
        fds__gykzu = builder.load(array_infos_ptr)
        rpcpp__pze = builder.bitcast(builder.extract_value(fds__gykzu,
            himc__jaw), mgia__xfxr)
        psoq__nzf.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, rpcpp__pze)
        wkzvp__fvizd = builder.bitcast(builder.extract_value(fds__gykzu, 
            himc__jaw + 1), mgia__xfxr)
        psoq__nzf.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, wkzvp__fvizd)
        builder.store(psoq__nzf._getvalue(), jegc__ifhw)
        uxa__tsw = context.make_helper(builder, arr_typ)
        uxa__tsw.meminfo = lbip__yfk
        return uxa__tsw._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        qkyq__kaf = []
        himc__jaw = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for xkqj__ugas in arr_typ.data:
            lqos__zvbm, lengths_pos, infos_pos = nested_to_array(context,
                builder, xkqj__ugas, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            qkyq__kaf.append(lqos__zvbm)
        qhw__rong = StructArrayPayloadType(arr_typ.data)
        qhbu__djuw = context.get_value_type(qhw__rong)
        vclo__ilzz = context.get_abi_sizeof(qhbu__djuw)
        tjy__gzq = define_struct_arr_dtor(context, builder, arr_typ, qhw__rong)
        lbip__yfk = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, vclo__ilzz), tjy__gzq)
        gmy__lmzru = context.nrt.meminfo_data(builder, lbip__yfk)
        jegc__ifhw = builder.bitcast(gmy__lmzru, qhbu__djuw.as_pointer())
        psoq__nzf = cgutils.create_struct_proxy(qhw__rong)(context, builder)
        psoq__nzf.data = cgutils.pack_array(builder, qkyq__kaf
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, qkyq__kaf)
        fds__gykzu = builder.load(array_infos_ptr)
        wkzvp__fvizd = builder.bitcast(builder.extract_value(fds__gykzu,
            himc__jaw), mgia__xfxr)
        psoq__nzf.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, wkzvp__fvizd)
        builder.store(psoq__nzf._getvalue(), jegc__ifhw)
        btb__zlog = context.make_helper(builder, arr_typ)
        btb__zlog.meminfo = lbip__yfk
        return btb__zlog._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        fds__gykzu = builder.load(array_infos_ptr)
        bdf__rzpn = builder.bitcast(builder.extract_value(fds__gykzu,
            infos_pos), mgia__xfxr)
        lymq__wqx = context.make_helper(builder, arr_typ)
        zzfl__dwo = ArrayItemArrayType(char_arr_type)
        uxa__tsw = context.make_helper(builder, zzfl__dwo)
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_to_string_array')
        builder.call(gudhw__ryn, [bdf__rzpn, uxa__tsw._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        lymq__wqx.data = uxa__tsw._getvalue()
        return lymq__wqx._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        fds__gykzu = builder.load(array_infos_ptr)
        jke__qftw = builder.bitcast(builder.extract_value(fds__gykzu, 
            infos_pos + 1), mgia__xfxr)
        return _lower_info_to_array_numpy(arr_typ, context, builder, jke__qftw
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        eadix__efb = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            eadix__efb = int128_type
        elif arr_typ == datetime_date_array_type:
            eadix__efb = types.int64
        fds__gykzu = builder.load(array_infos_ptr)
        wkzvp__fvizd = builder.bitcast(builder.extract_value(fds__gykzu,
            infos_pos), mgia__xfxr)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, wkzvp__fvizd)
        jke__qftw = builder.bitcast(builder.extract_value(fds__gykzu, 
            infos_pos + 1), mgia__xfxr)
        arr.data = _lower_info_to_array_numpy(types.Array(eadix__efb, 1,
            'C'), context, builder, jke__qftw)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, zyud__ckp = args
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        return _lower_info_to_array_list_string_array(arr_type, context,
            builder, in_info)
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
        StructArrayType, TupleArrayType)):

        def get_num_arrays(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 1 + get_num_arrays(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_arrays(xkqj__ugas) for xkqj__ugas in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(xkqj__ugas) for xkqj__ugas in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            lky__mzuew = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            lky__mzuew = _get_map_arr_data_type(arr_type)
        else:
            lky__mzuew = arr_type
        xud__ulgq = get_num_arrays(lky__mzuew)
        wmlwi__avtpg = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), 0) for zyud__ckp in range(xud__ulgq)])
        lengths_ptr = cgutils.alloca_once_value(builder, wmlwi__avtpg)
        bap__cyzi = lir.Constant(lir.IntType(8).as_pointer(), None)
        orvcz__ckkj = cgutils.pack_array(builder, [bap__cyzi for zyud__ckp in
            range(get_num_infos(lky__mzuew))])
        array_infos_ptr = cgutils.alloca_once_value(builder, orvcz__ckkj)
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_to_nested_array')
        builder.call(gudhw__ryn, [in_info, builder.bitcast(lengths_ptr, lir
            .IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, zyud__ckp, zyud__ckp = nested_to_array(context, builder,
            lky__mzuew, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            fxnyn__oxeqw = context.make_helper(builder, arr_type)
            fxnyn__oxeqw.data = arr
            context.nrt.incref(builder, lky__mzuew, arr)
            arr = fxnyn__oxeqw._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, lky__mzuew)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        lymq__wqx = context.make_helper(builder, arr_type)
        zzfl__dwo = ArrayItemArrayType(char_arr_type)
        uxa__tsw = context.make_helper(builder, zzfl__dwo)
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_to_string_array')
        builder.call(gudhw__ryn, [in_info, uxa__tsw._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        lymq__wqx.data = uxa__tsw._getvalue()
        return lymq__wqx._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='get_nested_info')
        fyyke__sjgrp = builder.call(gudhw__ryn, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        ogwv__ibv = builder.call(gudhw__ryn, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        vako__uwy = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        vako__uwy.data = info_to_array_codegen(context, builder, sig, (
            fyyke__sjgrp, context.get_constant_null(arr_type.data)))
        yiizt__csd = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = yiizt__csd(array_info_type, yiizt__csd)
        vako__uwy.indices = info_to_array_codegen(context, builder, sig, (
            ogwv__ibv, context.get_constant_null(yiizt__csd)))
        kzrh__xaapj = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='get_has_global_dictionary')
        ilfz__gfx = builder.call(gudhw__ryn, [in_info])
        vako__uwy.has_global_dictionary = builder.trunc(ilfz__gfx, cgutils.
            bool_t)
        return vako__uwy._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        lorkg__rnc = get_categories_int_type(arr_type.dtype)
        hsf__xryuo = types.Array(lorkg__rnc, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(hsf__xryuo, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            vft__lptcr = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(vft__lptcr))
            int_type = arr_type.dtype.int_type
            nfb__vbla = arr_type.dtype.data.data
            gabgd__mvkwx = context.get_constant_generic(builder, nfb__vbla,
                vft__lptcr)
            nifu__lipf = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(nfb__vbla), [gabgd__mvkwx])
        else:
            nifu__lipf = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, nifu__lipf)
        out_arr.dtype = nifu__lipf
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zwv__ddpr = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = zwv__ddpr
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType, TimeArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        eadix__efb = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            eadix__efb = int128_type
        elif arr_type == datetime_date_array_type:
            eadix__efb = types.int64
        myoq__bckhv = types.Array(eadix__efb, 1, 'C')
        pkfv__bufxd = context.make_array(myoq__bckhv)(context, builder)
        pto__hgi = types.Array(types.uint8, 1, 'C')
        ulbv__rflws = context.make_array(pto__hgi)(context, builder)
        ofck__rbs = cgutils.alloca_once(builder, lir.IntType(64))
        qtmh__miu = cgutils.alloca_once(builder, lir.IntType(64))
        jbr__bvao = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        asd__fxrxy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        uxxo__koymm = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        oegoh__rlx = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_to_nullable_array')
        builder.call(gudhw__ryn, [in_info, ofck__rbs, qtmh__miu, jbr__bvao,
            asd__fxrxy, uxxo__koymm, oegoh__rlx])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dhsn__yex = context.get_value_type(types.intp)
        atwn__gta = cgutils.pack_array(builder, [builder.load(ofck__rbs)],
            ty=dhsn__yex)
        qlx__aarpi = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(eadix__efb)))
        jflvg__gbwm = cgutils.pack_array(builder, [qlx__aarpi], ty=dhsn__yex)
        zwv__ddpr = builder.bitcast(builder.load(jbr__bvao), context.
            get_data_type(eadix__efb).as_pointer())
        numba.np.arrayobj.populate_array(pkfv__bufxd, data=zwv__ddpr, shape
            =atwn__gta, strides=jflvg__gbwm, itemsize=qlx__aarpi, meminfo=
            builder.load(uxxo__koymm))
        arr.data = pkfv__bufxd._getvalue()
        atwn__gta = cgutils.pack_array(builder, [builder.load(qtmh__miu)],
            ty=dhsn__yex)
        qlx__aarpi = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        jflvg__gbwm = cgutils.pack_array(builder, [qlx__aarpi], ty=dhsn__yex)
        zwv__ddpr = builder.bitcast(builder.load(asd__fxrxy), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(ulbv__rflws, data=zwv__ddpr, shape
            =atwn__gta, strides=jflvg__gbwm, itemsize=qlx__aarpi, meminfo=
            builder.load(oegoh__rlx))
        arr.null_bitmap = ulbv__rflws._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zqzyl__vziu = context.make_array(arr_type.arr_type)(context, builder)
        hjrv__rxg = context.make_array(arr_type.arr_type)(context, builder)
        ofck__rbs = cgutils.alloca_once(builder, lir.IntType(64))
        avw__hha = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        cyibe__ciyo = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        jgp__pkjw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tsbp__jnj = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_to_interval_array')
        builder.call(gudhw__ryn, [in_info, ofck__rbs, avw__hha, cyibe__ciyo,
            jgp__pkjw, tsbp__jnj])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dhsn__yex = context.get_value_type(types.intp)
        atwn__gta = cgutils.pack_array(builder, [builder.load(ofck__rbs)],
            ty=dhsn__yex)
        qlx__aarpi = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        jflvg__gbwm = cgutils.pack_array(builder, [qlx__aarpi], ty=dhsn__yex)
        iui__cucoa = builder.bitcast(builder.load(avw__hha), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(zqzyl__vziu, data=iui__cucoa,
            shape=atwn__gta, strides=jflvg__gbwm, itemsize=qlx__aarpi,
            meminfo=builder.load(jgp__pkjw))
        arr.left = zqzyl__vziu._getvalue()
        xuvr__qcwsl = builder.bitcast(builder.load(cyibe__ciyo), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(hjrv__rxg, data=xuvr__qcwsl, shape
            =atwn__gta, strides=jflvg__gbwm, itemsize=qlx__aarpi, meminfo=
            builder.load(tsbp__jnj))
        arr.right = hjrv__rxg._getvalue()
        return arr._getvalue()
    raise_bodo_error(f'info_to_array(): array type {arr_type} is not supported'
        )


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type, 'info_to_array: expected info type'
    return arr_type(info_type, array_type), info_to_array_codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        sgg__rknz, zyud__ckp = args
        ksgxt__hzmn = numba_to_c_type(array_type.dtype)
        okjus__ocaq = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ksgxt__hzmn))
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='alloc_numpy')
        return builder.call(gudhw__ryn, [sgg__rknz, builder.load(okjus__ocaq)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        sgg__rknz, gip__qzd = args
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='alloc_string_array')
        return builder.call(gudhw__ryn, [sgg__rknz, gip__qzd])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    roly__zgv, = args
    lwem__pcpj = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], roly__zgv)
    kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    gudhw__ryn = cgutils.get_or_insert_function(builder.module, kzrh__xaapj,
        name='arr_info_list_to_table')
    return builder.call(gudhw__ryn, [lwem__pcpj.data, lwem__pcpj.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_from_table')
        return builder.call(gudhw__ryn, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    trh__kuhru = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, yfk__walm, zyud__ckp = args
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='info_from_table')
        hju__nzp = cgutils.create_struct_proxy(trh__kuhru)(context, builder)
        hju__nzp.parent = cgutils.get_null_value(hju__nzp.parent.type)
        nvh__lof = context.make_array(table_idx_arr_t)(context, builder,
            yfk__walm)
        lzb__jxtu = context.get_constant(types.int64, -1)
        sgk__zdp = context.get_constant(types.int64, 0)
        dbif__nfi = cgutils.alloca_once_value(builder, sgk__zdp)
        for t, fkkv__zmdqf in trh__kuhru.type_to_blk.items():
            cbqi__gqlet = context.get_constant(types.int64, len(trh__kuhru.
                block_to_arr_ind[fkkv__zmdqf]))
            zyud__ckp, gpxrl__yrlb = ListInstance.allocate_ex(context,
                builder, types.List(t), cbqi__gqlet)
            gpxrl__yrlb.size = cbqi__gqlet
            cevh__leoqb = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(trh__kuhru.block_to_arr_ind[
                fkkv__zmdqf], dtype=np.int64))
            ruckg__xuj = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, cevh__leoqb)
            with cgutils.for_range(builder, cbqi__gqlet) as jyi__meec:
                vdgf__apesu = jyi__meec.index
                ipe__drirz = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ruckg__xuj, vdgf__apesu)
                aawkk__elqe = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, nvh__lof, ipe__drirz)
                moq__hwyz = builder.icmp_unsigned('!=', aawkk__elqe, lzb__jxtu)
                with builder.if_else(moq__hwyz) as (jjbn__amhjs, qfrk__bhx):
                    with jjbn__amhjs:
                        hwmga__yjg = builder.call(gudhw__ryn, [cpp_table,
                            aawkk__elqe])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            hwmga__yjg])
                        gpxrl__yrlb.inititem(vdgf__apesu, arr, incref=False)
                        sgg__rknz = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(sgg__rknz, dbif__nfi)
                    with qfrk__bhx:
                        bqnrn__bhqoz = context.get_constant_null(t)
                        gpxrl__yrlb.inititem(vdgf__apesu, bqnrn__bhqoz,
                            incref=False)
            setattr(hju__nzp, f'block_{fkkv__zmdqf}', gpxrl__yrlb.value)
        hju__nzp.len = builder.load(dbif__nfi)
        return hju__nzp._getvalue()
    return trh__kuhru(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    nvyq__fell = out_col_inds_t.instance_type.meta
    trh__kuhru = unwrap_typeref(out_types_t.types[0])
    mxmqa__hpf = [unwrap_typeref(out_types_t.types[vdgf__apesu]) for
        vdgf__apesu in range(1, len(out_types_t.types))]
    icdfl__uhuw = {}
    opu__elxq = get_overload_const_int(n_table_cols_t)
    ccwcb__gbikt = {hymjz__uqbzo: vdgf__apesu for vdgf__apesu, hymjz__uqbzo in
        enumerate(nvyq__fell)}
    if not is_overload_none(unknown_cat_arrs_t):
        hnaf__llbdh = {ezyq__ppmzw: vdgf__apesu for vdgf__apesu,
            ezyq__ppmzw in enumerate(cat_inds_t.instance_type.meta)}
    fbzv__zwivg = []
    ijif__myep = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(trh__kuhru, bodo.TableType):
        ijif__myep += f'  py_table = init_table(py_table_type, False)\n'
        ijif__myep += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for upnw__ozje, fkkv__zmdqf in trh__kuhru.type_to_blk.items():
            jtxsr__mtsjf = [ccwcb__gbikt.get(vdgf__apesu, -1) for
                vdgf__apesu in trh__kuhru.block_to_arr_ind[fkkv__zmdqf]]
            icdfl__uhuw[f'out_inds_{fkkv__zmdqf}'] = np.array(jtxsr__mtsjf,
                np.int64)
            icdfl__uhuw[f'out_type_{fkkv__zmdqf}'] = upnw__ozje
            icdfl__uhuw[f'typ_list_{fkkv__zmdqf}'] = types.List(upnw__ozje)
            dzzpu__qpih = f'out_type_{fkkv__zmdqf}'
            if type_has_unknown_cats(upnw__ozje):
                if is_overload_none(unknown_cat_arrs_t):
                    ijif__myep += f"""  in_arr_list_{fkkv__zmdqf} = get_table_block(out_types_t[0], {fkkv__zmdqf})
"""
                    dzzpu__qpih = f'in_arr_list_{fkkv__zmdqf}[i]'
                else:
                    icdfl__uhuw[f'cat_arr_inds_{fkkv__zmdqf}'] = np.array([
                        hnaf__llbdh.get(vdgf__apesu, -1) for vdgf__apesu in
                        trh__kuhru.block_to_arr_ind[fkkv__zmdqf]], np.int64)
                    dzzpu__qpih = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{fkkv__zmdqf}[i]]')
            cbqi__gqlet = len(trh__kuhru.block_to_arr_ind[fkkv__zmdqf])
            ijif__myep += f"""  arr_list_{fkkv__zmdqf} = alloc_list_like(typ_list_{fkkv__zmdqf}, {cbqi__gqlet}, False)
"""
            ijif__myep += f'  for i in range(len(arr_list_{fkkv__zmdqf})):\n'
            ijif__myep += (
                f'    cpp_ind_{fkkv__zmdqf} = out_inds_{fkkv__zmdqf}[i]\n')
            ijif__myep += f'    if cpp_ind_{fkkv__zmdqf} == -1:\n'
            ijif__myep += f'      continue\n'
            ijif__myep += f"""    arr_{fkkv__zmdqf} = info_to_array(info_from_table(cpp_table, cpp_ind_{fkkv__zmdqf}), {dzzpu__qpih})
"""
            ijif__myep += (
                f'    arr_list_{fkkv__zmdqf}[i] = arr_{fkkv__zmdqf}\n')
            ijif__myep += f"""  py_table = set_table_block(py_table, arr_list_{fkkv__zmdqf}, {fkkv__zmdqf})
"""
        fbzv__zwivg.append('py_table')
    elif trh__kuhru != types.none:
        wtjc__mmwx = ccwcb__gbikt.get(0, -1)
        if wtjc__mmwx != -1:
            icdfl__uhuw[f'arr_typ_arg0'] = trh__kuhru
            dzzpu__qpih = f'arr_typ_arg0'
            if type_has_unknown_cats(trh__kuhru):
                if is_overload_none(unknown_cat_arrs_t):
                    dzzpu__qpih = f'out_types_t[0]'
                else:
                    dzzpu__qpih = f'unknown_cat_arrs_t[{hnaf__llbdh[0]}]'
            ijif__myep += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {wtjc__mmwx}), {dzzpu__qpih})
"""
            fbzv__zwivg.append('out_arg0')
    for vdgf__apesu, t in enumerate(mxmqa__hpf):
        wtjc__mmwx = ccwcb__gbikt.get(opu__elxq + vdgf__apesu, -1)
        if wtjc__mmwx != -1:
            icdfl__uhuw[f'extra_arr_type_{vdgf__apesu}'] = t
            dzzpu__qpih = f'extra_arr_type_{vdgf__apesu}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    dzzpu__qpih = f'out_types_t[{vdgf__apesu + 1}]'
                else:
                    dzzpu__qpih = (
                        f'unknown_cat_arrs_t[{hnaf__llbdh[opu__elxq + vdgf__apesu]}]'
                        )
            ijif__myep += f"""  out_{vdgf__apesu} = info_to_array(info_from_table(cpp_table, {wtjc__mmwx}), {dzzpu__qpih})
"""
            fbzv__zwivg.append(f'out_{vdgf__apesu}')
    xhaf__ptodc = ',' if len(fbzv__zwivg) == 1 else ''
    ijif__myep += f"  return ({', '.join(fbzv__zwivg)}{xhaf__ptodc})\n"
    icdfl__uhuw.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(nvyq__fell), 'py_table_type': trh__kuhru})
    supr__ejm = {}
    exec(ijif__myep, icdfl__uhuw, supr__ejm)
    return supr__ejm['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    trh__kuhru = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, zyud__ckp = args
        vqcjv__jkmji = cgutils.create_struct_proxy(trh__kuhru)(context,
            builder, py_table)
        if trh__kuhru.has_runtime_cols:
            pkq__ntqtm = lir.Constant(lir.IntType(64), 0)
            for fkkv__zmdqf, t in enumerate(trh__kuhru.arr_types):
                epvj__jbmzx = getattr(vqcjv__jkmji, f'block_{fkkv__zmdqf}')
                nfzyh__yxzg = ListInstance(context, builder, types.List(t),
                    epvj__jbmzx)
                pkq__ntqtm = builder.add(pkq__ntqtm, nfzyh__yxzg.size)
        else:
            pkq__ntqtm = lir.Constant(lir.IntType(64), len(trh__kuhru.
                arr_types))
        zyud__ckp, jwmm__ocrq = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), pkq__ntqtm)
        jwmm__ocrq.size = pkq__ntqtm
        if trh__kuhru.has_runtime_cols:
            vog__qdqq = lir.Constant(lir.IntType(64), 0)
            for fkkv__zmdqf, t in enumerate(trh__kuhru.arr_types):
                epvj__jbmzx = getattr(vqcjv__jkmji, f'block_{fkkv__zmdqf}')
                nfzyh__yxzg = ListInstance(context, builder, types.List(t),
                    epvj__jbmzx)
                cbqi__gqlet = nfzyh__yxzg.size
                with cgutils.for_range(builder, cbqi__gqlet) as jyi__meec:
                    vdgf__apesu = jyi__meec.index
                    arr = nfzyh__yxzg.getitem(vdgf__apesu)
                    oetwv__xskk = signature(array_info_type, t)
                    ebdt__smagf = arr,
                    jzw__somiy = array_to_info_codegen(context, builder,
                        oetwv__xskk, ebdt__smagf)
                    jwmm__ocrq.inititem(builder.add(vog__qdqq, vdgf__apesu),
                        jzw__somiy, incref=False)
                vog__qdqq = builder.add(vog__qdqq, cbqi__gqlet)
        else:
            for t, fkkv__zmdqf in trh__kuhru.type_to_blk.items():
                cbqi__gqlet = context.get_constant(types.int64, len(
                    trh__kuhru.block_to_arr_ind[fkkv__zmdqf]))
                epvj__jbmzx = getattr(vqcjv__jkmji, f'block_{fkkv__zmdqf}')
                nfzyh__yxzg = ListInstance(context, builder, types.List(t),
                    epvj__jbmzx)
                cevh__leoqb = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(trh__kuhru.
                    block_to_arr_ind[fkkv__zmdqf], dtype=np.int64))
                ruckg__xuj = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, cevh__leoqb)
                with cgutils.for_range(builder, cbqi__gqlet) as jyi__meec:
                    vdgf__apesu = jyi__meec.index
                    ipe__drirz = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        ruckg__xuj, vdgf__apesu)
                    rbc__kvjd = signature(types.none, trh__kuhru, types.
                        List(t), types.int64, types.int64)
                    qdt__gvnjq = py_table, epvj__jbmzx, vdgf__apesu, ipe__drirz
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, rbc__kvjd, qdt__gvnjq)
                    arr = nfzyh__yxzg.getitem(vdgf__apesu)
                    oetwv__xskk = signature(array_info_type, t)
                    ebdt__smagf = arr,
                    jzw__somiy = array_to_info_codegen(context, builder,
                        oetwv__xskk, ebdt__smagf)
                    jwmm__ocrq.inititem(ipe__drirz, jzw__somiy, incref=False)
        jsgo__jbcyy = jwmm__ocrq.value
        fxsqr__yki = signature(table_type, types.List(array_info_type))
        uoc__bpvoo = jsgo__jbcyy,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            fxsqr__yki, uoc__bpvoo)
        context.nrt.decref(builder, types.List(array_info_type), jsgo__jbcyy)
        return cpp_table
    return table_type(trh__kuhru, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    ydh__vgg = in_col_inds_t.instance_type.meta
    icdfl__uhuw = {}
    opu__elxq = get_overload_const_int(n_table_cols_t)
    fijko__azjb = defaultdict(list)
    ccwcb__gbikt = {}
    for vdgf__apesu, hymjz__uqbzo in enumerate(ydh__vgg):
        if hymjz__uqbzo in ccwcb__gbikt:
            fijko__azjb[hymjz__uqbzo].append(vdgf__apesu)
        else:
            ccwcb__gbikt[hymjz__uqbzo] = vdgf__apesu
    ijif__myep = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    ijif__myep += (
        f'  cpp_arr_list = alloc_empty_list_type({len(ydh__vgg)}, array_info_type)\n'
        )
    if py_table != types.none:
        for fkkv__zmdqf in py_table.type_to_blk.values():
            jtxsr__mtsjf = [ccwcb__gbikt.get(vdgf__apesu, -1) for
                vdgf__apesu in py_table.block_to_arr_ind[fkkv__zmdqf]]
            icdfl__uhuw[f'out_inds_{fkkv__zmdqf}'] = np.array(jtxsr__mtsjf,
                np.int64)
            icdfl__uhuw[f'arr_inds_{fkkv__zmdqf}'] = np.array(py_table.
                block_to_arr_ind[fkkv__zmdqf], np.int64)
            ijif__myep += (
                f'  arr_list_{fkkv__zmdqf} = get_table_block(py_table, {fkkv__zmdqf})\n'
                )
            ijif__myep += f'  for i in range(len(arr_list_{fkkv__zmdqf})):\n'
            ijif__myep += (
                f'    out_arr_ind_{fkkv__zmdqf} = out_inds_{fkkv__zmdqf}[i]\n')
            ijif__myep += f'    if out_arr_ind_{fkkv__zmdqf} == -1:\n'
            ijif__myep += f'      continue\n'
            ijif__myep += (
                f'    arr_ind_{fkkv__zmdqf} = arr_inds_{fkkv__zmdqf}[i]\n')
            ijif__myep += f"""    ensure_column_unboxed(py_table, arr_list_{fkkv__zmdqf}, i, arr_ind_{fkkv__zmdqf})
"""
            ijif__myep += f"""    cpp_arr_list[out_arr_ind_{fkkv__zmdqf}] = array_to_info(arr_list_{fkkv__zmdqf}[i])
"""
        for gztq__uqan, ddt__usick in fijko__azjb.items():
            if gztq__uqan < opu__elxq:
                fkkv__zmdqf = py_table.block_nums[gztq__uqan]
                vpro__lmfdu = py_table.block_offsets[gztq__uqan]
                for wtjc__mmwx in ddt__usick:
                    ijif__myep += f"""  cpp_arr_list[{wtjc__mmwx}] = array_to_info(arr_list_{fkkv__zmdqf}[{vpro__lmfdu}])
"""
    for vdgf__apesu in range(len(extra_arrs_tup)):
        pdxcm__mca = ccwcb__gbikt.get(opu__elxq + vdgf__apesu, -1)
        if pdxcm__mca != -1:
            hgg__wutu = [pdxcm__mca] + fijko__azjb.get(opu__elxq +
                vdgf__apesu, [])
            for wtjc__mmwx in hgg__wutu:
                ijif__myep += f"""  cpp_arr_list[{wtjc__mmwx}] = array_to_info(extra_arrs_tup[{vdgf__apesu}])
"""
    ijif__myep += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    icdfl__uhuw.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    supr__ejm = {}
    exec(ijif__myep, icdfl__uhuw, supr__ejm)
    return supr__ejm['impl']


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))
decref_table_array = types.ExternalFunction('decref_table_array', types.
    void(table_type, types.int32))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='delete_table')
        builder.call(gudhw__ryn, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='shuffle_table')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        kzrh__xaapj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='delete_shuffle_info')
        return builder.call(gudhw__ryn, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='reverse_shuffle_table')
        return builder.call(gudhw__ryn, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    key_in_out_t, same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    extra_data_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len, num_rows_ptr_t):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='hash_join_table')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.int64, types.voidptr, types.int64, types.voidptr
        ), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, dead_keys_t, n_rows_t, parallel_t):
    assert table_t == table_type, 'C++ table type expected'

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='sort_values_table')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='sample_table')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='shuffle_renormalization')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='shuffle_renormalization_group')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='drop_duplicates_table')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean, types.boolean), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb,
    udf_table_dummy_t, n_out_rows_t, n_shuffle_keys_t):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        gudhw__ryn = cgutils.get_or_insert_function(builder.module,
            kzrh__xaapj, name='groupby_and_aggregate')
        jofsq__cjnf = builder.call(gudhw__ryn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jofsq__cjnf
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t, types.voidptr, types.int64), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit(no_cpython_wrapper=True)
def array_isin(out_arr, in_arr, in_values, is_parallel):
    in_arr = decode_if_dict_array(in_arr)
    in_values = decode_if_dict_array(in_values)
    fmwp__sevet = array_to_info(in_arr)
    vlkcs__payh = array_to_info(in_values)
    ugyo__aaqu = array_to_info(out_arr)
    qfrd__ypvlr = arr_info_list_to_table([fmwp__sevet, vlkcs__payh, ugyo__aaqu]
        )
    _array_isin(ugyo__aaqu, fmwp__sevet, vlkcs__payh, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(qfrd__ypvlr)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    fmwp__sevet = array_to_info(in_arr)
    ugyo__aaqu = array_to_info(out_arr)
    _get_search_regex(fmwp__sevet, case, match, pat, ugyo__aaqu)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    qdw__pvyjo = col_array_typ.dtype
    if isinstance(qdw__pvyjo, (types.Number, TimeType)) or qdw__pvyjo in [bodo
        .datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hju__nzp, vxfj__wvn = args
                hju__nzp = builder.bitcast(hju__nzp, lir.IntType(8).
                    as_pointer().as_pointer())
                mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                ycri__chn = builder.load(builder.gep(hju__nzp, [mqzcb__vpl]))
                ycri__chn = builder.bitcast(ycri__chn, context.
                    get_data_type(qdw__pvyjo).as_pointer())
                return builder.load(builder.gep(ycri__chn, [vxfj__wvn]))
            return qdw__pvyjo(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hju__nzp, vxfj__wvn = args
                hju__nzp = builder.bitcast(hju__nzp, lir.IntType(8).
                    as_pointer().as_pointer())
                mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                ycri__chn = builder.load(builder.gep(hju__nzp, [mqzcb__vpl]))
                kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                bcid__ixzro = cgutils.get_or_insert_function(builder.module,
                    kzrh__xaapj, name='array_info_getitem')
                mnjut__dqp = cgutils.alloca_once(builder, lir.IntType(64))
                args = ycri__chn, vxfj__wvn, mnjut__dqp
                jbr__bvao = builder.call(bcid__ixzro, args)
                return context.make_tuple(builder, sig.return_type, [
                    jbr__bvao, builder.load(mnjut__dqp)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xxuqg__baich = lir.Constant(lir.IntType(64), 1)
                uvce__ogbvu = lir.Constant(lir.IntType(64), 2)
                hju__nzp, vxfj__wvn = args
                hju__nzp = builder.bitcast(hju__nzp, lir.IntType(8).
                    as_pointer().as_pointer())
                mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                ycri__chn = builder.load(builder.gep(hju__nzp, [mqzcb__vpl]))
                kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                onan__pcy = cgutils.get_or_insert_function(builder.module,
                    kzrh__xaapj, name='get_nested_info')
                args = ycri__chn, uvce__ogbvu
                rfie__tdb = builder.call(onan__pcy, args)
                kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                oqjk__rikb = cgutils.get_or_insert_function(builder.module,
                    kzrh__xaapj, name='array_info_getdata1')
                args = rfie__tdb,
                zdjf__urs = builder.call(oqjk__rikb, args)
                zdjf__urs = builder.bitcast(zdjf__urs, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                dvyh__hey = builder.sext(builder.load(builder.gep(zdjf__urs,
                    [vxfj__wvn])), lir.IntType(64))
                args = ycri__chn, xxuqg__baich
                bteff__obec = builder.call(onan__pcy, args)
                kzrh__xaapj = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                bcid__ixzro = cgutils.get_or_insert_function(builder.module,
                    kzrh__xaapj, name='array_info_getitem')
                mnjut__dqp = cgutils.alloca_once(builder, lir.IntType(64))
                args = bteff__obec, dvyh__hey, mnjut__dqp
                jbr__bvao = builder.call(bcid__ixzro, args)
                return context.make_tuple(builder, sig.return_type, [
                    jbr__bvao, builder.load(mnjut__dqp)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{qdw__pvyjo}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in (bodo.libs.bool_arr_ext.boolean_array, bodo
        .binary_array_type) or is_str_arr_type(col_array_dtype) or isinstance(
        col_array_dtype, types.Array) and (col_array_dtype.dtype == bodo.
        datetime_date_type or isinstance(col_array_dtype.dtype, bodo.TimeType)
        ):

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xgef__iwo, vxfj__wvn = args
                xgef__iwo = builder.bitcast(xgef__iwo, lir.IntType(8).
                    as_pointer().as_pointer())
                mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                ycri__chn = builder.load(builder.gep(xgef__iwo, [mqzcb__vpl]))
                ialt__ipbr = builder.bitcast(ycri__chn, context.
                    get_data_type(types.bool_).as_pointer())
                bnx__pifdw = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    ialt__ipbr, vxfj__wvn)
                kvgss__hvtep = builder.icmp_unsigned('!=', bnx__pifdw, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(kvgss__hvtep, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        qdw__pvyjo = col_array_dtype.dtype
        if qdw__pvyjo in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hju__nzp, vxfj__wvn = args
                    hju__nzp = builder.bitcast(hju__nzp, lir.IntType(8).
                        as_pointer().as_pointer())
                    mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                    ycri__chn = builder.load(builder.gep(hju__nzp, [
                        mqzcb__vpl]))
                    ycri__chn = builder.bitcast(ycri__chn, context.
                        get_data_type(qdw__pvyjo).as_pointer())
                    lkw__dkr = builder.load(builder.gep(ycri__chn, [vxfj__wvn])
                        )
                    kvgss__hvtep = builder.icmp_unsigned('!=', lkw__dkr,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(kvgss__hvtep, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(qdw__pvyjo, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hju__nzp, vxfj__wvn = args
                    hju__nzp = builder.bitcast(hju__nzp, lir.IntType(8).
                        as_pointer().as_pointer())
                    mqzcb__vpl = lir.Constant(lir.IntType(64), c_ind)
                    ycri__chn = builder.load(builder.gep(hju__nzp, [
                        mqzcb__vpl]))
                    ycri__chn = builder.bitcast(ycri__chn, context.
                        get_data_type(qdw__pvyjo).as_pointer())
                    lkw__dkr = builder.load(builder.gep(ycri__chn, [vxfj__wvn])
                        )
                    knjda__rsxh = signature(types.bool_, qdw__pvyjo)
                    bnx__pifdw = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, knjda__rsxh, (lkw__dkr,))
                    return builder.not_(builder.sext(bnx__pifdw, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
