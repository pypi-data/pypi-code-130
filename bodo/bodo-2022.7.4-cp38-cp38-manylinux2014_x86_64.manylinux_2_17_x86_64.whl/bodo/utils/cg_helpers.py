"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    iddd__seuz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    zpru__iyylx = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    idpw__eyyyf = builder.gep(null_bitmap_ptr, [iddd__seuz], inbounds=True)
    wqxej__nbo = builder.load(idpw__eyyyf)
    isryx__kuoad = lir.ArrayType(lir.IntType(8), 8)
    syl__qffk = cgutils.alloca_once_value(builder, lir.Constant(
        isryx__kuoad, (1, 2, 4, 8, 16, 32, 64, 128)))
    wid__gcs = builder.load(builder.gep(syl__qffk, [lir.Constant(lir.
        IntType(64), 0), zpru__iyylx], inbounds=True))
    if val:
        builder.store(builder.or_(wqxej__nbo, wid__gcs), idpw__eyyyf)
    else:
        wid__gcs = builder.xor(wid__gcs, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(wqxej__nbo, wid__gcs), idpw__eyyyf)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    iddd__seuz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    zpru__iyylx = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    wqxej__nbo = builder.load(builder.gep(null_bitmap_ptr, [iddd__seuz],
        inbounds=True))
    isryx__kuoad = lir.ArrayType(lir.IntType(8), 8)
    syl__qffk = cgutils.alloca_once_value(builder, lir.Constant(
        isryx__kuoad, (1, 2, 4, 8, 16, 32, 64, 128)))
    wid__gcs = builder.load(builder.gep(syl__qffk, [lir.Constant(lir.
        IntType(64), 0), zpru__iyylx], inbounds=True))
    return builder.and_(wqxej__nbo, wid__gcs)


def pyarray_check(builder, context, obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    zlquu__iuf = lir.FunctionType(lir.IntType(32), [avshh__cszls])
    kvo__flxan = cgutils.get_or_insert_function(builder.module, zlquu__iuf,
        name='is_np_array')
    return builder.call(kvo__flxan, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    avshh__cszls = context.get_argument_type(types.pyobject)
    obf__lyd = context.get_value_type(types.intp)
    afy__ylf = lir.FunctionType(lir.IntType(8).as_pointer(), [avshh__cszls,
        obf__lyd])
    slaq__xjg = cgutils.get_or_insert_function(builder.module, afy__ylf,
        name='array_getptr1')
    ndho__myhq = lir.FunctionType(avshh__cszls, [avshh__cszls, lir.IntType(
        8).as_pointer()])
    tpdem__gvtp = cgutils.get_or_insert_function(builder.module, ndho__myhq,
        name='array_getitem')
    qllhy__shwuu = builder.call(slaq__xjg, [arr_obj, ind])
    return builder.call(tpdem__gvtp, [arr_obj, qllhy__shwuu])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    obf__lyd = context.get_value_type(types.intp)
    afy__ylf = lir.FunctionType(lir.IntType(8).as_pointer(), [avshh__cszls,
        obf__lyd])
    slaq__xjg = cgutils.get_or_insert_function(builder.module, afy__ylf,
        name='array_getptr1')
    jhnq__lnxbk = lir.FunctionType(lir.VoidType(), [avshh__cszls, lir.
        IntType(8).as_pointer(), avshh__cszls])
    vocl__prqt = cgutils.get_or_insert_function(builder.module, jhnq__lnxbk,
        name='array_setitem')
    qllhy__shwuu = builder.call(slaq__xjg, [arr_obj, ind])
    builder.call(vocl__prqt, [arr_obj, qllhy__shwuu, val_obj])


def seq_getitem(builder, context, obj, ind):
    avshh__cszls = context.get_argument_type(types.pyobject)
    obf__lyd = context.get_value_type(types.intp)
    rsxl__hqd = lir.FunctionType(avshh__cszls, [avshh__cszls, obf__lyd])
    twnye__nuq = cgutils.get_or_insert_function(builder.module, rsxl__hqd,
        name='seq_getitem')
    return builder.call(twnye__nuq, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    avshh__cszls = context.get_argument_type(types.pyobject)
    ccj__irx = lir.FunctionType(lir.IntType(32), [avshh__cszls, avshh__cszls])
    gif__xsbc = cgutils.get_or_insert_function(builder.module, ccj__irx,
        name='is_na_value')
    return builder.call(gif__xsbc, [val, C_NA])


def list_check(builder, context, obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    zdez__kssda = context.get_value_type(types.int32)
    wlb__brc = lir.FunctionType(zdez__kssda, [avshh__cszls])
    idw__ddk = cgutils.get_or_insert_function(builder.module, wlb__brc,
        name='list_check')
    return builder.call(idw__ddk, [obj])


def dict_keys(builder, context, obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    wlb__brc = lir.FunctionType(avshh__cszls, [avshh__cszls])
    idw__ddk = cgutils.get_or_insert_function(builder.module, wlb__brc,
        name='dict_keys')
    return builder.call(idw__ddk, [obj])


def dict_values(builder, context, obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    wlb__brc = lir.FunctionType(avshh__cszls, [avshh__cszls])
    idw__ddk = cgutils.get_or_insert_function(builder.module, wlb__brc,
        name='dict_values')
    return builder.call(idw__ddk, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    avshh__cszls = context.get_argument_type(types.pyobject)
    wlb__brc = lir.FunctionType(lir.VoidType(), [avshh__cszls, avshh__cszls])
    idw__ddk = cgutils.get_or_insert_function(builder.module, wlb__brc,
        name='dict_merge_from_seq2')
    builder.call(idw__ddk, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    zmwau__wlw = cgutils.alloca_once_value(builder, val)
    xyfx__vqw = list_check(builder, context, val)
    tgkcx__fabc = builder.icmp_unsigned('!=', xyfx__vqw, lir.Constant(
        xyfx__vqw.type, 0))
    with builder.if_then(tgkcx__fabc):
        ercmy__wytk = context.insert_const_string(builder.module, 'numpy')
        ukuk__vbcsj = c.pyapi.import_module_noblock(ercmy__wytk)
        uzey__kiu = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            uzey__kiu = str(typ.dtype)
        skl__bzpue = c.pyapi.object_getattr_string(ukuk__vbcsj, uzey__kiu)
        rebcx__achu = builder.load(zmwau__wlw)
        bbzw__jovsx = c.pyapi.call_method(ukuk__vbcsj, 'asarray', (
            rebcx__achu, skl__bzpue))
        builder.store(bbzw__jovsx, zmwau__wlw)
        c.pyapi.decref(ukuk__vbcsj)
        c.pyapi.decref(skl__bzpue)
    val = builder.load(zmwau__wlw)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        nmlk__osc = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        yctwb__ghyaz, epr__adi = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [nmlk__osc])
        context.nrt.decref(builder, typ, nmlk__osc)
        return cgutils.pack_array(builder, [epr__adi])
    if isinstance(typ, (StructType, types.BaseTuple)):
        ercmy__wytk = context.insert_const_string(builder.module, 'pandas')
        sqixc__xht = c.pyapi.import_module_noblock(ercmy__wytk)
        C_NA = c.pyapi.object_getattr_string(sqixc__xht, 'NA')
        ynw__aodm = bodo.utils.transform.get_type_alloc_counts(typ)
        wkk__tbgz = context.make_tuple(builder, types.Tuple(ynw__aodm * [
            types.int64]), ynw__aodm * [context.get_constant(types.int64, 0)])
        tefl__jgdp = cgutils.alloca_once_value(builder, wkk__tbgz)
        bei__eekr = 0
        zofqu__vycil = typ.data if isinstance(typ, StructType) else typ.types
        for nqffn__yyup, t in enumerate(zofqu__vycil):
            epnl__gpa = bodo.utils.transform.get_type_alloc_counts(t)
            if epnl__gpa == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    nqffn__yyup])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, nqffn__yyup)
            wtj__pxwo = is_na_value(builder, context, val_obj, C_NA)
            vau__wyw = builder.icmp_unsigned('!=', wtj__pxwo, lir.Constant(
                wtj__pxwo.type, 1))
            with builder.if_then(vau__wyw):
                wkk__tbgz = builder.load(tefl__jgdp)
                ewk__djt = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for nqffn__yyup in range(epnl__gpa):
                    oif__qhqv = builder.extract_value(wkk__tbgz, bei__eekr +
                        nqffn__yyup)
                    orz__zpq = builder.extract_value(ewk__djt, nqffn__yyup)
                    wkk__tbgz = builder.insert_value(wkk__tbgz, builder.add
                        (oif__qhqv, orz__zpq), bei__eekr + nqffn__yyup)
                builder.store(wkk__tbgz, tefl__jgdp)
            bei__eekr += epnl__gpa
        c.pyapi.decref(sqixc__xht)
        c.pyapi.decref(C_NA)
        return builder.load(tefl__jgdp)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    ercmy__wytk = context.insert_const_string(builder.module, 'pandas')
    sqixc__xht = c.pyapi.import_module_noblock(ercmy__wytk)
    C_NA = c.pyapi.object_getattr_string(sqixc__xht, 'NA')
    ynw__aodm = bodo.utils.transform.get_type_alloc_counts(typ)
    wkk__tbgz = context.make_tuple(builder, types.Tuple(ynw__aodm * [types.
        int64]), [n] + (ynw__aodm - 1) * [context.get_constant(types.int64, 0)]
        )
    tefl__jgdp = cgutils.alloca_once_value(builder, wkk__tbgz)
    with cgutils.for_range(builder, n) as xun__fwqqk:
        jghrg__jaakk = xun__fwqqk.index
        uzgd__jqt = seq_getitem(builder, context, arr_obj, jghrg__jaakk)
        wtj__pxwo = is_na_value(builder, context, uzgd__jqt, C_NA)
        vau__wyw = builder.icmp_unsigned('!=', wtj__pxwo, lir.Constant(
            wtj__pxwo.type, 1))
        with builder.if_then(vau__wyw):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                wkk__tbgz = builder.load(tefl__jgdp)
                ewk__djt = get_array_elem_counts(c, builder, context,
                    uzgd__jqt, typ.dtype)
                for nqffn__yyup in range(ynw__aodm - 1):
                    oif__qhqv = builder.extract_value(wkk__tbgz, 
                        nqffn__yyup + 1)
                    orz__zpq = builder.extract_value(ewk__djt, nqffn__yyup)
                    wkk__tbgz = builder.insert_value(wkk__tbgz, builder.add
                        (oif__qhqv, orz__zpq), nqffn__yyup + 1)
                builder.store(wkk__tbgz, tefl__jgdp)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                bei__eekr = 1
                for nqffn__yyup, t in enumerate(typ.data):
                    epnl__gpa = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if epnl__gpa == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(uzgd__jqt, nqffn__yyup)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(uzgd__jqt,
                            typ.names[nqffn__yyup])
                    wtj__pxwo = is_na_value(builder, context, val_obj, C_NA)
                    vau__wyw = builder.icmp_unsigned('!=', wtj__pxwo, lir.
                        Constant(wtj__pxwo.type, 1))
                    with builder.if_then(vau__wyw):
                        wkk__tbgz = builder.load(tefl__jgdp)
                        ewk__djt = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for nqffn__yyup in range(epnl__gpa):
                            oif__qhqv = builder.extract_value(wkk__tbgz, 
                                bei__eekr + nqffn__yyup)
                            orz__zpq = builder.extract_value(ewk__djt,
                                nqffn__yyup)
                            wkk__tbgz = builder.insert_value(wkk__tbgz,
                                builder.add(oif__qhqv, orz__zpq), bei__eekr +
                                nqffn__yyup)
                        builder.store(wkk__tbgz, tefl__jgdp)
                    bei__eekr += epnl__gpa
            else:
                assert isinstance(typ, MapArrayType), typ
                wkk__tbgz = builder.load(tefl__jgdp)
                dnv__bwsbe = dict_keys(builder, context, uzgd__jqt)
                zpsz__qmxxe = dict_values(builder, context, uzgd__jqt)
                olh__lobz = get_array_elem_counts(c, builder, context,
                    dnv__bwsbe, typ.key_arr_type)
                apdtc__qdsum = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for nqffn__yyup in range(1, apdtc__qdsum + 1):
                    oif__qhqv = builder.extract_value(wkk__tbgz, nqffn__yyup)
                    orz__zpq = builder.extract_value(olh__lobz, nqffn__yyup - 1
                        )
                    wkk__tbgz = builder.insert_value(wkk__tbgz, builder.add
                        (oif__qhqv, orz__zpq), nqffn__yyup)
                dmuk__fvk = get_array_elem_counts(c, builder, context,
                    zpsz__qmxxe, typ.value_arr_type)
                for nqffn__yyup in range(apdtc__qdsum + 1, ynw__aodm):
                    oif__qhqv = builder.extract_value(wkk__tbgz, nqffn__yyup)
                    orz__zpq = builder.extract_value(dmuk__fvk, nqffn__yyup -
                        apdtc__qdsum)
                    wkk__tbgz = builder.insert_value(wkk__tbgz, builder.add
                        (oif__qhqv, orz__zpq), nqffn__yyup)
                builder.store(wkk__tbgz, tefl__jgdp)
                c.pyapi.decref(dnv__bwsbe)
                c.pyapi.decref(zpsz__qmxxe)
        c.pyapi.decref(uzgd__jqt)
    c.pyapi.decref(sqixc__xht)
    c.pyapi.decref(C_NA)
    return builder.load(tefl__jgdp)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    pza__coyud = n_elems.type.count
    assert pza__coyud >= 1
    tgt__pbuf = builder.extract_value(n_elems, 0)
    if pza__coyud != 1:
        tkhti__yha = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, nqffn__yyup) for nqffn__yyup in range(1, pza__coyud)])
        qve__axnpf = types.Tuple([types.int64] * (pza__coyud - 1))
    else:
        tkhti__yha = context.get_dummy_value()
        qve__axnpf = types.none
    jlu__brwbw = types.TypeRef(arr_type)
    luefu__ydpsg = arr_type(types.int64, jlu__brwbw, qve__axnpf)
    args = [tgt__pbuf, context.get_dummy_value(), tkhti__yha]
    uwlwj__bcv = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        yctwb__ghyaz, uckak__rawh = c.pyapi.call_jit_code(uwlwj__bcv,
            luefu__ydpsg, args)
    else:
        uckak__rawh = context.compile_internal(builder, uwlwj__bcv,
            luefu__ydpsg, args)
    return uckak__rawh


def is_ll_eq(builder, val1, val2):
    ezhw__hfa = val1.type.pointee
    zamzo__aje = val2.type.pointee
    assert ezhw__hfa == zamzo__aje, 'invalid llvm value comparison'
    if isinstance(ezhw__hfa, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(ezhw__hfa.elements) if isinstance(ezhw__hfa, lir.
            BaseStructType) else ezhw__hfa.count
        ydly__mxpc = lir.Constant(lir.IntType(1), 1)
        for nqffn__yyup in range(n_elems):
            gch__tmj = lir.IntType(32)(0)
            tbm__ljeyo = lir.IntType(32)(nqffn__yyup)
            cgnv__ndbr = builder.gep(val1, [gch__tmj, tbm__ljeyo], inbounds
                =True)
            gnif__rpy = builder.gep(val2, [gch__tmj, tbm__ljeyo], inbounds=True
                )
            ydly__mxpc = builder.and_(ydly__mxpc, is_ll_eq(builder,
                cgnv__ndbr, gnif__rpy))
        return ydly__mxpc
    nwwk__qdh = builder.load(val1)
    fktu__vfz = builder.load(val2)
    if nwwk__qdh.type in (lir.FloatType(), lir.DoubleType()):
        uayh__fbf = 32 if nwwk__qdh.type == lir.FloatType() else 64
        nwwk__qdh = builder.bitcast(nwwk__qdh, lir.IntType(uayh__fbf))
        fktu__vfz = builder.bitcast(fktu__vfz, lir.IntType(uayh__fbf))
    return builder.icmp_unsigned('==', nwwk__qdh, fktu__vfz)
