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
        qrh__jujgg = context.make_helper(builder, arr_type, in_arr)
        in_arr = qrh__jujgg.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        hwa__wapjn = context.make_helper(builder, arr_type, in_arr)
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='list_string_array_to_info')
        return builder.call(guqz__kcplh, [hwa__wapjn.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                fscs__duomq = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for exgdj__vfzw in arr_typ.data:
                    fscs__duomq += get_types(exgdj__vfzw)
                return fscs__duomq
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
            qkqs__fft = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                lzc__njfs = context.make_helper(builder, arr_typ, value=arr)
                mlu__etrw = get_lengths(_get_map_arr_data_type(arr_typ),
                    lzc__njfs.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                mhhpt__jyzrn = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                mlu__etrw = get_lengths(arr_typ.dtype, mhhpt__jyzrn.data)
                mlu__etrw = cgutils.pack_array(builder, [mhhpt__jyzrn.
                    n_arrays] + [builder.extract_value(mlu__etrw, zjcr__lvn
                    ) for zjcr__lvn in range(mlu__etrw.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                mhhpt__jyzrn = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                mlu__etrw = []
                for zjcr__lvn, exgdj__vfzw in enumerate(arr_typ.data):
                    cjj__dvjyz = get_lengths(exgdj__vfzw, builder.
                        extract_value(mhhpt__jyzrn.data, zjcr__lvn))
                    mlu__etrw += [builder.extract_value(cjj__dvjyz,
                        ostub__cbya) for ostub__cbya in range(cjj__dvjyz.
                        type.count)]
                mlu__etrw = cgutils.pack_array(builder, [qkqs__fft, context
                    .get_constant(types.int64, -1)] + mlu__etrw)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                mlu__etrw = cgutils.pack_array(builder, [qkqs__fft])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return mlu__etrw

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                lzc__njfs = context.make_helper(builder, arr_typ, value=arr)
                rxw__apf = get_buffers(_get_map_arr_data_type(arr_typ),
                    lzc__njfs.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                mhhpt__jyzrn = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                yqd__xoxaf = get_buffers(arr_typ.dtype, mhhpt__jyzrn.data)
                aary__ljf = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, mhhpt__jyzrn.offsets)
                qyq__xazew = builder.bitcast(aary__ljf.data, lir.IntType(8)
                    .as_pointer())
                mzm__twu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, mhhpt__jyzrn.null_bitmap)
                rquh__szghd = builder.bitcast(mzm__twu.data, lir.IntType(8)
                    .as_pointer())
                rxw__apf = cgutils.pack_array(builder, [qyq__xazew,
                    rquh__szghd] + [builder.extract_value(yqd__xoxaf,
                    zjcr__lvn) for zjcr__lvn in range(yqd__xoxaf.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                mhhpt__jyzrn = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                yqd__xoxaf = []
                for zjcr__lvn, exgdj__vfzw in enumerate(arr_typ.data):
                    gvy__pif = get_buffers(exgdj__vfzw, builder.
                        extract_value(mhhpt__jyzrn.data, zjcr__lvn))
                    yqd__xoxaf += [builder.extract_value(gvy__pif,
                        ostub__cbya) for ostub__cbya in range(gvy__pif.type
                        .count)]
                mzm__twu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, mhhpt__jyzrn.null_bitmap)
                rquh__szghd = builder.bitcast(mzm__twu.data, lir.IntType(8)
                    .as_pointer())
                rxw__apf = cgutils.pack_array(builder, [rquh__szghd] +
                    yqd__xoxaf)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                rqjim__srxu = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    rqjim__srxu = int128_type
                elif arr_typ == datetime_date_array_type:
                    rqjim__srxu = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                ssq__qgpk = context.make_array(types.Array(rqjim__srxu, 1, 'C')
                    )(context, builder, arr.data)
                mzm__twu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                jsx__uhpua = builder.bitcast(ssq__qgpk.data, lir.IntType(8)
                    .as_pointer())
                rquh__szghd = builder.bitcast(mzm__twu.data, lir.IntType(8)
                    .as_pointer())
                rxw__apf = cgutils.pack_array(builder, [rquh__szghd,
                    jsx__uhpua])
            elif arr_typ in (string_array_type, binary_array_type):
                mhhpt__jyzrn = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                dwo__grr = context.make_helper(builder, offset_arr_type,
                    mhhpt__jyzrn.offsets).data
                soay__lmfa = context.make_helper(builder, char_arr_type,
                    mhhpt__jyzrn.data).data
                svi__mtqo = context.make_helper(builder,
                    null_bitmap_arr_type, mhhpt__jyzrn.null_bitmap).data
                rxw__apf = cgutils.pack_array(builder, [builder.bitcast(
                    dwo__grr, lir.IntType(8).as_pointer()), builder.bitcast
                    (svi__mtqo, lir.IntType(8).as_pointer()), builder.
                    bitcast(soay__lmfa, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                jsx__uhpua = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                thlqu__kuw = lir.Constant(lir.IntType(8).as_pointer(), None)
                rxw__apf = cgutils.pack_array(builder, [thlqu__kuw, jsx__uhpua]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return rxw__apf

        def get_field_names(arr_typ):
            eru__lna = []
            if isinstance(arr_typ, StructArrayType):
                for aitz__mryub, ndlv__bxs in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    eru__lna.append(aitz__mryub)
                    eru__lna += get_field_names(ndlv__bxs)
            elif isinstance(arr_typ, ArrayItemArrayType):
                eru__lna += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                eru__lna += get_field_names(_get_map_arr_data_type(arr_typ))
            return eru__lna
        fscs__duomq = get_types(arr_type)
        rkfh__bxogd = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in fscs__duomq])
        xgomq__ith = cgutils.alloca_once_value(builder, rkfh__bxogd)
        mlu__etrw = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, mlu__etrw)
        rxw__apf = get_buffers(arr_type, in_arr)
        uei__cutr = cgutils.alloca_once_value(builder, rxw__apf)
        eru__lna = get_field_names(arr_type)
        if len(eru__lna) == 0:
            eru__lna = ['irrelevant']
        qnaa__kvt = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in eru__lna])
        kdumt__xsqyi = cgutils.alloca_once_value(builder, qnaa__kvt)
        if isinstance(arr_type, MapArrayType):
            azl__dowi = _get_map_arr_data_type(arr_type)
            uoo__zeu = context.make_helper(builder, arr_type, value=in_arr)
            poa__sgflf = uoo__zeu.data
        else:
            azl__dowi = arr_type
            poa__sgflf = in_arr
        slalz__rxg = context.make_helper(builder, azl__dowi, poa__sgflf)
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='nested_array_to_info')
        hltdo__erd = builder.call(guqz__kcplh, [builder.bitcast(xgomq__ith,
            lir.IntType(32).as_pointer()), builder.bitcast(uei__cutr, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            kdumt__xsqyi, lir.IntType(8).as_pointer()), slalz__rxg.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
    if arr_type in (string_array_type, binary_array_type):
        tfclu__ibhb = context.make_helper(builder, arr_type, in_arr)
        fuao__iqr = ArrayItemArrayType(char_arr_type)
        hwa__wapjn = context.make_helper(builder, fuao__iqr, tfclu__ibhb.data)
        mhhpt__jyzrn = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        dwo__grr = context.make_helper(builder, offset_arr_type,
            mhhpt__jyzrn.offsets).data
        soay__lmfa = context.make_helper(builder, char_arr_type,
            mhhpt__jyzrn.data).data
        svi__mtqo = context.make_helper(builder, null_bitmap_arr_type,
            mhhpt__jyzrn.null_bitmap).data
        tncmo__fzwtj = builder.zext(builder.load(builder.gep(dwo__grr, [
            mhhpt__jyzrn.n_arrays])), lir.IntType(64))
        xcvc__qyo = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='string_array_to_info')
        return builder.call(guqz__kcplh, [mhhpt__jyzrn.n_arrays,
            tncmo__fzwtj, soay__lmfa, dwo__grr, svi__mtqo, hwa__wapjn.
            meminfo, xcvc__qyo])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        sqjwe__rmwx = arr.data
        vdj__qxv = arr.indices
        sig = array_info_type(arr_type.data)
        pfh__gxagz = array_to_info_codegen(context, builder, sig, (
            sqjwe__rmwx,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        vhv__xdkzn = array_to_info_codegen(context, builder, sig, (vdj__qxv
            ,), False)
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(32)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='dict_str_array_to_info')
        blkn__icns = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(guqz__kcplh, [pfh__gxagz, vhv__xdkzn, blkn__icns])
    suuw__wsp = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        psf__tlqjk = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        zfnke__lyhw = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(zfnke__lyhw, 1, 'C')
        suuw__wsp = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if suuw__wsp:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        qkqs__fft = builder.extract_value(arr.shape, 0)
        wicz__grp = arr_type.dtype
        cka__rczmt = numba_to_c_type(wicz__grp)
        ijf__lnf = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), cka__rczmt))
        if suuw__wsp:
            cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            guqz__kcplh = cgutils.get_or_insert_function(builder.module,
                cmms__zwa, name='categorical_array_to_info')
            return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ijf__lnf), psf__tlqjk, arr.meminfo])
        else:
            cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            guqz__kcplh = cgutils.get_or_insert_function(builder.module,
                cmms__zwa, name='numpy_array_to_info')
            return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ijf__lnf), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType, TimeArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        wicz__grp = arr_type.dtype
        rqjim__srxu = wicz__grp
        if isinstance(arr_type, DecimalArrayType):
            rqjim__srxu = int128_type
        if arr_type == datetime_date_array_type:
            rqjim__srxu = types.int64
        ssq__qgpk = context.make_array(types.Array(rqjim__srxu, 1, 'C'))(
            context, builder, arr.data)
        qkqs__fft = builder.extract_value(ssq__qgpk.shape, 0)
        vafbb__ioyox = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        cka__rczmt = numba_to_c_type(wicz__grp)
        ijf__lnf = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), cka__rczmt))
        if isinstance(arr_type, DecimalArrayType):
            cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            guqz__kcplh = cgutils.get_or_insert_function(builder.module,
                cmms__zwa, name='decimal_array_to_info')
            return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
                ssq__qgpk.data, lir.IntType(8).as_pointer()), builder.load(
                ijf__lnf), builder.bitcast(vafbb__ioyox.data, lir.IntType(8
                ).as_pointer()), ssq__qgpk.meminfo, vafbb__ioyox.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        elif isinstance(arr_type, TimeArrayType):
            cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32)])
            guqz__kcplh = cgutils.get_or_insert_function(builder.module,
                cmms__zwa, name='time_array_to_info')
            return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
                ssq__qgpk.data, lir.IntType(8).as_pointer()), builder.load(
                ijf__lnf), builder.bitcast(vafbb__ioyox.data, lir.IntType(8
                ).as_pointer()), ssq__qgpk.meminfo, vafbb__ioyox.meminfo,
                lir.Constant(lir.IntType(32), arr_type.precision)])
        else:
            cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            guqz__kcplh = cgutils.get_or_insert_function(builder.module,
                cmms__zwa, name='nullable_array_to_info')
            return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
                ssq__qgpk.data, lir.IntType(8).as_pointer()), builder.load(
                ijf__lnf), builder.bitcast(vafbb__ioyox.data, lir.IntType(8
                ).as_pointer()), ssq__qgpk.meminfo, vafbb__ioyox.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        hnx__yaew = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        jmjx__yoh = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        qkqs__fft = builder.extract_value(hnx__yaew.shape, 0)
        cka__rczmt = numba_to_c_type(arr_type.arr_type.dtype)
        ijf__lnf = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), cka__rczmt))
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='interval_array_to_info')
        return builder.call(guqz__kcplh, [qkqs__fft, builder.bitcast(
            hnx__yaew.data, lir.IntType(8).as_pointer()), builder.bitcast(
            jmjx__yoh.data, lir.IntType(8).as_pointer()), builder.load(
            ijf__lnf), hnx__yaew.meminfo, jmjx__yoh.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    bde__uka = cgutils.alloca_once(builder, lir.IntType(64))
    jsx__uhpua = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    qpzby__uitfl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer(), lir.IntType(8).as_pointer().
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    guqz__kcplh = cgutils.get_or_insert_function(builder.module, cmms__zwa,
        name='info_to_numpy_array')
    builder.call(guqz__kcplh, [in_info, bde__uka, jsx__uhpua, qpzby__uitfl])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    ddejp__dzdnn = context.get_value_type(types.intp)
    otnqi__xuybe = cgutils.pack_array(builder, [builder.load(bde__uka)], ty
        =ddejp__dzdnn)
    jciox__yvsty = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    tat__amu = cgutils.pack_array(builder, [jciox__yvsty], ty=ddejp__dzdnn)
    soay__lmfa = builder.bitcast(builder.load(jsx__uhpua), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=soay__lmfa, shape=
        otnqi__xuybe, strides=tat__amu, itemsize=jciox__yvsty, meminfo=
        builder.load(qpzby__uitfl))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    xaxxf__pohay = context.make_helper(builder, arr_type)
    cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(8).as_pointer().as_pointer()])
    guqz__kcplh = cgutils.get_or_insert_function(builder.module, cmms__zwa,
        name='info_to_list_string_array')
    builder.call(guqz__kcplh, [in_info, xaxxf__pohay._get_ptr_by_name(
        'meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return xaxxf__pohay._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    vnvd__gtkky = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        bnng__xwjy = lengths_pos
        pnqzf__epzg = infos_pos
        tjqd__zeto, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        ijca__irn = ArrayItemArrayPayloadType(arr_typ)
        qlcl__zxoir = context.get_data_type(ijca__irn)
        jfx__vtsu = context.get_abi_sizeof(qlcl__zxoir)
        cbt__hde = define_array_item_dtor(context, builder, arr_typ, ijca__irn)
        wowz__rlezp = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, jfx__vtsu), cbt__hde)
        xoi__vhsd = context.nrt.meminfo_data(builder, wowz__rlezp)
        mhph__nboz = builder.bitcast(xoi__vhsd, qlcl__zxoir.as_pointer())
        mhhpt__jyzrn = cgutils.create_struct_proxy(ijca__irn)(context, builder)
        mhhpt__jyzrn.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), bnng__xwjy)
        mhhpt__jyzrn.data = tjqd__zeto
        qxy__gmcad = builder.load(array_infos_ptr)
        cgo__lhaa = builder.bitcast(builder.extract_value(qxy__gmcad,
            pnqzf__epzg), vnvd__gtkky)
        mhhpt__jyzrn.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, cgo__lhaa)
        llzp__ihof = builder.bitcast(builder.extract_value(qxy__gmcad, 
            pnqzf__epzg + 1), vnvd__gtkky)
        mhhpt__jyzrn.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, llzp__ihof)
        builder.store(mhhpt__jyzrn._getvalue(), mhph__nboz)
        hwa__wapjn = context.make_helper(builder, arr_typ)
        hwa__wapjn.meminfo = wowz__rlezp
        return hwa__wapjn._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        nybpe__ppo = []
        pnqzf__epzg = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for oqz__ydgp in arr_typ.data:
            tjqd__zeto, lengths_pos, infos_pos = nested_to_array(context,
                builder, oqz__ydgp, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            nybpe__ppo.append(tjqd__zeto)
        ijca__irn = StructArrayPayloadType(arr_typ.data)
        qlcl__zxoir = context.get_value_type(ijca__irn)
        jfx__vtsu = context.get_abi_sizeof(qlcl__zxoir)
        cbt__hde = define_struct_arr_dtor(context, builder, arr_typ, ijca__irn)
        wowz__rlezp = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, jfx__vtsu), cbt__hde)
        xoi__vhsd = context.nrt.meminfo_data(builder, wowz__rlezp)
        mhph__nboz = builder.bitcast(xoi__vhsd, qlcl__zxoir.as_pointer())
        mhhpt__jyzrn = cgutils.create_struct_proxy(ijca__irn)(context, builder)
        mhhpt__jyzrn.data = cgutils.pack_array(builder, nybpe__ppo
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, nybpe__ppo)
        qxy__gmcad = builder.load(array_infos_ptr)
        llzp__ihof = builder.bitcast(builder.extract_value(qxy__gmcad,
            pnqzf__epzg), vnvd__gtkky)
        mhhpt__jyzrn.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, llzp__ihof)
        builder.store(mhhpt__jyzrn._getvalue(), mhph__nboz)
        wahxz__rudu = context.make_helper(builder, arr_typ)
        wahxz__rudu.meminfo = wowz__rlezp
        return wahxz__rudu._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        qxy__gmcad = builder.load(array_infos_ptr)
        amat__ctzby = builder.bitcast(builder.extract_value(qxy__gmcad,
            infos_pos), vnvd__gtkky)
        tfclu__ibhb = context.make_helper(builder, arr_typ)
        fuao__iqr = ArrayItemArrayType(char_arr_type)
        hwa__wapjn = context.make_helper(builder, fuao__iqr)
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_to_string_array')
        builder.call(guqz__kcplh, [amat__ctzby, hwa__wapjn._get_ptr_by_name
            ('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        tfclu__ibhb.data = hwa__wapjn._getvalue()
        return tfclu__ibhb._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        qxy__gmcad = builder.load(array_infos_ptr)
        zmpad__vgl = builder.bitcast(builder.extract_value(qxy__gmcad, 
            infos_pos + 1), vnvd__gtkky)
        return _lower_info_to_array_numpy(arr_typ, context, builder, zmpad__vgl
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        rqjim__srxu = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            rqjim__srxu = int128_type
        elif arr_typ == datetime_date_array_type:
            rqjim__srxu = types.int64
        qxy__gmcad = builder.load(array_infos_ptr)
        llzp__ihof = builder.bitcast(builder.extract_value(qxy__gmcad,
            infos_pos), vnvd__gtkky)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, llzp__ihof)
        zmpad__vgl = builder.bitcast(builder.extract_value(qxy__gmcad, 
            infos_pos + 1), vnvd__gtkky)
        arr.data = _lower_info_to_array_numpy(types.Array(rqjim__srxu, 1,
            'C'), context, builder, zmpad__vgl)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, luz__yrr = args
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
                return 1 + sum([get_num_arrays(oqz__ydgp) for oqz__ydgp in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(oqz__ydgp) for oqz__ydgp in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            yyes__hxqgn = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            yyes__hxqgn = _get_map_arr_data_type(arr_type)
        else:
            yyes__hxqgn = arr_type
        ufdx__ywmar = get_num_arrays(yyes__hxqgn)
        mlu__etrw = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for luz__yrr in range(ufdx__ywmar)])
        lengths_ptr = cgutils.alloca_once_value(builder, mlu__etrw)
        thlqu__kuw = lir.Constant(lir.IntType(8).as_pointer(), None)
        begf__kogq = cgutils.pack_array(builder, [thlqu__kuw for luz__yrr in
            range(get_num_infos(yyes__hxqgn))])
        array_infos_ptr = cgutils.alloca_once_value(builder, begf__kogq)
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_to_nested_array')
        builder.call(guqz__kcplh, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, luz__yrr, luz__yrr = nested_to_array(context, builder,
            yyes__hxqgn, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            qrh__jujgg = context.make_helper(builder, arr_type)
            qrh__jujgg.data = arr
            context.nrt.incref(builder, yyes__hxqgn, arr)
            arr = qrh__jujgg._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, yyes__hxqgn)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        tfclu__ibhb = context.make_helper(builder, arr_type)
        fuao__iqr = ArrayItemArrayType(char_arr_type)
        hwa__wapjn = context.make_helper(builder, fuao__iqr)
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_to_string_array')
        builder.call(guqz__kcplh, [in_info, hwa__wapjn._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        tfclu__ibhb.data = hwa__wapjn._getvalue()
        return tfclu__ibhb._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='get_nested_info')
        pfh__gxagz = builder.call(guqz__kcplh, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        vhv__xdkzn = builder.call(guqz__kcplh, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        jlj__vyip = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        jlj__vyip.data = info_to_array_codegen(context, builder, sig, (
            pfh__gxagz, context.get_constant_null(arr_type.data)))
        cmka__fyd = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = cmka__fyd(array_info_type, cmka__fyd)
        jlj__vyip.indices = info_to_array_codegen(context, builder, sig, (
            vhv__xdkzn, context.get_constant_null(cmka__fyd)))
        cmms__zwa = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='get_has_global_dictionary')
        blkn__icns = builder.call(guqz__kcplh, [in_info])
        jlj__vyip.has_global_dictionary = builder.trunc(blkn__icns, cgutils
            .bool_t)
        return jlj__vyip._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zfnke__lyhw = get_categories_int_type(arr_type.dtype)
        fxsed__tjstj = types.Array(zfnke__lyhw, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(fxsed__tjstj, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            smcst__wquj = bodo.utils.utils.create_categorical_type(arr_type
                .dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(smcst__wquj))
            int_type = arr_type.dtype.int_type
            xnl__edd = arr_type.dtype.data.data
            kkny__qxfz = context.get_constant_generic(builder, xnl__edd,
                smcst__wquj)
            wicz__grp = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(xnl__edd), [kkny__qxfz])
        else:
            wicz__grp = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, wicz__grp)
        out_arr.dtype = wicz__grp
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        soay__lmfa = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = soay__lmfa
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType, TimeArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        rqjim__srxu = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            rqjim__srxu = int128_type
        elif arr_type == datetime_date_array_type:
            rqjim__srxu = types.int64
        umqqj__echui = types.Array(rqjim__srxu, 1, 'C')
        ssq__qgpk = context.make_array(umqqj__echui)(context, builder)
        bkel__tspy = types.Array(types.uint8, 1, 'C')
        vbuna__vddvu = context.make_array(bkel__tspy)(context, builder)
        bde__uka = cgutils.alloca_once(builder, lir.IntType(64))
        njl__pqh = cgutils.alloca_once(builder, lir.IntType(64))
        jsx__uhpua = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ymjaa__asxzv = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        qpzby__uitfl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        gys__ajgk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_to_nullable_array')
        builder.call(guqz__kcplh, [in_info, bde__uka, njl__pqh, jsx__uhpua,
            ymjaa__asxzv, qpzby__uitfl, gys__ajgk])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ddejp__dzdnn = context.get_value_type(types.intp)
        otnqi__xuybe = cgutils.pack_array(builder, [builder.load(bde__uka)],
            ty=ddejp__dzdnn)
        jciox__yvsty = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(rqjim__srxu)))
        tat__amu = cgutils.pack_array(builder, [jciox__yvsty], ty=ddejp__dzdnn)
        soay__lmfa = builder.bitcast(builder.load(jsx__uhpua), context.
            get_data_type(rqjim__srxu).as_pointer())
        numba.np.arrayobj.populate_array(ssq__qgpk, data=soay__lmfa, shape=
            otnqi__xuybe, strides=tat__amu, itemsize=jciox__yvsty, meminfo=
            builder.load(qpzby__uitfl))
        arr.data = ssq__qgpk._getvalue()
        otnqi__xuybe = cgutils.pack_array(builder, [builder.load(njl__pqh)],
            ty=ddejp__dzdnn)
        jciox__yvsty = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        tat__amu = cgutils.pack_array(builder, [jciox__yvsty], ty=ddejp__dzdnn)
        soay__lmfa = builder.bitcast(builder.load(ymjaa__asxzv), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(vbuna__vddvu, data=soay__lmfa,
            shape=otnqi__xuybe, strides=tat__amu, itemsize=jciox__yvsty,
            meminfo=builder.load(gys__ajgk))
        arr.null_bitmap = vbuna__vddvu._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        hnx__yaew = context.make_array(arr_type.arr_type)(context, builder)
        jmjx__yoh = context.make_array(arr_type.arr_type)(context, builder)
        bde__uka = cgutils.alloca_once(builder, lir.IntType(64))
        oyv__obu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ltiq__bpis = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        scf__mxbqk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        buirs__llj = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_to_interval_array')
        builder.call(guqz__kcplh, [in_info, bde__uka, oyv__obu, ltiq__bpis,
            scf__mxbqk, buirs__llj])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ddejp__dzdnn = context.get_value_type(types.intp)
        otnqi__xuybe = cgutils.pack_array(builder, [builder.load(bde__uka)],
            ty=ddejp__dzdnn)
        jciox__yvsty = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        tat__amu = cgutils.pack_array(builder, [jciox__yvsty], ty=ddejp__dzdnn)
        fsnwp__kezl = builder.bitcast(builder.load(oyv__obu), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(hnx__yaew, data=fsnwp__kezl, shape
            =otnqi__xuybe, strides=tat__amu, itemsize=jciox__yvsty, meminfo
            =builder.load(scf__mxbqk))
        arr.left = hnx__yaew._getvalue()
        ewoll__gss = builder.bitcast(builder.load(ltiq__bpis), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(jmjx__yoh, data=ewoll__gss, shape=
            otnqi__xuybe, strides=tat__amu, itemsize=jciox__yvsty, meminfo=
            builder.load(buirs__llj))
        arr.right = jmjx__yoh._getvalue()
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
        qkqs__fft, luz__yrr = args
        cka__rczmt = numba_to_c_type(array_type.dtype)
        ijf__lnf = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), cka__rczmt))
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='alloc_numpy')
        return builder.call(guqz__kcplh, [qkqs__fft, builder.load(ijf__lnf)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        qkqs__fft, pbgiy__aznry = args
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='alloc_string_array')
        return builder.call(guqz__kcplh, [qkqs__fft, pbgiy__aznry])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    rss__sia, = args
    smwb__kpxr = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], rss__sia)
    cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer().as_pointer(), lir.IntType(64)])
    guqz__kcplh = cgutils.get_or_insert_function(builder.module, cmms__zwa,
        name='arr_info_list_to_table')
    return builder.call(guqz__kcplh, [smwb__kpxr.data, smwb__kpxr.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_from_table')
        return builder.call(guqz__kcplh, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    ztgy__itd = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, luwc__fdiz, luz__yrr = args
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='info_from_table')
        yuq__qqddm = cgutils.create_struct_proxy(ztgy__itd)(context, builder)
        yuq__qqddm.parent = cgutils.get_null_value(yuq__qqddm.parent.type)
        umff__dzuo = context.make_array(table_idx_arr_t)(context, builder,
            luwc__fdiz)
        htooa__geugj = context.get_constant(types.int64, -1)
        yobdc__byyvw = context.get_constant(types.int64, 0)
        vdag__pshct = cgutils.alloca_once_value(builder, yobdc__byyvw)
        for t, soqkv__wbv in ztgy__itd.type_to_blk.items():
            pst__bawq = context.get_constant(types.int64, len(ztgy__itd.
                block_to_arr_ind[soqkv__wbv]))
            luz__yrr, tpp__hkqnz = ListInstance.allocate_ex(context,
                builder, types.List(t), pst__bawq)
            tpp__hkqnz.size = pst__bawq
            gpmg__yis = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(ztgy__itd.block_to_arr_ind[
                soqkv__wbv], dtype=np.int64))
            reptr__nye = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, gpmg__yis)
            with cgutils.for_range(builder, pst__bawq) as xmw__brpjg:
                zjcr__lvn = xmw__brpjg.index
                sjo__tjp = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    reptr__nye, zjcr__lvn)
                vptnn__qht = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, umff__dzuo, sjo__tjp)
                ita__spzy = builder.icmp_unsigned('!=', vptnn__qht,
                    htooa__geugj)
                with builder.if_else(ita__spzy) as (aps__xyul, dmpgg__behrj):
                    with aps__xyul:
                        renk__rhgr = builder.call(guqz__kcplh, [cpp_table,
                            vptnn__qht])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            renk__rhgr])
                        tpp__hkqnz.inititem(zjcr__lvn, arr, incref=False)
                        qkqs__fft = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(qkqs__fft, vdag__pshct)
                    with dmpgg__behrj:
                        kxfyx__dlkkk = context.get_constant_null(t)
                        tpp__hkqnz.inititem(zjcr__lvn, kxfyx__dlkkk, incref
                            =False)
            setattr(yuq__qqddm, f'block_{soqkv__wbv}', tpp__hkqnz.value)
        yuq__qqddm.len = builder.load(vdag__pshct)
        return yuq__qqddm._getvalue()
    return ztgy__itd(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    fjfgu__nwp = out_col_inds_t.instance_type.meta
    ztgy__itd = unwrap_typeref(out_types_t.types[0])
    nufdn__wxhu = [unwrap_typeref(out_types_t.types[zjcr__lvn]) for
        zjcr__lvn in range(1, len(out_types_t.types))]
    cued__uhdp = {}
    aiaq__lfmww = get_overload_const_int(n_table_cols_t)
    kumw__xfepx = {mwkk__mrew: zjcr__lvn for zjcr__lvn, mwkk__mrew in
        enumerate(fjfgu__nwp)}
    if not is_overload_none(unknown_cat_arrs_t):
        fndyy__knjgy = {plc__fdeps: zjcr__lvn for zjcr__lvn, plc__fdeps in
            enumerate(cat_inds_t.instance_type.meta)}
    xyh__dirbu = []
    bon__iqpda = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(ztgy__itd, bodo.TableType):
        bon__iqpda += f'  py_table = init_table(py_table_type, False)\n'
        bon__iqpda += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for wyz__fwpjp, soqkv__wbv in ztgy__itd.type_to_blk.items():
            pka__fjtw = [kumw__xfepx.get(zjcr__lvn, -1) for zjcr__lvn in
                ztgy__itd.block_to_arr_ind[soqkv__wbv]]
            cued__uhdp[f'out_inds_{soqkv__wbv}'] = np.array(pka__fjtw, np.int64
                )
            cued__uhdp[f'out_type_{soqkv__wbv}'] = wyz__fwpjp
            cued__uhdp[f'typ_list_{soqkv__wbv}'] = types.List(wyz__fwpjp)
            foxxa__dyqph = f'out_type_{soqkv__wbv}'
            if type_has_unknown_cats(wyz__fwpjp):
                if is_overload_none(unknown_cat_arrs_t):
                    bon__iqpda += f"""  in_arr_list_{soqkv__wbv} = get_table_block(out_types_t[0], {soqkv__wbv})
"""
                    foxxa__dyqph = f'in_arr_list_{soqkv__wbv}[i]'
                else:
                    cued__uhdp[f'cat_arr_inds_{soqkv__wbv}'] = np.array([
                        fndyy__knjgy.get(zjcr__lvn, -1) for zjcr__lvn in
                        ztgy__itd.block_to_arr_ind[soqkv__wbv]], np.int64)
                    foxxa__dyqph = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{soqkv__wbv}[i]]')
            pst__bawq = len(ztgy__itd.block_to_arr_ind[soqkv__wbv])
            bon__iqpda += f"""  arr_list_{soqkv__wbv} = alloc_list_like(typ_list_{soqkv__wbv}, {pst__bawq}, False)
"""
            bon__iqpda += f'  for i in range(len(arr_list_{soqkv__wbv})):\n'
            bon__iqpda += (
                f'    cpp_ind_{soqkv__wbv} = out_inds_{soqkv__wbv}[i]\n')
            bon__iqpda += f'    if cpp_ind_{soqkv__wbv} == -1:\n'
            bon__iqpda += f'      continue\n'
            bon__iqpda += f"""    arr_{soqkv__wbv} = info_to_array(info_from_table(cpp_table, cpp_ind_{soqkv__wbv}), {foxxa__dyqph})
"""
            bon__iqpda += f'    arr_list_{soqkv__wbv}[i] = arr_{soqkv__wbv}\n'
            bon__iqpda += f"""  py_table = set_table_block(py_table, arr_list_{soqkv__wbv}, {soqkv__wbv})
"""
        xyh__dirbu.append('py_table')
    elif ztgy__itd != types.none:
        hcq__yui = kumw__xfepx.get(0, -1)
        if hcq__yui != -1:
            cued__uhdp[f'arr_typ_arg0'] = ztgy__itd
            foxxa__dyqph = f'arr_typ_arg0'
            if type_has_unknown_cats(ztgy__itd):
                if is_overload_none(unknown_cat_arrs_t):
                    foxxa__dyqph = f'out_types_t[0]'
                else:
                    foxxa__dyqph = f'unknown_cat_arrs_t[{fndyy__knjgy[0]}]'
            bon__iqpda += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {hcq__yui}), {foxxa__dyqph})
"""
            xyh__dirbu.append('out_arg0')
    for zjcr__lvn, t in enumerate(nufdn__wxhu):
        hcq__yui = kumw__xfepx.get(aiaq__lfmww + zjcr__lvn, -1)
        if hcq__yui != -1:
            cued__uhdp[f'extra_arr_type_{zjcr__lvn}'] = t
            foxxa__dyqph = f'extra_arr_type_{zjcr__lvn}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    foxxa__dyqph = f'out_types_t[{zjcr__lvn + 1}]'
                else:
                    foxxa__dyqph = (
                        f'unknown_cat_arrs_t[{fndyy__knjgy[aiaq__lfmww + zjcr__lvn]}]'
                        )
            bon__iqpda += f"""  out_{zjcr__lvn} = info_to_array(info_from_table(cpp_table, {hcq__yui}), {foxxa__dyqph})
"""
            xyh__dirbu.append(f'out_{zjcr__lvn}')
    mlp__obzxy = ',' if len(xyh__dirbu) == 1 else ''
    bon__iqpda += f"  return ({', '.join(xyh__dirbu)}{mlp__obzxy})\n"
    cued__uhdp.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(fjfgu__nwp), 'py_table_type': ztgy__itd})
    bsu__jdh = {}
    exec(bon__iqpda, cued__uhdp, bsu__jdh)
    return bsu__jdh['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    ztgy__itd = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, luz__yrr = args
        mmw__bipq = cgutils.create_struct_proxy(ztgy__itd)(context, builder,
            py_table)
        if ztgy__itd.has_runtime_cols:
            igidd__nby = lir.Constant(lir.IntType(64), 0)
            for soqkv__wbv, t in enumerate(ztgy__itd.arr_types):
                ajdgl__riiq = getattr(mmw__bipq, f'block_{soqkv__wbv}')
                vcnis__jgzjv = ListInstance(context, builder, types.List(t),
                    ajdgl__riiq)
                igidd__nby = builder.add(igidd__nby, vcnis__jgzjv.size)
        else:
            igidd__nby = lir.Constant(lir.IntType(64), len(ztgy__itd.arr_types)
                )
        luz__yrr, jvc__ikvcl = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), igidd__nby)
        jvc__ikvcl.size = igidd__nby
        if ztgy__itd.has_runtime_cols:
            bvl__htwm = lir.Constant(lir.IntType(64), 0)
            for soqkv__wbv, t in enumerate(ztgy__itd.arr_types):
                ajdgl__riiq = getattr(mmw__bipq, f'block_{soqkv__wbv}')
                vcnis__jgzjv = ListInstance(context, builder, types.List(t),
                    ajdgl__riiq)
                pst__bawq = vcnis__jgzjv.size
                with cgutils.for_range(builder, pst__bawq) as xmw__brpjg:
                    zjcr__lvn = xmw__brpjg.index
                    arr = vcnis__jgzjv.getitem(zjcr__lvn)
                    mowrh__qkvyr = signature(array_info_type, t)
                    mqlsm__dmbo = arr,
                    kzjl__olv = array_to_info_codegen(context, builder,
                        mowrh__qkvyr, mqlsm__dmbo)
                    jvc__ikvcl.inititem(builder.add(bvl__htwm, zjcr__lvn),
                        kzjl__olv, incref=False)
                bvl__htwm = builder.add(bvl__htwm, pst__bawq)
        else:
            for t, soqkv__wbv in ztgy__itd.type_to_blk.items():
                pst__bawq = context.get_constant(types.int64, len(ztgy__itd
                    .block_to_arr_ind[soqkv__wbv]))
                ajdgl__riiq = getattr(mmw__bipq, f'block_{soqkv__wbv}')
                vcnis__jgzjv = ListInstance(context, builder, types.List(t),
                    ajdgl__riiq)
                gpmg__yis = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(ztgy__itd.
                    block_to_arr_ind[soqkv__wbv], dtype=np.int64))
                reptr__nye = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, gpmg__yis)
                with cgutils.for_range(builder, pst__bawq) as xmw__brpjg:
                    zjcr__lvn = xmw__brpjg.index
                    sjo__tjp = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        reptr__nye, zjcr__lvn)
                    iyylj__xstgf = signature(types.none, ztgy__itd, types.
                        List(t), types.int64, types.int64)
                    yusx__ogm = py_table, ajdgl__riiq, zjcr__lvn, sjo__tjp
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, iyylj__xstgf, yusx__ogm)
                    arr = vcnis__jgzjv.getitem(zjcr__lvn)
                    mowrh__qkvyr = signature(array_info_type, t)
                    mqlsm__dmbo = arr,
                    kzjl__olv = array_to_info_codegen(context, builder,
                        mowrh__qkvyr, mqlsm__dmbo)
                    jvc__ikvcl.inititem(sjo__tjp, kzjl__olv, incref=False)
        yhmu__tiwak = jvc__ikvcl.value
        ttj__bjz = signature(table_type, types.List(array_info_type))
        kvno__ogt = yhmu__tiwak,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            ttj__bjz, kvno__ogt)
        context.nrt.decref(builder, types.List(array_info_type), yhmu__tiwak)
        return cpp_table
    return table_type(ztgy__itd, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    xhlu__vpsz = in_col_inds_t.instance_type.meta
    cued__uhdp = {}
    aiaq__lfmww = get_overload_const_int(n_table_cols_t)
    pzlx__rwm = defaultdict(list)
    kumw__xfepx = {}
    for zjcr__lvn, mwkk__mrew in enumerate(xhlu__vpsz):
        if mwkk__mrew in kumw__xfepx:
            pzlx__rwm[mwkk__mrew].append(zjcr__lvn)
        else:
            kumw__xfepx[mwkk__mrew] = zjcr__lvn
    bon__iqpda = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    bon__iqpda += (
        f'  cpp_arr_list = alloc_empty_list_type({len(xhlu__vpsz)}, array_info_type)\n'
        )
    if py_table != types.none:
        for soqkv__wbv in py_table.type_to_blk.values():
            pka__fjtw = [kumw__xfepx.get(zjcr__lvn, -1) for zjcr__lvn in
                py_table.block_to_arr_ind[soqkv__wbv]]
            cued__uhdp[f'out_inds_{soqkv__wbv}'] = np.array(pka__fjtw, np.int64
                )
            cued__uhdp[f'arr_inds_{soqkv__wbv}'] = np.array(py_table.
                block_to_arr_ind[soqkv__wbv], np.int64)
            bon__iqpda += (
                f'  arr_list_{soqkv__wbv} = get_table_block(py_table, {soqkv__wbv})\n'
                )
            bon__iqpda += f'  for i in range(len(arr_list_{soqkv__wbv})):\n'
            bon__iqpda += (
                f'    out_arr_ind_{soqkv__wbv} = out_inds_{soqkv__wbv}[i]\n')
            bon__iqpda += f'    if out_arr_ind_{soqkv__wbv} == -1:\n'
            bon__iqpda += f'      continue\n'
            bon__iqpda += (
                f'    arr_ind_{soqkv__wbv} = arr_inds_{soqkv__wbv}[i]\n')
            bon__iqpda += f"""    ensure_column_unboxed(py_table, arr_list_{soqkv__wbv}, i, arr_ind_{soqkv__wbv})
"""
            bon__iqpda += f"""    cpp_arr_list[out_arr_ind_{soqkv__wbv}] = array_to_info(arr_list_{soqkv__wbv}[i])
"""
        for ekny__vpzh, asw__tkzz in pzlx__rwm.items():
            if ekny__vpzh < aiaq__lfmww:
                soqkv__wbv = py_table.block_nums[ekny__vpzh]
                kuoo__hnt = py_table.block_offsets[ekny__vpzh]
                for hcq__yui in asw__tkzz:
                    bon__iqpda += f"""  cpp_arr_list[{hcq__yui}] = array_to_info(arr_list_{soqkv__wbv}[{kuoo__hnt}])
"""
    for zjcr__lvn in range(len(extra_arrs_tup)):
        qmxpa__wag = kumw__xfepx.get(aiaq__lfmww + zjcr__lvn, -1)
        if qmxpa__wag != -1:
            wqits__zgltr = [qmxpa__wag] + pzlx__rwm.get(aiaq__lfmww +
                zjcr__lvn, [])
            for hcq__yui in wqits__zgltr:
                bon__iqpda += f"""  cpp_arr_list[{hcq__yui}] = array_to_info(extra_arrs_tup[{zjcr__lvn}])
"""
    bon__iqpda += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    cued__uhdp.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    bsu__jdh = {}
    exec(bon__iqpda, cued__uhdp, bsu__jdh)
    return bsu__jdh['impl']


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
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='delete_table')
        builder.call(guqz__kcplh, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='shuffle_table')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
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
        cmms__zwa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='delete_shuffle_info')
        return builder.call(guqz__kcplh, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='reverse_shuffle_table')
        return builder.call(guqz__kcplh, args)
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
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='hash_join_table')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
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
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='sort_values_table')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='sample_table')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='shuffle_renormalization')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='shuffle_renormalization_group')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='drop_duplicates_table')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
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
        cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        guqz__kcplh = cgutils.get_or_insert_function(builder.module,
            cmms__zwa, name='groupby_and_aggregate')
        hltdo__erd = builder.call(guqz__kcplh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hltdo__erd
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
    psqlm__whqy = array_to_info(in_arr)
    nrjz__oep = array_to_info(in_values)
    kxrjt__sbpa = array_to_info(out_arr)
    biohr__pjgem = arr_info_list_to_table([psqlm__whqy, nrjz__oep, kxrjt__sbpa]
        )
    _array_isin(kxrjt__sbpa, psqlm__whqy, nrjz__oep, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(biohr__pjgem)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    psqlm__whqy = array_to_info(in_arr)
    kxrjt__sbpa = array_to_info(out_arr)
    _get_search_regex(psqlm__whqy, case, match, pat, kxrjt__sbpa)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    eewv__oflp = col_array_typ.dtype
    if isinstance(eewv__oflp, (types.Number, TimeType)) or eewv__oflp in [bodo
        .datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                yuq__qqddm, dhwot__xlt = args
                yuq__qqddm = builder.bitcast(yuq__qqddm, lir.IntType(8).
                    as_pointer().as_pointer())
                azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                nxrrr__dvd = builder.load(builder.gep(yuq__qqddm, [azbq__mmmy])
                    )
                nxrrr__dvd = builder.bitcast(nxrrr__dvd, context.
                    get_data_type(eewv__oflp).as_pointer())
                return builder.load(builder.gep(nxrrr__dvd, [dhwot__xlt]))
            return eewv__oflp(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                yuq__qqddm, dhwot__xlt = args
                yuq__qqddm = builder.bitcast(yuq__qqddm, lir.IntType(8).
                    as_pointer().as_pointer())
                azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                nxrrr__dvd = builder.load(builder.gep(yuq__qqddm, [azbq__mmmy])
                    )
                cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dpgg__jxop = cgutils.get_or_insert_function(builder.module,
                    cmms__zwa, name='array_info_getitem')
                wpoal__fbt = cgutils.alloca_once(builder, lir.IntType(64))
                args = nxrrr__dvd, dhwot__xlt, wpoal__fbt
                jsx__uhpua = builder.call(dpgg__jxop, args)
                return context.make_tuple(builder, sig.return_type, [
                    jsx__uhpua, builder.load(wpoal__fbt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hzra__seiy = lir.Constant(lir.IntType(64), 1)
                pkj__skshz = lir.Constant(lir.IntType(64), 2)
                yuq__qqddm, dhwot__xlt = args
                yuq__qqddm = builder.bitcast(yuq__qqddm, lir.IntType(8).
                    as_pointer().as_pointer())
                azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                nxrrr__dvd = builder.load(builder.gep(yuq__qqddm, [azbq__mmmy])
                    )
                cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64)])
                pexz__atw = cgutils.get_or_insert_function(builder.module,
                    cmms__zwa, name='get_nested_info')
                args = nxrrr__dvd, pkj__skshz
                vrmx__miz = builder.call(pexz__atw, args)
                cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer()])
                kqus__jzrpk = cgutils.get_or_insert_function(builder.module,
                    cmms__zwa, name='array_info_getdata1')
                args = vrmx__miz,
                rdcmv__loz = builder.call(kqus__jzrpk, args)
                rdcmv__loz = builder.bitcast(rdcmv__loz, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                qdpxz__dxdk = builder.sext(builder.load(builder.gep(
                    rdcmv__loz, [dhwot__xlt])), lir.IntType(64))
                args = nxrrr__dvd, hzra__seiy
                rsy__vjppj = builder.call(pexz__atw, args)
                cmms__zwa = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dpgg__jxop = cgutils.get_or_insert_function(builder.module,
                    cmms__zwa, name='array_info_getitem')
                wpoal__fbt = cgutils.alloca_once(builder, lir.IntType(64))
                args = rsy__vjppj, qdpxz__dxdk, wpoal__fbt
                jsx__uhpua = builder.call(dpgg__jxop, args)
                return context.make_tuple(builder, sig.return_type, [
                    jsx__uhpua, builder.load(wpoal__fbt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{eewv__oflp}' column data type not supported"
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
                ieqky__xkat, dhwot__xlt = args
                ieqky__xkat = builder.bitcast(ieqky__xkat, lir.IntType(8).
                    as_pointer().as_pointer())
                azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                nxrrr__dvd = builder.load(builder.gep(ieqky__xkat, [
                    azbq__mmmy]))
                svi__mtqo = builder.bitcast(nxrrr__dvd, context.
                    get_data_type(types.bool_).as_pointer())
                fers__nakdk = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    svi__mtqo, dhwot__xlt)
                ogex__zdl = builder.icmp_unsigned('!=', fers__nakdk, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(ogex__zdl, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        eewv__oflp = col_array_dtype.dtype
        if eewv__oflp in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    yuq__qqddm, dhwot__xlt = args
                    yuq__qqddm = builder.bitcast(yuq__qqddm, lir.IntType(8)
                        .as_pointer().as_pointer())
                    azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                    nxrrr__dvd = builder.load(builder.gep(yuq__qqddm, [
                        azbq__mmmy]))
                    nxrrr__dvd = builder.bitcast(nxrrr__dvd, context.
                        get_data_type(eewv__oflp).as_pointer())
                    kqggl__tgw = builder.load(builder.gep(nxrrr__dvd, [
                        dhwot__xlt]))
                    ogex__zdl = builder.icmp_unsigned('!=', kqggl__tgw, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(ogex__zdl, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(eewv__oflp, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    yuq__qqddm, dhwot__xlt = args
                    yuq__qqddm = builder.bitcast(yuq__qqddm, lir.IntType(8)
                        .as_pointer().as_pointer())
                    azbq__mmmy = lir.Constant(lir.IntType(64), c_ind)
                    nxrrr__dvd = builder.load(builder.gep(yuq__qqddm, [
                        azbq__mmmy]))
                    nxrrr__dvd = builder.bitcast(nxrrr__dvd, context.
                        get_data_type(eewv__oflp).as_pointer())
                    kqggl__tgw = builder.load(builder.gep(nxrrr__dvd, [
                        dhwot__xlt]))
                    fqobv__xvjkf = signature(types.bool_, eewv__oflp)
                    fers__nakdk = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, fqobv__xvjkf, (kqggl__tgw,))
                    return builder.not_(builder.sext(fers__nakdk, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
