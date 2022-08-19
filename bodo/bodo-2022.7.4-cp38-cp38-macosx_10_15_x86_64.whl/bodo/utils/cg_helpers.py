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
    steji__eeosd = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    kvbd__fiphu = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    gesii__ibr = builder.gep(null_bitmap_ptr, [steji__eeosd], inbounds=True)
    vxgzy__dkhh = builder.load(gesii__ibr)
    vuqqk__fzfdj = lir.ArrayType(lir.IntType(8), 8)
    oidx__veib = cgutils.alloca_once_value(builder, lir.Constant(
        vuqqk__fzfdj, (1, 2, 4, 8, 16, 32, 64, 128)))
    iqumz__ccjn = builder.load(builder.gep(oidx__veib, [lir.Constant(lir.
        IntType(64), 0), kvbd__fiphu], inbounds=True))
    if val:
        builder.store(builder.or_(vxgzy__dkhh, iqumz__ccjn), gesii__ibr)
    else:
        iqumz__ccjn = builder.xor(iqumz__ccjn, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(vxgzy__dkhh, iqumz__ccjn), gesii__ibr)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    steji__eeosd = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    kvbd__fiphu = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    vxgzy__dkhh = builder.load(builder.gep(null_bitmap_ptr, [steji__eeosd],
        inbounds=True))
    vuqqk__fzfdj = lir.ArrayType(lir.IntType(8), 8)
    oidx__veib = cgutils.alloca_once_value(builder, lir.Constant(
        vuqqk__fzfdj, (1, 2, 4, 8, 16, 32, 64, 128)))
    iqumz__ccjn = builder.load(builder.gep(oidx__veib, [lir.Constant(lir.
        IntType(64), 0), kvbd__fiphu], inbounds=True))
    return builder.and_(vxgzy__dkhh, iqumz__ccjn)


def pyarray_check(builder, context, obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    nlr__vkga = lir.FunctionType(lir.IntType(32), [ldbc__rjny])
    zkg__fsxa = cgutils.get_or_insert_function(builder.module, nlr__vkga,
        name='is_np_array')
    return builder.call(zkg__fsxa, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    zba__kov = context.get_value_type(types.intp)
    wyu__cac = lir.FunctionType(lir.IntType(8).as_pointer(), [ldbc__rjny,
        zba__kov])
    wdiz__zvq = cgutils.get_or_insert_function(builder.module, wyu__cac,
        name='array_getptr1')
    fzu__iohun = lir.FunctionType(ldbc__rjny, [ldbc__rjny, lir.IntType(8).
        as_pointer()])
    rmoj__cmmz = cgutils.get_or_insert_function(builder.module, fzu__iohun,
        name='array_getitem')
    yenlb__cks = builder.call(wdiz__zvq, [arr_obj, ind])
    return builder.call(rmoj__cmmz, [arr_obj, yenlb__cks])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    zba__kov = context.get_value_type(types.intp)
    wyu__cac = lir.FunctionType(lir.IntType(8).as_pointer(), [ldbc__rjny,
        zba__kov])
    wdiz__zvq = cgutils.get_or_insert_function(builder.module, wyu__cac,
        name='array_getptr1')
    msw__qxywr = lir.FunctionType(lir.VoidType(), [ldbc__rjny, lir.IntType(
        8).as_pointer(), ldbc__rjny])
    osv__hqqu = cgutils.get_or_insert_function(builder.module, msw__qxywr,
        name='array_setitem')
    yenlb__cks = builder.call(wdiz__zvq, [arr_obj, ind])
    builder.call(osv__hqqu, [arr_obj, yenlb__cks, val_obj])


def seq_getitem(builder, context, obj, ind):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    zba__kov = context.get_value_type(types.intp)
    qrok__riblu = lir.FunctionType(ldbc__rjny, [ldbc__rjny, zba__kov])
    cpbto__mdqor = cgutils.get_or_insert_function(builder.module,
        qrok__riblu, name='seq_getitem')
    return builder.call(cpbto__mdqor, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    vnghs__ndyz = lir.FunctionType(lir.IntType(32), [ldbc__rjny, ldbc__rjny])
    zltkm__ezwi = cgutils.get_or_insert_function(builder.module,
        vnghs__ndyz, name='is_na_value')
    return builder.call(zltkm__ezwi, [val, C_NA])


def list_check(builder, context, obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    oshkq__tjz = context.get_value_type(types.int32)
    jxj__wxm = lir.FunctionType(oshkq__tjz, [ldbc__rjny])
    rlx__inlgm = cgutils.get_or_insert_function(builder.module, jxj__wxm,
        name='list_check')
    return builder.call(rlx__inlgm, [obj])


def dict_keys(builder, context, obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    jxj__wxm = lir.FunctionType(ldbc__rjny, [ldbc__rjny])
    rlx__inlgm = cgutils.get_or_insert_function(builder.module, jxj__wxm,
        name='dict_keys')
    return builder.call(rlx__inlgm, [obj])


def dict_values(builder, context, obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    jxj__wxm = lir.FunctionType(ldbc__rjny, [ldbc__rjny])
    rlx__inlgm = cgutils.get_or_insert_function(builder.module, jxj__wxm,
        name='dict_values')
    return builder.call(rlx__inlgm, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    ldbc__rjny = context.get_argument_type(types.pyobject)
    jxj__wxm = lir.FunctionType(lir.VoidType(), [ldbc__rjny, ldbc__rjny])
    rlx__inlgm = cgutils.get_or_insert_function(builder.module, jxj__wxm,
        name='dict_merge_from_seq2')
    builder.call(rlx__inlgm, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    nhhq__yhlc = cgutils.alloca_once_value(builder, val)
    ygj__amp = list_check(builder, context, val)
    aissu__gawz = builder.icmp_unsigned('!=', ygj__amp, lir.Constant(
        ygj__amp.type, 0))
    with builder.if_then(aissu__gawz):
        sza__ytyr = context.insert_const_string(builder.module, 'numpy')
        ttbxz__jcdt = c.pyapi.import_module_noblock(sza__ytyr)
        idv__fokh = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            idv__fokh = str(typ.dtype)
        dyc__ocr = c.pyapi.object_getattr_string(ttbxz__jcdt, idv__fokh)
        euwru__hjigd = builder.load(nhhq__yhlc)
        mtfnw__uyry = c.pyapi.call_method(ttbxz__jcdt, 'asarray', (
            euwru__hjigd, dyc__ocr))
        builder.store(mtfnw__uyry, nhhq__yhlc)
        c.pyapi.decref(ttbxz__jcdt)
        c.pyapi.decref(dyc__ocr)
    val = builder.load(nhhq__yhlc)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        ccr__pig = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        irp__hwin, smuzo__papj = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [ccr__pig])
        context.nrt.decref(builder, typ, ccr__pig)
        return cgutils.pack_array(builder, [smuzo__papj])
    if isinstance(typ, (StructType, types.BaseTuple)):
        sza__ytyr = context.insert_const_string(builder.module, 'pandas')
        lghjc__nfnh = c.pyapi.import_module_noblock(sza__ytyr)
        C_NA = c.pyapi.object_getattr_string(lghjc__nfnh, 'NA')
        yhavw__bfb = bodo.utils.transform.get_type_alloc_counts(typ)
        gel__ulnu = context.make_tuple(builder, types.Tuple(yhavw__bfb * [
            types.int64]), yhavw__bfb * [context.get_constant(types.int64, 0)])
        kpoyl__symqa = cgutils.alloca_once_value(builder, gel__ulnu)
        heqvg__xsy = 0
        lznqf__vnc = typ.data if isinstance(typ, StructType) else typ.types
        for leaen__pxbtg, t in enumerate(lznqf__vnc):
            empb__zdcel = bodo.utils.transform.get_type_alloc_counts(t)
            if empb__zdcel == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    leaen__pxbtg])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, leaen__pxbtg)
            dsft__usck = is_na_value(builder, context, val_obj, C_NA)
            rca__jmix = builder.icmp_unsigned('!=', dsft__usck, lir.
                Constant(dsft__usck.type, 1))
            with builder.if_then(rca__jmix):
                gel__ulnu = builder.load(kpoyl__symqa)
                hgt__zwi = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for leaen__pxbtg in range(empb__zdcel):
                    kvky__apd = builder.extract_value(gel__ulnu, heqvg__xsy +
                        leaen__pxbtg)
                    khfx__hwtz = builder.extract_value(hgt__zwi, leaen__pxbtg)
                    gel__ulnu = builder.insert_value(gel__ulnu, builder.add
                        (kvky__apd, khfx__hwtz), heqvg__xsy + leaen__pxbtg)
                builder.store(gel__ulnu, kpoyl__symqa)
            heqvg__xsy += empb__zdcel
        c.pyapi.decref(lghjc__nfnh)
        c.pyapi.decref(C_NA)
        return builder.load(kpoyl__symqa)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    sza__ytyr = context.insert_const_string(builder.module, 'pandas')
    lghjc__nfnh = c.pyapi.import_module_noblock(sza__ytyr)
    C_NA = c.pyapi.object_getattr_string(lghjc__nfnh, 'NA')
    yhavw__bfb = bodo.utils.transform.get_type_alloc_counts(typ)
    gel__ulnu = context.make_tuple(builder, types.Tuple(yhavw__bfb * [types
        .int64]), [n] + (yhavw__bfb - 1) * [context.get_constant(types.
        int64, 0)])
    kpoyl__symqa = cgutils.alloca_once_value(builder, gel__ulnu)
    with cgutils.for_range(builder, n) as bfqb__ixzd:
        lkq__zgqoc = bfqb__ixzd.index
        qwj__zeohc = seq_getitem(builder, context, arr_obj, lkq__zgqoc)
        dsft__usck = is_na_value(builder, context, qwj__zeohc, C_NA)
        rca__jmix = builder.icmp_unsigned('!=', dsft__usck, lir.Constant(
            dsft__usck.type, 1))
        with builder.if_then(rca__jmix):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                gel__ulnu = builder.load(kpoyl__symqa)
                hgt__zwi = get_array_elem_counts(c, builder, context,
                    qwj__zeohc, typ.dtype)
                for leaen__pxbtg in range(yhavw__bfb - 1):
                    kvky__apd = builder.extract_value(gel__ulnu, 
                        leaen__pxbtg + 1)
                    khfx__hwtz = builder.extract_value(hgt__zwi, leaen__pxbtg)
                    gel__ulnu = builder.insert_value(gel__ulnu, builder.add
                        (kvky__apd, khfx__hwtz), leaen__pxbtg + 1)
                builder.store(gel__ulnu, kpoyl__symqa)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                heqvg__xsy = 1
                for leaen__pxbtg, t in enumerate(typ.data):
                    empb__zdcel = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if empb__zdcel == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(qwj__zeohc,
                            leaen__pxbtg)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(qwj__zeohc,
                            typ.names[leaen__pxbtg])
                    dsft__usck = is_na_value(builder, context, val_obj, C_NA)
                    rca__jmix = builder.icmp_unsigned('!=', dsft__usck, lir
                        .Constant(dsft__usck.type, 1))
                    with builder.if_then(rca__jmix):
                        gel__ulnu = builder.load(kpoyl__symqa)
                        hgt__zwi = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for leaen__pxbtg in range(empb__zdcel):
                            kvky__apd = builder.extract_value(gel__ulnu, 
                                heqvg__xsy + leaen__pxbtg)
                            khfx__hwtz = builder.extract_value(hgt__zwi,
                                leaen__pxbtg)
                            gel__ulnu = builder.insert_value(gel__ulnu,
                                builder.add(kvky__apd, khfx__hwtz), 
                                heqvg__xsy + leaen__pxbtg)
                        builder.store(gel__ulnu, kpoyl__symqa)
                    heqvg__xsy += empb__zdcel
            else:
                assert isinstance(typ, MapArrayType), typ
                gel__ulnu = builder.load(kpoyl__symqa)
                dwmbj__knzoc = dict_keys(builder, context, qwj__zeohc)
                nuntq__fike = dict_values(builder, context, qwj__zeohc)
                fkbow__kvy = get_array_elem_counts(c, builder, context,
                    dwmbj__knzoc, typ.key_arr_type)
                jklta__fejcc = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for leaen__pxbtg in range(1, jklta__fejcc + 1):
                    kvky__apd = builder.extract_value(gel__ulnu, leaen__pxbtg)
                    khfx__hwtz = builder.extract_value(fkbow__kvy, 
                        leaen__pxbtg - 1)
                    gel__ulnu = builder.insert_value(gel__ulnu, builder.add
                        (kvky__apd, khfx__hwtz), leaen__pxbtg)
                fwm__fnmia = get_array_elem_counts(c, builder, context,
                    nuntq__fike, typ.value_arr_type)
                for leaen__pxbtg in range(jklta__fejcc + 1, yhavw__bfb):
                    kvky__apd = builder.extract_value(gel__ulnu, leaen__pxbtg)
                    khfx__hwtz = builder.extract_value(fwm__fnmia, 
                        leaen__pxbtg - jklta__fejcc)
                    gel__ulnu = builder.insert_value(gel__ulnu, builder.add
                        (kvky__apd, khfx__hwtz), leaen__pxbtg)
                builder.store(gel__ulnu, kpoyl__symqa)
                c.pyapi.decref(dwmbj__knzoc)
                c.pyapi.decref(nuntq__fike)
        c.pyapi.decref(qwj__zeohc)
    c.pyapi.decref(lghjc__nfnh)
    c.pyapi.decref(C_NA)
    return builder.load(kpoyl__symqa)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    ccg__pmwbz = n_elems.type.count
    assert ccg__pmwbz >= 1
    ybatr__xvgrg = builder.extract_value(n_elems, 0)
    if ccg__pmwbz != 1:
        effm__blam = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, leaen__pxbtg) for leaen__pxbtg in range(1, ccg__pmwbz)])
        gxsfk__mgxuz = types.Tuple([types.int64] * (ccg__pmwbz - 1))
    else:
        effm__blam = context.get_dummy_value()
        gxsfk__mgxuz = types.none
    xgusl__ldfy = types.TypeRef(arr_type)
    izq__ohaf = arr_type(types.int64, xgusl__ldfy, gxsfk__mgxuz)
    args = [ybatr__xvgrg, context.get_dummy_value(), effm__blam]
    ubaw__qgb = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        irp__hwin, cbrq__qxru = c.pyapi.call_jit_code(ubaw__qgb, izq__ohaf,
            args)
    else:
        cbrq__qxru = context.compile_internal(builder, ubaw__qgb, izq__ohaf,
            args)
    return cbrq__qxru


def is_ll_eq(builder, val1, val2):
    ykcia__fqdg = val1.type.pointee
    fyql__eqvz = val2.type.pointee
    assert ykcia__fqdg == fyql__eqvz, 'invalid llvm value comparison'
    if isinstance(ykcia__fqdg, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(ykcia__fqdg.elements) if isinstance(ykcia__fqdg, lir.
            BaseStructType) else ykcia__fqdg.count
        citpy__ybxh = lir.Constant(lir.IntType(1), 1)
        for leaen__pxbtg in range(n_elems):
            lmdak__ufx = lir.IntType(32)(0)
            zpx__tkw = lir.IntType(32)(leaen__pxbtg)
            yrfsy__xvgp = builder.gep(val1, [lmdak__ufx, zpx__tkw],
                inbounds=True)
            qkq__kjnwr = builder.gep(val2, [lmdak__ufx, zpx__tkw], inbounds
                =True)
            citpy__ybxh = builder.and_(citpy__ybxh, is_ll_eq(builder,
                yrfsy__xvgp, qkq__kjnwr))
        return citpy__ybxh
    yic__krrg = builder.load(val1)
    yvx__igjuv = builder.load(val2)
    if yic__krrg.type in (lir.FloatType(), lir.DoubleType()):
        wsfuw__qymrl = 32 if yic__krrg.type == lir.FloatType() else 64
        yic__krrg = builder.bitcast(yic__krrg, lir.IntType(wsfuw__qymrl))
        yvx__igjuv = builder.bitcast(yvx__igjuv, lir.IntType(wsfuw__qymrl))
    return builder.icmp_unsigned('==', yic__krrg, yvx__igjuv)
