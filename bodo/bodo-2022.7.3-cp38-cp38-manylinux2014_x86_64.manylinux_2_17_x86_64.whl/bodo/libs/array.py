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
        ekb__kjc = context.make_helper(builder, arr_type, in_arr)
        in_arr = ekb__kjc.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        lfn__fiu = context.make_helper(builder, arr_type, in_arr)
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='list_string_array_to_info')
        return builder.call(koq__kea, [lfn__fiu.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                lbs__qqeqc = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for bfqb__oxnvu in arr_typ.data:
                    lbs__qqeqc += get_types(bfqb__oxnvu)
                return lbs__qqeqc
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
            vvy__ylhw = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ixpjw__pyd = context.make_helper(builder, arr_typ, value=arr)
                bpb__rsiv = get_lengths(_get_map_arr_data_type(arr_typ),
                    ixpjw__pyd.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                cga__adkyp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                bpb__rsiv = get_lengths(arr_typ.dtype, cga__adkyp.data)
                bpb__rsiv = cgutils.pack_array(builder, [cga__adkyp.
                    n_arrays] + [builder.extract_value(bpb__rsiv,
                    vxli__jnzrt) for vxli__jnzrt in range(bpb__rsiv.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                cga__adkyp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                bpb__rsiv = []
                for vxli__jnzrt, bfqb__oxnvu in enumerate(arr_typ.data):
                    ovt__dfr = get_lengths(bfqb__oxnvu, builder.
                        extract_value(cga__adkyp.data, vxli__jnzrt))
                    bpb__rsiv += [builder.extract_value(ovt__dfr,
                        qtbmk__fqc) for qtbmk__fqc in range(ovt__dfr.type.
                        count)]
                bpb__rsiv = cgutils.pack_array(builder, [vvy__ylhw, context
                    .get_constant(types.int64, -1)] + bpb__rsiv)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                bpb__rsiv = cgutils.pack_array(builder, [vvy__ylhw])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return bpb__rsiv

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ixpjw__pyd = context.make_helper(builder, arr_typ, value=arr)
                lni__esip = get_buffers(_get_map_arr_data_type(arr_typ),
                    ixpjw__pyd.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                cga__adkyp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                daca__txkzi = get_buffers(arr_typ.dtype, cga__adkyp.data)
                aby__krmd = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, cga__adkyp.offsets)
                clp__vzko = builder.bitcast(aby__krmd.data, lir.IntType(8).
                    as_pointer())
                kqqwb__lpo = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, cga__adkyp.null_bitmap)
                bpl__wzucs = builder.bitcast(kqqwb__lpo.data, lir.IntType(8
                    ).as_pointer())
                lni__esip = cgutils.pack_array(builder, [clp__vzko,
                    bpl__wzucs] + [builder.extract_value(daca__txkzi,
                    vxli__jnzrt) for vxli__jnzrt in range(daca__txkzi.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                cga__adkyp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                daca__txkzi = []
                for vxli__jnzrt, bfqb__oxnvu in enumerate(arr_typ.data):
                    orryt__vuqnj = get_buffers(bfqb__oxnvu, builder.
                        extract_value(cga__adkyp.data, vxli__jnzrt))
                    daca__txkzi += [builder.extract_value(orryt__vuqnj,
                        qtbmk__fqc) for qtbmk__fqc in range(orryt__vuqnj.
                        type.count)]
                kqqwb__lpo = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, cga__adkyp.null_bitmap)
                bpl__wzucs = builder.bitcast(kqqwb__lpo.data, lir.IntType(8
                    ).as_pointer())
                lni__esip = cgutils.pack_array(builder, [bpl__wzucs] +
                    daca__txkzi)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                xawn__oqzdj = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    xawn__oqzdj = int128_type
                elif arr_typ == datetime_date_array_type:
                    xawn__oqzdj = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                gltsx__sccb = context.make_array(types.Array(xawn__oqzdj, 1,
                    'C'))(context, builder, arr.data)
                kqqwb__lpo = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                swmq__nubbc = builder.bitcast(gltsx__sccb.data, lir.IntType
                    (8).as_pointer())
                bpl__wzucs = builder.bitcast(kqqwb__lpo.data, lir.IntType(8
                    ).as_pointer())
                lni__esip = cgutils.pack_array(builder, [bpl__wzucs,
                    swmq__nubbc])
            elif arr_typ in (string_array_type, binary_array_type):
                cga__adkyp = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                cie__vfg = context.make_helper(builder, offset_arr_type,
                    cga__adkyp.offsets).data
                izlel__jjyuz = context.make_helper(builder, char_arr_type,
                    cga__adkyp.data).data
                bpmnh__uawmx = context.make_helper(builder,
                    null_bitmap_arr_type, cga__adkyp.null_bitmap).data
                lni__esip = cgutils.pack_array(builder, [builder.bitcast(
                    cie__vfg, lir.IntType(8).as_pointer()), builder.bitcast
                    (bpmnh__uawmx, lir.IntType(8).as_pointer()), builder.
                    bitcast(izlel__jjyuz, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                swmq__nubbc = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                gmi__gnmmv = lir.Constant(lir.IntType(8).as_pointer(), None)
                lni__esip = cgutils.pack_array(builder, [gmi__gnmmv,
                    swmq__nubbc])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return lni__esip

        def get_field_names(arr_typ):
            udt__mnfj = []
            if isinstance(arr_typ, StructArrayType):
                for hvrv__gzcxg, kepyf__bng in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    udt__mnfj.append(hvrv__gzcxg)
                    udt__mnfj += get_field_names(kepyf__bng)
            elif isinstance(arr_typ, ArrayItemArrayType):
                udt__mnfj += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                udt__mnfj += get_field_names(_get_map_arr_data_type(arr_typ))
            return udt__mnfj
        lbs__qqeqc = get_types(arr_type)
        nflb__gmkxp = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in lbs__qqeqc])
        omi__wmga = cgutils.alloca_once_value(builder, nflb__gmkxp)
        bpb__rsiv = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, bpb__rsiv)
        lni__esip = get_buffers(arr_type, in_arr)
        gjo__dyjfl = cgutils.alloca_once_value(builder, lni__esip)
        udt__mnfj = get_field_names(arr_type)
        if len(udt__mnfj) == 0:
            udt__mnfj = ['irrelevant']
        ryws__jnf = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in udt__mnfj])
        evbp__uxib = cgutils.alloca_once_value(builder, ryws__jnf)
        if isinstance(arr_type, MapArrayType):
            bqwd__lvrk = _get_map_arr_data_type(arr_type)
            fib__xhmof = context.make_helper(builder, arr_type, value=in_arr)
            mnxjo__bnhlj = fib__xhmof.data
        else:
            bqwd__lvrk = arr_type
            mnxjo__bnhlj = in_arr
        rkbtt__qemvb = context.make_helper(builder, bqwd__lvrk, mnxjo__bnhlj)
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='nested_array_to_info')
        efv__rhut = builder.call(koq__kea, [builder.bitcast(omi__wmga, lir.
            IntType(32).as_pointer()), builder.bitcast(gjo__dyjfl, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            evbp__uxib, lir.IntType(8).as_pointer()), rkbtt__qemvb.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
    if arr_type in (string_array_type, binary_array_type):
        xpw__mam = context.make_helper(builder, arr_type, in_arr)
        puj__ovar = ArrayItemArrayType(char_arr_type)
        lfn__fiu = context.make_helper(builder, puj__ovar, xpw__mam.data)
        cga__adkyp = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        cie__vfg = context.make_helper(builder, offset_arr_type, cga__adkyp
            .offsets).data
        izlel__jjyuz = context.make_helper(builder, char_arr_type,
            cga__adkyp.data).data
        bpmnh__uawmx = context.make_helper(builder, null_bitmap_arr_type,
            cga__adkyp.null_bitmap).data
        rxsxy__ldb = builder.zext(builder.load(builder.gep(cie__vfg, [
            cga__adkyp.n_arrays])), lir.IntType(64))
        toc__tryi = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='string_array_to_info')
        return builder.call(koq__kea, [cga__adkyp.n_arrays, rxsxy__ldb,
            izlel__jjyuz, cie__vfg, bpmnh__uawmx, lfn__fiu.meminfo, toc__tryi])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        htzk__xwcmj = arr.data
        klfv__fcrsh = arr.indices
        sig = array_info_type(arr_type.data)
        ljmf__sgsyf = array_to_info_codegen(context, builder, sig, (
            htzk__xwcmj,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        uci__adzgx = array_to_info_codegen(context, builder, sig, (
            klfv__fcrsh,), False)
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(32)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='dict_str_array_to_info')
        fht__ftbt = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(koq__kea, [ljmf__sgsyf, uci__adzgx, fht__ftbt])
    lkni__ufbq = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        aaaf__znssu = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        ycvf__awdjf = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(ycvf__awdjf, 1, 'C')
        lkni__ufbq = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if lkni__ufbq:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        vvy__ylhw = builder.extract_value(arr.shape, 0)
        mdmz__uxrvc = arr_type.dtype
        qxun__vuy = numba_to_c_type(mdmz__uxrvc)
        vlpn__eeoyd = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), qxun__vuy))
        if lkni__ufbq:
            zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            koq__kea = cgutils.get_or_insert_function(builder.module,
                zqr__yyn, name='categorical_array_to_info')
            return builder.call(koq__kea, [vvy__ylhw, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                vlpn__eeoyd), aaaf__znssu, arr.meminfo])
        else:
            zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            koq__kea = cgutils.get_or_insert_function(builder.module,
                zqr__yyn, name='numpy_array_to_info')
            return builder.call(koq__kea, [vvy__ylhw, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                vlpn__eeoyd), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        mdmz__uxrvc = arr_type.dtype
        xawn__oqzdj = mdmz__uxrvc
        if isinstance(arr_type, DecimalArrayType):
            xawn__oqzdj = int128_type
        if arr_type == datetime_date_array_type:
            xawn__oqzdj = types.int64
        gltsx__sccb = context.make_array(types.Array(xawn__oqzdj, 1, 'C'))(
            context, builder, arr.data)
        vvy__ylhw = builder.extract_value(gltsx__sccb.shape, 0)
        evu__jdl = context.make_array(types.Array(types.uint8, 1, 'C'))(context
            , builder, arr.null_bitmap)
        qxun__vuy = numba_to_c_type(mdmz__uxrvc)
        vlpn__eeoyd = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), qxun__vuy))
        if isinstance(arr_type, DecimalArrayType):
            zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            koq__kea = cgutils.get_or_insert_function(builder.module,
                zqr__yyn, name='decimal_array_to_info')
            return builder.call(koq__kea, [vvy__ylhw, builder.bitcast(
                gltsx__sccb.data, lir.IntType(8).as_pointer()), builder.
                load(vlpn__eeoyd), builder.bitcast(evu__jdl.data, lir.
                IntType(8).as_pointer()), gltsx__sccb.meminfo, evu__jdl.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            koq__kea = cgutils.get_or_insert_function(builder.module,
                zqr__yyn, name='nullable_array_to_info')
            return builder.call(koq__kea, [vvy__ylhw, builder.bitcast(
                gltsx__sccb.data, lir.IntType(8).as_pointer()), builder.
                load(vlpn__eeoyd), builder.bitcast(evu__jdl.data, lir.
                IntType(8).as_pointer()), gltsx__sccb.meminfo, evu__jdl.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        qky__qlwnp = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        xjvv__ztdk = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        vvy__ylhw = builder.extract_value(qky__qlwnp.shape, 0)
        qxun__vuy = numba_to_c_type(arr_type.arr_type.dtype)
        vlpn__eeoyd = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), qxun__vuy))
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='interval_array_to_info')
        return builder.call(koq__kea, [vvy__ylhw, builder.bitcast(
            qky__qlwnp.data, lir.IntType(8).as_pointer()), builder.bitcast(
            xjvv__ztdk.data, lir.IntType(8).as_pointer()), builder.load(
            vlpn__eeoyd), qky__qlwnp.meminfo, xjvv__ztdk.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    tho__rzwbv = cgutils.alloca_once(builder, lir.IntType(64))
    swmq__nubbc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    shssw__amned = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(64).as_pointer(), lir.IntType(8).as_pointer().
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
        name='info_to_numpy_array')
    builder.call(koq__kea, [in_info, tho__rzwbv, swmq__nubbc, shssw__amned])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    ebyc__gdx = context.get_value_type(types.intp)
    pdsje__jptz = cgutils.pack_array(builder, [builder.load(tho__rzwbv)],
        ty=ebyc__gdx)
    fof__dhrhz = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    atxu__mywjw = cgutils.pack_array(builder, [fof__dhrhz], ty=ebyc__gdx)
    izlel__jjyuz = builder.bitcast(builder.load(swmq__nubbc), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=izlel__jjyuz, shape=
        pdsje__jptz, strides=atxu__mywjw, itemsize=fof__dhrhz, meminfo=
        builder.load(shssw__amned))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    imter__rxolz = context.make_helper(builder, arr_type)
    zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(8).as_pointer().as_pointer()])
    koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
        name='info_to_list_string_array')
    builder.call(koq__kea, [in_info, imter__rxolz._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return imter__rxolz._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    ywv__jsglx = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        wqdk__bpeu = lengths_pos
        qyd__zyop = infos_pos
        mnsic__wxx, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        rwsso__xirt = ArrayItemArrayPayloadType(arr_typ)
        iyx__ghx = context.get_data_type(rwsso__xirt)
        vxda__xzenm = context.get_abi_sizeof(iyx__ghx)
        ddqp__zlphb = define_array_item_dtor(context, builder, arr_typ,
            rwsso__xirt)
        osghy__lebut = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, vxda__xzenm), ddqp__zlphb)
        wxju__ljpg = context.nrt.meminfo_data(builder, osghy__lebut)
        uab__cwk = builder.bitcast(wxju__ljpg, iyx__ghx.as_pointer())
        cga__adkyp = cgutils.create_struct_proxy(rwsso__xirt)(context, builder)
        cga__adkyp.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), wqdk__bpeu)
        cga__adkyp.data = mnsic__wxx
        tsj__baxz = builder.load(array_infos_ptr)
        dxos__bxs = builder.bitcast(builder.extract_value(tsj__baxz,
            qyd__zyop), ywv__jsglx)
        cga__adkyp.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, dxos__bxs)
        prifd__rem = builder.bitcast(builder.extract_value(tsj__baxz, 
            qyd__zyop + 1), ywv__jsglx)
        cga__adkyp.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, prifd__rem)
        builder.store(cga__adkyp._getvalue(), uab__cwk)
        lfn__fiu = context.make_helper(builder, arr_typ)
        lfn__fiu.meminfo = osghy__lebut
        return lfn__fiu._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        gddl__irunm = []
        qyd__zyop = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for pyh__vrcn in arr_typ.data:
            mnsic__wxx, lengths_pos, infos_pos = nested_to_array(context,
                builder, pyh__vrcn, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            gddl__irunm.append(mnsic__wxx)
        rwsso__xirt = StructArrayPayloadType(arr_typ.data)
        iyx__ghx = context.get_value_type(rwsso__xirt)
        vxda__xzenm = context.get_abi_sizeof(iyx__ghx)
        ddqp__zlphb = define_struct_arr_dtor(context, builder, arr_typ,
            rwsso__xirt)
        osghy__lebut = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, vxda__xzenm), ddqp__zlphb)
        wxju__ljpg = context.nrt.meminfo_data(builder, osghy__lebut)
        uab__cwk = builder.bitcast(wxju__ljpg, iyx__ghx.as_pointer())
        cga__adkyp = cgutils.create_struct_proxy(rwsso__xirt)(context, builder)
        cga__adkyp.data = cgutils.pack_array(builder, gddl__irunm
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, gddl__irunm)
        tsj__baxz = builder.load(array_infos_ptr)
        prifd__rem = builder.bitcast(builder.extract_value(tsj__baxz,
            qyd__zyop), ywv__jsglx)
        cga__adkyp.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, prifd__rem)
        builder.store(cga__adkyp._getvalue(), uab__cwk)
        xku__miqw = context.make_helper(builder, arr_typ)
        xku__miqw.meminfo = osghy__lebut
        return xku__miqw._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        tsj__baxz = builder.load(array_infos_ptr)
        jgpme__siwq = builder.bitcast(builder.extract_value(tsj__baxz,
            infos_pos), ywv__jsglx)
        xpw__mam = context.make_helper(builder, arr_typ)
        puj__ovar = ArrayItemArrayType(char_arr_type)
        lfn__fiu = context.make_helper(builder, puj__ovar)
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_to_string_array')
        builder.call(koq__kea, [jgpme__siwq, lfn__fiu._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        xpw__mam.data = lfn__fiu._getvalue()
        return xpw__mam._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        tsj__baxz = builder.load(array_infos_ptr)
        cbbas__evgl = builder.bitcast(builder.extract_value(tsj__baxz, 
            infos_pos + 1), ywv__jsglx)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            cbbas__evgl), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        xawn__oqzdj = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            xawn__oqzdj = int128_type
        elif arr_typ == datetime_date_array_type:
            xawn__oqzdj = types.int64
        tsj__baxz = builder.load(array_infos_ptr)
        prifd__rem = builder.bitcast(builder.extract_value(tsj__baxz,
            infos_pos), ywv__jsglx)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, prifd__rem)
        cbbas__evgl = builder.bitcast(builder.extract_value(tsj__baxz, 
            infos_pos + 1), ywv__jsglx)
        arr.data = _lower_info_to_array_numpy(types.Array(xawn__oqzdj, 1,
            'C'), context, builder, cbbas__evgl)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, ipls__peskt = args
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
                return 1 + sum([get_num_arrays(pyh__vrcn) for pyh__vrcn in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(pyh__vrcn) for pyh__vrcn in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            wmcrb__ttt = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            wmcrb__ttt = _get_map_arr_data_type(arr_type)
        else:
            wmcrb__ttt = arr_type
        oopha__zlyj = get_num_arrays(wmcrb__ttt)
        bpb__rsiv = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for ipls__peskt in range(oopha__zlyj)])
        lengths_ptr = cgutils.alloca_once_value(builder, bpb__rsiv)
        gmi__gnmmv = lir.Constant(lir.IntType(8).as_pointer(), None)
        ztzgs__htobc = cgutils.pack_array(builder, [gmi__gnmmv for
            ipls__peskt in range(get_num_infos(wmcrb__ttt))])
        array_infos_ptr = cgutils.alloca_once_value(builder, ztzgs__htobc)
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_to_nested_array')
        builder.call(koq__kea, [in_info, builder.bitcast(lengths_ptr, lir.
            IntType(64).as_pointer()), builder.bitcast(array_infos_ptr, lir
            .IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, ipls__peskt, ipls__peskt = nested_to_array(context, builder,
            wmcrb__ttt, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            ekb__kjc = context.make_helper(builder, arr_type)
            ekb__kjc.data = arr
            context.nrt.incref(builder, wmcrb__ttt, arr)
            arr = ekb__kjc._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, wmcrb__ttt)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        xpw__mam = context.make_helper(builder, arr_type)
        puj__ovar = ArrayItemArrayType(char_arr_type)
        lfn__fiu = context.make_helper(builder, puj__ovar)
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_to_string_array')
        builder.call(koq__kea, [in_info, lfn__fiu._get_ptr_by_name('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        xpw__mam.data = lfn__fiu._getvalue()
        return xpw__mam._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='get_nested_info')
        ljmf__sgsyf = builder.call(koq__kea, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        uci__adzgx = builder.call(koq__kea, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        qjdj__ttvab = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        qjdj__ttvab.data = info_to_array_codegen(context, builder, sig, (
            ljmf__sgsyf, context.get_constant_null(arr_type.data)))
        tzb__dibe = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = tzb__dibe(array_info_type, tzb__dibe)
        qjdj__ttvab.indices = info_to_array_codegen(context, builder, sig,
            (uci__adzgx, context.get_constant_null(tzb__dibe)))
        zqr__yyn = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='get_has_global_dictionary')
        fht__ftbt = builder.call(koq__kea, [in_info])
        qjdj__ttvab.has_global_dictionary = builder.trunc(fht__ftbt,
            cgutils.bool_t)
        return qjdj__ttvab._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ycvf__awdjf = get_categories_int_type(arr_type.dtype)
        yly__ejlmz = types.Array(ycvf__awdjf, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(yly__ejlmz, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            hulq__wbfl = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(hulq__wbfl))
            int_type = arr_type.dtype.int_type
            ygxr__mns = arr_type.dtype.data.data
            dlv__toxtk = context.get_constant_generic(builder, ygxr__mns,
                hulq__wbfl)
            mdmz__uxrvc = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(ygxr__mns), [dlv__toxtk])
        else:
            mdmz__uxrvc = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, mdmz__uxrvc)
        out_arr.dtype = mdmz__uxrvc
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        izlel__jjyuz = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = izlel__jjyuz
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        xawn__oqzdj = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            xawn__oqzdj = int128_type
        elif arr_type == datetime_date_array_type:
            xawn__oqzdj = types.int64
        itaec__bmb = types.Array(xawn__oqzdj, 1, 'C')
        gltsx__sccb = context.make_array(itaec__bmb)(context, builder)
        belww__jpz = types.Array(types.uint8, 1, 'C')
        hxd__iabm = context.make_array(belww__jpz)(context, builder)
        tho__rzwbv = cgutils.alloca_once(builder, lir.IntType(64))
        xhirs__loru = cgutils.alloca_once(builder, lir.IntType(64))
        swmq__nubbc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ehgx__juyk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        shssw__amned = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        mocp__zwj = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_to_nullable_array')
        builder.call(koq__kea, [in_info, tho__rzwbv, xhirs__loru,
            swmq__nubbc, ehgx__juyk, shssw__amned, mocp__zwj])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ebyc__gdx = context.get_value_type(types.intp)
        pdsje__jptz = cgutils.pack_array(builder, [builder.load(tho__rzwbv)
            ], ty=ebyc__gdx)
        fof__dhrhz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(xawn__oqzdj)))
        atxu__mywjw = cgutils.pack_array(builder, [fof__dhrhz], ty=ebyc__gdx)
        izlel__jjyuz = builder.bitcast(builder.load(swmq__nubbc), context.
            get_data_type(xawn__oqzdj).as_pointer())
        numba.np.arrayobj.populate_array(gltsx__sccb, data=izlel__jjyuz,
            shape=pdsje__jptz, strides=atxu__mywjw, itemsize=fof__dhrhz,
            meminfo=builder.load(shssw__amned))
        arr.data = gltsx__sccb._getvalue()
        pdsje__jptz = cgutils.pack_array(builder, [builder.load(xhirs__loru
            )], ty=ebyc__gdx)
        fof__dhrhz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        atxu__mywjw = cgutils.pack_array(builder, [fof__dhrhz], ty=ebyc__gdx)
        izlel__jjyuz = builder.bitcast(builder.load(ehgx__juyk), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(hxd__iabm, data=izlel__jjyuz,
            shape=pdsje__jptz, strides=atxu__mywjw, itemsize=fof__dhrhz,
            meminfo=builder.load(mocp__zwj))
        arr.null_bitmap = hxd__iabm._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        qky__qlwnp = context.make_array(arr_type.arr_type)(context, builder)
        xjvv__ztdk = context.make_array(arr_type.arr_type)(context, builder)
        tho__rzwbv = cgutils.alloca_once(builder, lir.IntType(64))
        tvobg__jndu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        xlbp__htwa = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        xpd__wjy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        kujmc__bpmy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_to_interval_array')
        builder.call(koq__kea, [in_info, tho__rzwbv, tvobg__jndu,
            xlbp__htwa, xpd__wjy, kujmc__bpmy])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ebyc__gdx = context.get_value_type(types.intp)
        pdsje__jptz = cgutils.pack_array(builder, [builder.load(tho__rzwbv)
            ], ty=ebyc__gdx)
        fof__dhrhz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        atxu__mywjw = cgutils.pack_array(builder, [fof__dhrhz], ty=ebyc__gdx)
        xjd__nrbum = builder.bitcast(builder.load(tvobg__jndu), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(qky__qlwnp, data=xjd__nrbum, shape
            =pdsje__jptz, strides=atxu__mywjw, itemsize=fof__dhrhz, meminfo
            =builder.load(xpd__wjy))
        arr.left = qky__qlwnp._getvalue()
        veayz__uetp = builder.bitcast(builder.load(xlbp__htwa), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(xjvv__ztdk, data=veayz__uetp,
            shape=pdsje__jptz, strides=atxu__mywjw, itemsize=fof__dhrhz,
            meminfo=builder.load(kujmc__bpmy))
        arr.right = xjvv__ztdk._getvalue()
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
        vvy__ylhw, ipls__peskt = args
        qxun__vuy = numba_to_c_type(array_type.dtype)
        vlpn__eeoyd = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), qxun__vuy))
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='alloc_numpy')
        return builder.call(koq__kea, [vvy__ylhw, builder.load(vlpn__eeoyd)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        vvy__ylhw, bitoa__rza = args
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='alloc_string_array')
        return builder.call(koq__kea, [vvy__ylhw, bitoa__rza])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    ozi__avm, = args
    qifr__psrhm = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], ozi__avm)
    zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(8
        ).as_pointer().as_pointer(), lir.IntType(64)])
    koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
        name='arr_info_list_to_table')
    return builder.call(koq__kea, [qifr__psrhm.data, qifr__psrhm.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_from_table')
        return builder.call(koq__kea, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    cbhp__nzo = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, pzhd__lxs, ipls__peskt = args
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='info_from_table')
        ujvlu__yxzgn = cgutils.create_struct_proxy(cbhp__nzo)(context, builder)
        ujvlu__yxzgn.parent = cgutils.get_null_value(ujvlu__yxzgn.parent.type)
        yrl__azqj = context.make_array(table_idx_arr_t)(context, builder,
            pzhd__lxs)
        sukgs__uybm = context.get_constant(types.int64, -1)
        tjiuy__ekp = context.get_constant(types.int64, 0)
        whhzq__skn = cgutils.alloca_once_value(builder, tjiuy__ekp)
        for t, ihnmc__jcma in cbhp__nzo.type_to_blk.items():
            qsuh__sho = context.get_constant(types.int64, len(cbhp__nzo.
                block_to_arr_ind[ihnmc__jcma]))
            ipls__peskt, dhqv__vnalm = ListInstance.allocate_ex(context,
                builder, types.List(t), qsuh__sho)
            dhqv__vnalm.size = qsuh__sho
            hjm__xgx = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(cbhp__nzo.block_to_arr_ind[
                ihnmc__jcma], dtype=np.int64))
            anc__jkw = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, hjm__xgx)
            with cgutils.for_range(builder, qsuh__sho) as qzg__emkhn:
                vxli__jnzrt = qzg__emkhn.index
                yqpxg__sdwfi = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), anc__jkw,
                    vxli__jnzrt)
                qqpg__gto = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, yrl__azqj, yqpxg__sdwfi)
                oxig__zxza = builder.icmp_unsigned('!=', qqpg__gto, sukgs__uybm
                    )
                with builder.if_else(oxig__zxza) as (tad__pkr, svdne__xtydk):
                    with tad__pkr:
                        qat__rxybb = builder.call(koq__kea, [cpp_table,
                            qqpg__gto])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            qat__rxybb])
                        dhqv__vnalm.inititem(vxli__jnzrt, arr, incref=False)
                        vvy__ylhw = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(vvy__ylhw, whhzq__skn)
                    with svdne__xtydk:
                        gpvu__qjmh = context.get_constant_null(t)
                        dhqv__vnalm.inititem(vxli__jnzrt, gpvu__qjmh,
                            incref=False)
            setattr(ujvlu__yxzgn, f'block_{ihnmc__jcma}', dhqv__vnalm.value)
        ujvlu__yxzgn.len = builder.load(whhzq__skn)
        return ujvlu__yxzgn._getvalue()
    return cbhp__nzo(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    mawy__ohe = out_col_inds_t.instance_type.meta
    cbhp__nzo = unwrap_typeref(out_types_t.types[0])
    vhc__jer = [unwrap_typeref(out_types_t.types[vxli__jnzrt]) for
        vxli__jnzrt in range(1, len(out_types_t.types))]
    dfbx__iuum = {}
    xxrer__smrcv = get_overload_const_int(n_table_cols_t)
    jumm__svir = {fvwdj__bocy: vxli__jnzrt for vxli__jnzrt, fvwdj__bocy in
        enumerate(mawy__ohe)}
    if not is_overload_none(unknown_cat_arrs_t):
        obb__mnsg = {lcbji__rhi: vxli__jnzrt for vxli__jnzrt, lcbji__rhi in
            enumerate(cat_inds_t.instance_type.meta)}
    oyl__wdye = []
    luolx__hzti = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(cbhp__nzo, bodo.TableType):
        luolx__hzti += f'  py_table = init_table(py_table_type, False)\n'
        luolx__hzti += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for hfmu__ottw, ihnmc__jcma in cbhp__nzo.type_to_blk.items():
            nyp__odxql = [jumm__svir.get(vxli__jnzrt, -1) for vxli__jnzrt in
                cbhp__nzo.block_to_arr_ind[ihnmc__jcma]]
            dfbx__iuum[f'out_inds_{ihnmc__jcma}'] = np.array(nyp__odxql, np
                .int64)
            dfbx__iuum[f'out_type_{ihnmc__jcma}'] = hfmu__ottw
            dfbx__iuum[f'typ_list_{ihnmc__jcma}'] = types.List(hfmu__ottw)
            osodx__hiob = f'out_type_{ihnmc__jcma}'
            if type_has_unknown_cats(hfmu__ottw):
                if is_overload_none(unknown_cat_arrs_t):
                    luolx__hzti += f"""  in_arr_list_{ihnmc__jcma} = get_table_block(out_types_t[0], {ihnmc__jcma})
"""
                    osodx__hiob = f'in_arr_list_{ihnmc__jcma}[i]'
                else:
                    dfbx__iuum[f'cat_arr_inds_{ihnmc__jcma}'] = np.array([
                        obb__mnsg.get(vxli__jnzrt, -1) for vxli__jnzrt in
                        cbhp__nzo.block_to_arr_ind[ihnmc__jcma]], np.int64)
                    osodx__hiob = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{ihnmc__jcma}[i]]')
            qsuh__sho = len(cbhp__nzo.block_to_arr_ind[ihnmc__jcma])
            luolx__hzti += f"""  arr_list_{ihnmc__jcma} = alloc_list_like(typ_list_{ihnmc__jcma}, {qsuh__sho}, False)
"""
            luolx__hzti += f'  for i in range(len(arr_list_{ihnmc__jcma})):\n'
            luolx__hzti += (
                f'    cpp_ind_{ihnmc__jcma} = out_inds_{ihnmc__jcma}[i]\n')
            luolx__hzti += f'    if cpp_ind_{ihnmc__jcma} == -1:\n'
            luolx__hzti += f'      continue\n'
            luolx__hzti += f"""    arr_{ihnmc__jcma} = info_to_array(info_from_table(cpp_table, cpp_ind_{ihnmc__jcma}), {osodx__hiob})
"""
            luolx__hzti += (
                f'    arr_list_{ihnmc__jcma}[i] = arr_{ihnmc__jcma}\n')
            luolx__hzti += f"""  py_table = set_table_block(py_table, arr_list_{ihnmc__jcma}, {ihnmc__jcma})
"""
        oyl__wdye.append('py_table')
    elif cbhp__nzo != types.none:
        sdpuz__xmjsw = jumm__svir.get(0, -1)
        if sdpuz__xmjsw != -1:
            dfbx__iuum[f'arr_typ_arg0'] = cbhp__nzo
            osodx__hiob = f'arr_typ_arg0'
            if type_has_unknown_cats(cbhp__nzo):
                if is_overload_none(unknown_cat_arrs_t):
                    osodx__hiob = f'out_types_t[0]'
                else:
                    osodx__hiob = f'unknown_cat_arrs_t[{obb__mnsg[0]}]'
            luolx__hzti += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {sdpuz__xmjsw}), {osodx__hiob})
"""
            oyl__wdye.append('out_arg0')
    for vxli__jnzrt, t in enumerate(vhc__jer):
        sdpuz__xmjsw = jumm__svir.get(xxrer__smrcv + vxli__jnzrt, -1)
        if sdpuz__xmjsw != -1:
            dfbx__iuum[f'extra_arr_type_{vxli__jnzrt}'] = t
            osodx__hiob = f'extra_arr_type_{vxli__jnzrt}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    osodx__hiob = f'out_types_t[{vxli__jnzrt + 1}]'
                else:
                    osodx__hiob = (
                        f'unknown_cat_arrs_t[{obb__mnsg[xxrer__smrcv + vxli__jnzrt]}]'
                        )
            luolx__hzti += f"""  out_{vxli__jnzrt} = info_to_array(info_from_table(cpp_table, {sdpuz__xmjsw}), {osodx__hiob})
"""
            oyl__wdye.append(f'out_{vxli__jnzrt}')
    wwoig__pvegb = ',' if len(oyl__wdye) == 1 else ''
    luolx__hzti += f"  return ({', '.join(oyl__wdye)}{wwoig__pvegb})\n"
    dfbx__iuum.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(mawy__ohe), 'py_table_type': cbhp__nzo})
    sau__ofjmm = {}
    exec(luolx__hzti, dfbx__iuum, sau__ofjmm)
    return sau__ofjmm['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    cbhp__nzo = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, ipls__peskt = args
        tyji__ijjg = cgutils.create_struct_proxy(cbhp__nzo)(context,
            builder, py_table)
        if cbhp__nzo.has_runtime_cols:
            cwy__ihzxz = lir.Constant(lir.IntType(64), 0)
            for ihnmc__jcma, t in enumerate(cbhp__nzo.arr_types):
                eopr__rwy = getattr(tyji__ijjg, f'block_{ihnmc__jcma}')
                clz__dlnsg = ListInstance(context, builder, types.List(t),
                    eopr__rwy)
                cwy__ihzxz = builder.add(cwy__ihzxz, clz__dlnsg.size)
        else:
            cwy__ihzxz = lir.Constant(lir.IntType(64), len(cbhp__nzo.arr_types)
                )
        ipls__peskt, dnok__wlzs = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), cwy__ihzxz)
        dnok__wlzs.size = cwy__ihzxz
        if cbhp__nzo.has_runtime_cols:
            zovn__suwbp = lir.Constant(lir.IntType(64), 0)
            for ihnmc__jcma, t in enumerate(cbhp__nzo.arr_types):
                eopr__rwy = getattr(tyji__ijjg, f'block_{ihnmc__jcma}')
                clz__dlnsg = ListInstance(context, builder, types.List(t),
                    eopr__rwy)
                qsuh__sho = clz__dlnsg.size
                with cgutils.for_range(builder, qsuh__sho) as qzg__emkhn:
                    vxli__jnzrt = qzg__emkhn.index
                    arr = clz__dlnsg.getitem(vxli__jnzrt)
                    bpm__vqd = signature(array_info_type, t)
                    rbe__acrx = arr,
                    jbzg__nay = array_to_info_codegen(context, builder,
                        bpm__vqd, rbe__acrx)
                    dnok__wlzs.inititem(builder.add(zovn__suwbp,
                        vxli__jnzrt), jbzg__nay, incref=False)
                zovn__suwbp = builder.add(zovn__suwbp, qsuh__sho)
        else:
            for t, ihnmc__jcma in cbhp__nzo.type_to_blk.items():
                qsuh__sho = context.get_constant(types.int64, len(cbhp__nzo
                    .block_to_arr_ind[ihnmc__jcma]))
                eopr__rwy = getattr(tyji__ijjg, f'block_{ihnmc__jcma}')
                clz__dlnsg = ListInstance(context, builder, types.List(t),
                    eopr__rwy)
                hjm__xgx = context.make_constant_array(builder, types.Array
                    (types.int64, 1, 'C'), np.array(cbhp__nzo.
                    block_to_arr_ind[ihnmc__jcma], dtype=np.int64))
                anc__jkw = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, hjm__xgx)
                with cgutils.for_range(builder, qsuh__sho) as qzg__emkhn:
                    vxli__jnzrt = qzg__emkhn.index
                    yqpxg__sdwfi = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), anc__jkw, vxli__jnzrt)
                    rdqwu__gtk = signature(types.none, cbhp__nzo, types.
                        List(t), types.int64, types.int64)
                    gpngt__kpt = py_table, eopr__rwy, vxli__jnzrt, yqpxg__sdwfi
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, rdqwu__gtk, gpngt__kpt)
                    arr = clz__dlnsg.getitem(vxli__jnzrt)
                    bpm__vqd = signature(array_info_type, t)
                    rbe__acrx = arr,
                    jbzg__nay = array_to_info_codegen(context, builder,
                        bpm__vqd, rbe__acrx)
                    dnok__wlzs.inititem(yqpxg__sdwfi, jbzg__nay, incref=False)
        vntnv__fgz = dnok__wlzs.value
        krdn__zdnr = signature(table_type, types.List(array_info_type))
        fkxd__xmv = vntnv__fgz,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            krdn__zdnr, fkxd__xmv)
        context.nrt.decref(builder, types.List(array_info_type), vntnv__fgz)
        return cpp_table
    return table_type(cbhp__nzo, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    nowqv__rcd = in_col_inds_t.instance_type.meta
    dfbx__iuum = {}
    xxrer__smrcv = get_overload_const_int(n_table_cols_t)
    cwsn__fxyju = defaultdict(list)
    jumm__svir = {}
    for vxli__jnzrt, fvwdj__bocy in enumerate(nowqv__rcd):
        if fvwdj__bocy in jumm__svir:
            cwsn__fxyju[fvwdj__bocy].append(vxli__jnzrt)
        else:
            jumm__svir[fvwdj__bocy] = vxli__jnzrt
    luolx__hzti = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    luolx__hzti += (
        f'  cpp_arr_list = alloc_empty_list_type({len(nowqv__rcd)}, array_info_type)\n'
        )
    if py_table != types.none:
        for ihnmc__jcma in py_table.type_to_blk.values():
            nyp__odxql = [jumm__svir.get(vxli__jnzrt, -1) for vxli__jnzrt in
                py_table.block_to_arr_ind[ihnmc__jcma]]
            dfbx__iuum[f'out_inds_{ihnmc__jcma}'] = np.array(nyp__odxql, np
                .int64)
            dfbx__iuum[f'arr_inds_{ihnmc__jcma}'] = np.array(py_table.
                block_to_arr_ind[ihnmc__jcma], np.int64)
            luolx__hzti += (
                f'  arr_list_{ihnmc__jcma} = get_table_block(py_table, {ihnmc__jcma})\n'
                )
            luolx__hzti += f'  for i in range(len(arr_list_{ihnmc__jcma})):\n'
            luolx__hzti += (
                f'    out_arr_ind_{ihnmc__jcma} = out_inds_{ihnmc__jcma}[i]\n')
            luolx__hzti += f'    if out_arr_ind_{ihnmc__jcma} == -1:\n'
            luolx__hzti += f'      continue\n'
            luolx__hzti += (
                f'    arr_ind_{ihnmc__jcma} = arr_inds_{ihnmc__jcma}[i]\n')
            luolx__hzti += f"""    ensure_column_unboxed(py_table, arr_list_{ihnmc__jcma}, i, arr_ind_{ihnmc__jcma})
"""
            luolx__hzti += f"""    cpp_arr_list[out_arr_ind_{ihnmc__jcma}] = array_to_info(arr_list_{ihnmc__jcma}[i])
"""
        for moe__qfjm, koibh__cexs in cwsn__fxyju.items():
            if moe__qfjm < xxrer__smrcv:
                ihnmc__jcma = py_table.block_nums[moe__qfjm]
                obzit__fwoh = py_table.block_offsets[moe__qfjm]
                for sdpuz__xmjsw in koibh__cexs:
                    luolx__hzti += f"""  cpp_arr_list[{sdpuz__xmjsw}] = array_to_info(arr_list_{ihnmc__jcma}[{obzit__fwoh}])
"""
    for vxli__jnzrt in range(len(extra_arrs_tup)):
        nku__mecvb = jumm__svir.get(xxrer__smrcv + vxli__jnzrt, -1)
        if nku__mecvb != -1:
            jzja__pfx = [nku__mecvb] + cwsn__fxyju.get(xxrer__smrcv +
                vxli__jnzrt, [])
            for sdpuz__xmjsw in jzja__pfx:
                luolx__hzti += f"""  cpp_arr_list[{sdpuz__xmjsw}] = array_to_info(extra_arrs_tup[{vxli__jnzrt}])
"""
    luolx__hzti += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    dfbx__iuum.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    sau__ofjmm = {}
    exec(luolx__hzti, dfbx__iuum, sau__ofjmm)
    return sau__ofjmm['impl']


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
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='delete_table')
        builder.call(koq__kea, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='shuffle_table')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
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
        zqr__yyn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='delete_shuffle_info')
        return builder.call(koq__kea, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='reverse_shuffle_table')
        return builder.call(koq__kea, args)
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
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='hash_join_table')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
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
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='sort_values_table')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='sample_table')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='shuffle_renormalization')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='shuffle_renormalization_group')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='drop_duplicates_table')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
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
        zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        koq__kea = cgutils.get_or_insert_function(builder.module, zqr__yyn,
            name='groupby_and_aggregate')
        efv__rhut = builder.call(koq__kea, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return efv__rhut
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
    plzp__dduad = array_to_info(in_arr)
    xqta__pmkxx = array_to_info(in_values)
    tzutm__cshbw = array_to_info(out_arr)
    tzz__ppq = arr_info_list_to_table([plzp__dduad, xqta__pmkxx, tzutm__cshbw])
    _array_isin(tzutm__cshbw, plzp__dduad, xqta__pmkxx, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(tzz__ppq)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    plzp__dduad = array_to_info(in_arr)
    tzutm__cshbw = array_to_info(out_arr)
    _get_search_regex(plzp__dduad, case, match, pat, tzutm__cshbw)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    ijyip__zhd = col_array_typ.dtype
    if isinstance(ijyip__zhd, types.Number) or ijyip__zhd in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ujvlu__yxzgn, cpo__hlag = args
                ujvlu__yxzgn = builder.bitcast(ujvlu__yxzgn, lir.IntType(8)
                    .as_pointer().as_pointer())
                cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                fodd__qznqv = builder.load(builder.gep(ujvlu__yxzgn, [
                    cadse__potvs]))
                fodd__qznqv = builder.bitcast(fodd__qznqv, context.
                    get_data_type(ijyip__zhd).as_pointer())
                return builder.load(builder.gep(fodd__qznqv, [cpo__hlag]))
            return ijyip__zhd(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ujvlu__yxzgn, cpo__hlag = args
                ujvlu__yxzgn = builder.bitcast(ujvlu__yxzgn, lir.IntType(8)
                    .as_pointer().as_pointer())
                cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                fodd__qznqv = builder.load(builder.gep(ujvlu__yxzgn, [
                    cadse__potvs]))
                zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                fwsq__hhxx = cgutils.get_or_insert_function(builder.module,
                    zqr__yyn, name='array_info_getitem')
                zlo__bxdmt = cgutils.alloca_once(builder, lir.IntType(64))
                args = fodd__qznqv, cpo__hlag, zlo__bxdmt
                swmq__nubbc = builder.call(fwsq__hhxx, args)
                return context.make_tuple(builder, sig.return_type, [
                    swmq__nubbc, builder.load(zlo__bxdmt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                jtqu__qco = lir.Constant(lir.IntType(64), 1)
                pwl__dgmam = lir.Constant(lir.IntType(64), 2)
                ujvlu__yxzgn, cpo__hlag = args
                ujvlu__yxzgn = builder.bitcast(ujvlu__yxzgn, lir.IntType(8)
                    .as_pointer().as_pointer())
                cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                fodd__qznqv = builder.load(builder.gep(ujvlu__yxzgn, [
                    cadse__potvs]))
                zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64)])
                vywp__rhtia = cgutils.get_or_insert_function(builder.module,
                    zqr__yyn, name='get_nested_info')
                args = fodd__qznqv, pwl__dgmam
                tzfie__lhb = builder.call(vywp__rhtia, args)
                zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer()])
                nbla__jqw = cgutils.get_or_insert_function(builder.module,
                    zqr__yyn, name='array_info_getdata1')
                args = tzfie__lhb,
                jmn__ovou = builder.call(nbla__jqw, args)
                jmn__ovou = builder.bitcast(jmn__ovou, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                zxr__sug = builder.sext(builder.load(builder.gep(jmn__ovou,
                    [cpo__hlag])), lir.IntType(64))
                args = fodd__qznqv, jtqu__qco
                mgp__mpfl = builder.call(vywp__rhtia, args)
                zqr__yyn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                fwsq__hhxx = cgutils.get_or_insert_function(builder.module,
                    zqr__yyn, name='array_info_getitem')
                zlo__bxdmt = cgutils.alloca_once(builder, lir.IntType(64))
                args = mgp__mpfl, zxr__sug, zlo__bxdmt
                swmq__nubbc = builder.call(fwsq__hhxx, args)
                return context.make_tuple(builder, sig.return_type, [
                    swmq__nubbc, builder.load(zlo__bxdmt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{ijyip__zhd}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in (bodo.libs.bool_arr_ext.boolean_array, bodo
        .binary_array_type) or is_str_arr_type(col_array_dtype) or isinstance(
        col_array_dtype, types.Array
        ) and col_array_dtype.dtype == bodo.datetime_date_type:

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                uzz__wae, cpo__hlag = args
                uzz__wae = builder.bitcast(uzz__wae, lir.IntType(8).
                    as_pointer().as_pointer())
                cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                fodd__qznqv = builder.load(builder.gep(uzz__wae, [
                    cadse__potvs]))
                bpmnh__uawmx = builder.bitcast(fodd__qznqv, context.
                    get_data_type(types.bool_).as_pointer())
                qgz__zlmu = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    bpmnh__uawmx, cpo__hlag)
                xescc__flyzq = builder.icmp_unsigned('!=', qgz__zlmu, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(xescc__flyzq, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        ijyip__zhd = col_array_dtype.dtype
        if ijyip__zhd in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    ujvlu__yxzgn, cpo__hlag = args
                    ujvlu__yxzgn = builder.bitcast(ujvlu__yxzgn, lir.
                        IntType(8).as_pointer().as_pointer())
                    cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                    fodd__qznqv = builder.load(builder.gep(ujvlu__yxzgn, [
                        cadse__potvs]))
                    fodd__qznqv = builder.bitcast(fodd__qznqv, context.
                        get_data_type(ijyip__zhd).as_pointer())
                    vxrv__vkixv = builder.load(builder.gep(fodd__qznqv, [
                        cpo__hlag]))
                    xescc__flyzq = builder.icmp_unsigned('!=', vxrv__vkixv,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(xescc__flyzq, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(ijyip__zhd, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    ujvlu__yxzgn, cpo__hlag = args
                    ujvlu__yxzgn = builder.bitcast(ujvlu__yxzgn, lir.
                        IntType(8).as_pointer().as_pointer())
                    cadse__potvs = lir.Constant(lir.IntType(64), c_ind)
                    fodd__qznqv = builder.load(builder.gep(ujvlu__yxzgn, [
                        cadse__potvs]))
                    fodd__qznqv = builder.bitcast(fodd__qznqv, context.
                        get_data_type(ijyip__zhd).as_pointer())
                    vxrv__vkixv = builder.load(builder.gep(fodd__qznqv, [
                        cpo__hlag]))
                    vqc__lvb = signature(types.bool_, ijyip__zhd)
                    qgz__zlmu = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, vqc__lvb, (vxrv__vkixv,))
                    return builder.not_(builder.sext(qgz__zlmu, lir.IntType(8))
                        )
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
