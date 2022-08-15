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
    fqqe__pqrdk = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    yrsoe__jyq = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    gjmi__uccqw = builder.gep(null_bitmap_ptr, [fqqe__pqrdk], inbounds=True)
    nkxyh__isi = builder.load(gjmi__uccqw)
    duhyn__zes = lir.ArrayType(lir.IntType(8), 8)
    ghirq__cra = cgutils.alloca_once_value(builder, lir.Constant(duhyn__zes,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    oum__nza = builder.load(builder.gep(ghirq__cra, [lir.Constant(lir.
        IntType(64), 0), yrsoe__jyq], inbounds=True))
    if val:
        builder.store(builder.or_(nkxyh__isi, oum__nza), gjmi__uccqw)
    else:
        oum__nza = builder.xor(oum__nza, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(nkxyh__isi, oum__nza), gjmi__uccqw)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    fqqe__pqrdk = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    yrsoe__jyq = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    nkxyh__isi = builder.load(builder.gep(null_bitmap_ptr, [fqqe__pqrdk],
        inbounds=True))
    duhyn__zes = lir.ArrayType(lir.IntType(8), 8)
    ghirq__cra = cgutils.alloca_once_value(builder, lir.Constant(duhyn__zes,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    oum__nza = builder.load(builder.gep(ghirq__cra, [lir.Constant(lir.
        IntType(64), 0), yrsoe__jyq], inbounds=True))
    return builder.and_(nkxyh__isi, oum__nza)


def pyarray_check(builder, context, obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    vwvh__bhcxn = lir.FunctionType(lir.IntType(32), [vwnvz__aorm])
    ypwk__ihrz = cgutils.get_or_insert_function(builder.module, vwvh__bhcxn,
        name='is_np_array')
    return builder.call(ypwk__ihrz, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    ayb__ytsx = context.get_value_type(types.intp)
    snv__bvd = lir.FunctionType(lir.IntType(8).as_pointer(), [vwnvz__aorm,
        ayb__ytsx])
    jkbbu__ruifm = cgutils.get_or_insert_function(builder.module, snv__bvd,
        name='array_getptr1')
    xbb__iygw = lir.FunctionType(vwnvz__aorm, [vwnvz__aorm, lir.IntType(8).
        as_pointer()])
    voxa__gxp = cgutils.get_or_insert_function(builder.module, xbb__iygw,
        name='array_getitem')
    vywik__hfti = builder.call(jkbbu__ruifm, [arr_obj, ind])
    return builder.call(voxa__gxp, [arr_obj, vywik__hfti])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    ayb__ytsx = context.get_value_type(types.intp)
    snv__bvd = lir.FunctionType(lir.IntType(8).as_pointer(), [vwnvz__aorm,
        ayb__ytsx])
    jkbbu__ruifm = cgutils.get_or_insert_function(builder.module, snv__bvd,
        name='array_getptr1')
    fae__zmgow = lir.FunctionType(lir.VoidType(), [vwnvz__aorm, lir.IntType
        (8).as_pointer(), vwnvz__aorm])
    xuv__axd = cgutils.get_or_insert_function(builder.module, fae__zmgow,
        name='array_setitem')
    vywik__hfti = builder.call(jkbbu__ruifm, [arr_obj, ind])
    builder.call(xuv__axd, [arr_obj, vywik__hfti, val_obj])


def seq_getitem(builder, context, obj, ind):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    ayb__ytsx = context.get_value_type(types.intp)
    qsed__jennw = lir.FunctionType(vwnvz__aorm, [vwnvz__aorm, ayb__ytsx])
    hcsi__zin = cgutils.get_or_insert_function(builder.module, qsed__jennw,
        name='seq_getitem')
    return builder.call(hcsi__zin, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    ubgbo__wlcs = lir.FunctionType(lir.IntType(32), [vwnvz__aorm, vwnvz__aorm])
    qox__dluaq = cgutils.get_or_insert_function(builder.module, ubgbo__wlcs,
        name='is_na_value')
    return builder.call(qox__dluaq, [val, C_NA])


def list_check(builder, context, obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    dwep__gscq = context.get_value_type(types.int32)
    dgahi__tmt = lir.FunctionType(dwep__gscq, [vwnvz__aorm])
    qrrd__myq = cgutils.get_or_insert_function(builder.module, dgahi__tmt,
        name='list_check')
    return builder.call(qrrd__myq, [obj])


def dict_keys(builder, context, obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    dgahi__tmt = lir.FunctionType(vwnvz__aorm, [vwnvz__aorm])
    qrrd__myq = cgutils.get_or_insert_function(builder.module, dgahi__tmt,
        name='dict_keys')
    return builder.call(qrrd__myq, [obj])


def dict_values(builder, context, obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    dgahi__tmt = lir.FunctionType(vwnvz__aorm, [vwnvz__aorm])
    qrrd__myq = cgutils.get_or_insert_function(builder.module, dgahi__tmt,
        name='dict_values')
    return builder.call(qrrd__myq, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    vwnvz__aorm = context.get_argument_type(types.pyobject)
    dgahi__tmt = lir.FunctionType(lir.VoidType(), [vwnvz__aorm, vwnvz__aorm])
    qrrd__myq = cgutils.get_or_insert_function(builder.module, dgahi__tmt,
        name='dict_merge_from_seq2')
    builder.call(qrrd__myq, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    mcj__xoo = cgutils.alloca_once_value(builder, val)
    rpcjy__wnwds = list_check(builder, context, val)
    hto__ldvkj = builder.icmp_unsigned('!=', rpcjy__wnwds, lir.Constant(
        rpcjy__wnwds.type, 0))
    with builder.if_then(hto__ldvkj):
        clrxz__xphvd = context.insert_const_string(builder.module, 'numpy')
        qodl__vgda = c.pyapi.import_module_noblock(clrxz__xphvd)
        tii__pqkl = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            tii__pqkl = str(typ.dtype)
        ysuin__eqzaf = c.pyapi.object_getattr_string(qodl__vgda, tii__pqkl)
        cnwdj__fff = builder.load(mcj__xoo)
        naap__buxir = c.pyapi.call_method(qodl__vgda, 'asarray', (
            cnwdj__fff, ysuin__eqzaf))
        builder.store(naap__buxir, mcj__xoo)
        c.pyapi.decref(qodl__vgda)
        c.pyapi.decref(ysuin__eqzaf)
    val = builder.load(mcj__xoo)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        pza__mtdy = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        esdl__fifx, rai__wqnwt = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [pza__mtdy])
        context.nrt.decref(builder, typ, pza__mtdy)
        return cgutils.pack_array(builder, [rai__wqnwt])
    if isinstance(typ, (StructType, types.BaseTuple)):
        clrxz__xphvd = context.insert_const_string(builder.module, 'pandas')
        cbxy__puy = c.pyapi.import_module_noblock(clrxz__xphvd)
        C_NA = c.pyapi.object_getattr_string(cbxy__puy, 'NA')
        sedf__zxk = bodo.utils.transform.get_type_alloc_counts(typ)
        iqzpm__koa = context.make_tuple(builder, types.Tuple(sedf__zxk * [
            types.int64]), sedf__zxk * [context.get_constant(types.int64, 0)])
        erx__qnrhc = cgutils.alloca_once_value(builder, iqzpm__koa)
        yko__rbfi = 0
        rgmf__xcmi = typ.data if isinstance(typ, StructType) else typ.types
        for hlou__jpd, t in enumerate(rgmf__xcmi):
            bjj__chy = bodo.utils.transform.get_type_alloc_counts(t)
            if bjj__chy == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    hlou__jpd])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, hlou__jpd)
            unfd__hgjri = is_na_value(builder, context, val_obj, C_NA)
            ogpg__yftdi = builder.icmp_unsigned('!=', unfd__hgjri, lir.
                Constant(unfd__hgjri.type, 1))
            with builder.if_then(ogpg__yftdi):
                iqzpm__koa = builder.load(erx__qnrhc)
                anxwq__vozlw = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for hlou__jpd in range(bjj__chy):
                    whp__yzx = builder.extract_value(iqzpm__koa, yko__rbfi +
                        hlou__jpd)
                    mbekf__hcog = builder.extract_value(anxwq__vozlw, hlou__jpd
                        )
                    iqzpm__koa = builder.insert_value(iqzpm__koa, builder.
                        add(whp__yzx, mbekf__hcog), yko__rbfi + hlou__jpd)
                builder.store(iqzpm__koa, erx__qnrhc)
            yko__rbfi += bjj__chy
        c.pyapi.decref(cbxy__puy)
        c.pyapi.decref(C_NA)
        return builder.load(erx__qnrhc)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    clrxz__xphvd = context.insert_const_string(builder.module, 'pandas')
    cbxy__puy = c.pyapi.import_module_noblock(clrxz__xphvd)
    C_NA = c.pyapi.object_getattr_string(cbxy__puy, 'NA')
    sedf__zxk = bodo.utils.transform.get_type_alloc_counts(typ)
    iqzpm__koa = context.make_tuple(builder, types.Tuple(sedf__zxk * [types
        .int64]), [n] + (sedf__zxk - 1) * [context.get_constant(types.int64,
        0)])
    erx__qnrhc = cgutils.alloca_once_value(builder, iqzpm__koa)
    with cgutils.for_range(builder, n) as dom__stxh:
        qkwqd__dsgvd = dom__stxh.index
        upt__rdyp = seq_getitem(builder, context, arr_obj, qkwqd__dsgvd)
        unfd__hgjri = is_na_value(builder, context, upt__rdyp, C_NA)
        ogpg__yftdi = builder.icmp_unsigned('!=', unfd__hgjri, lir.Constant
            (unfd__hgjri.type, 1))
        with builder.if_then(ogpg__yftdi):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                iqzpm__koa = builder.load(erx__qnrhc)
                anxwq__vozlw = get_array_elem_counts(c, builder, context,
                    upt__rdyp, typ.dtype)
                for hlou__jpd in range(sedf__zxk - 1):
                    whp__yzx = builder.extract_value(iqzpm__koa, hlou__jpd + 1)
                    mbekf__hcog = builder.extract_value(anxwq__vozlw, hlou__jpd
                        )
                    iqzpm__koa = builder.insert_value(iqzpm__koa, builder.
                        add(whp__yzx, mbekf__hcog), hlou__jpd + 1)
                builder.store(iqzpm__koa, erx__qnrhc)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                yko__rbfi = 1
                for hlou__jpd, t in enumerate(typ.data):
                    bjj__chy = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if bjj__chy == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(upt__rdyp, hlou__jpd)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(upt__rdyp,
                            typ.names[hlou__jpd])
                    unfd__hgjri = is_na_value(builder, context, val_obj, C_NA)
                    ogpg__yftdi = builder.icmp_unsigned('!=', unfd__hgjri,
                        lir.Constant(unfd__hgjri.type, 1))
                    with builder.if_then(ogpg__yftdi):
                        iqzpm__koa = builder.load(erx__qnrhc)
                        anxwq__vozlw = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for hlou__jpd in range(bjj__chy):
                            whp__yzx = builder.extract_value(iqzpm__koa, 
                                yko__rbfi + hlou__jpd)
                            mbekf__hcog = builder.extract_value(anxwq__vozlw,
                                hlou__jpd)
                            iqzpm__koa = builder.insert_value(iqzpm__koa,
                                builder.add(whp__yzx, mbekf__hcog), 
                                yko__rbfi + hlou__jpd)
                        builder.store(iqzpm__koa, erx__qnrhc)
                    yko__rbfi += bjj__chy
            else:
                assert isinstance(typ, MapArrayType), typ
                iqzpm__koa = builder.load(erx__qnrhc)
                tac__qvyhp = dict_keys(builder, context, upt__rdyp)
                rbpvg__drwd = dict_values(builder, context, upt__rdyp)
                ujayh__pkpqg = get_array_elem_counts(c, builder, context,
                    tac__qvyhp, typ.key_arr_type)
                xok__rwmd = bodo.utils.transform.get_type_alloc_counts(typ.
                    key_arr_type)
                for hlou__jpd in range(1, xok__rwmd + 1):
                    whp__yzx = builder.extract_value(iqzpm__koa, hlou__jpd)
                    mbekf__hcog = builder.extract_value(ujayh__pkpqg, 
                        hlou__jpd - 1)
                    iqzpm__koa = builder.insert_value(iqzpm__koa, builder.
                        add(whp__yzx, mbekf__hcog), hlou__jpd)
                mtjfq__vzeo = get_array_elem_counts(c, builder, context,
                    rbpvg__drwd, typ.value_arr_type)
                for hlou__jpd in range(xok__rwmd + 1, sedf__zxk):
                    whp__yzx = builder.extract_value(iqzpm__koa, hlou__jpd)
                    mbekf__hcog = builder.extract_value(mtjfq__vzeo, 
                        hlou__jpd - xok__rwmd)
                    iqzpm__koa = builder.insert_value(iqzpm__koa, builder.
                        add(whp__yzx, mbekf__hcog), hlou__jpd)
                builder.store(iqzpm__koa, erx__qnrhc)
                c.pyapi.decref(tac__qvyhp)
                c.pyapi.decref(rbpvg__drwd)
        c.pyapi.decref(upt__rdyp)
    c.pyapi.decref(cbxy__puy)
    c.pyapi.decref(C_NA)
    return builder.load(erx__qnrhc)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    wuq__ehqu = n_elems.type.count
    assert wuq__ehqu >= 1
    qtenv__nzcva = builder.extract_value(n_elems, 0)
    if wuq__ehqu != 1:
        dkulm__rcaa = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, hlou__jpd) for hlou__jpd in range(1, wuq__ehqu)])
        fvwjg__plzyx = types.Tuple([types.int64] * (wuq__ehqu - 1))
    else:
        dkulm__rcaa = context.get_dummy_value()
        fvwjg__plzyx = types.none
    tsbt__dymc = types.TypeRef(arr_type)
    mch__zpzo = arr_type(types.int64, tsbt__dymc, fvwjg__plzyx)
    args = [qtenv__nzcva, context.get_dummy_value(), dkulm__rcaa]
    tsc__yrpap = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        esdl__fifx, pea__terzy = c.pyapi.call_jit_code(tsc__yrpap,
            mch__zpzo, args)
    else:
        pea__terzy = context.compile_internal(builder, tsc__yrpap,
            mch__zpzo, args)
    return pea__terzy


def is_ll_eq(builder, val1, val2):
    kvy__gyx = val1.type.pointee
    nrjs__sdms = val2.type.pointee
    assert kvy__gyx == nrjs__sdms, 'invalid llvm value comparison'
    if isinstance(kvy__gyx, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(kvy__gyx.elements) if isinstance(kvy__gyx, lir.
            BaseStructType) else kvy__gyx.count
        yjcqn__axhwj = lir.Constant(lir.IntType(1), 1)
        for hlou__jpd in range(n_elems):
            hepz__wufzy = lir.IntType(32)(0)
            qwgwj__sssa = lir.IntType(32)(hlou__jpd)
            himnn__zhrgl = builder.gep(val1, [hepz__wufzy, qwgwj__sssa],
                inbounds=True)
            yxngf__icw = builder.gep(val2, [hepz__wufzy, qwgwj__sssa],
                inbounds=True)
            yjcqn__axhwj = builder.and_(yjcqn__axhwj, is_ll_eq(builder,
                himnn__zhrgl, yxngf__icw))
        return yjcqn__axhwj
    htf__wyyrv = builder.load(val1)
    nlija__otkl = builder.load(val2)
    if htf__wyyrv.type in (lir.FloatType(), lir.DoubleType()):
        sal__sscd = 32 if htf__wyyrv.type == lir.FloatType() else 64
        htf__wyyrv = builder.bitcast(htf__wyyrv, lir.IntType(sal__sscd))
        nlija__otkl = builder.bitcast(nlija__otkl, lir.IntType(sal__sscd))
    return builder.icmp_unsigned('==', htf__wyyrv, nlija__otkl)
