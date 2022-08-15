import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    inrd__ebgrq = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        tfca__yrctq, = args
        ewr__xkf = cgutils.create_struct_proxy(string_type)(context,
            builder, value=tfca__yrctq)
        jkqbp__mpooq = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        ohc__vhx = cgutils.create_struct_proxy(inrd__ebgrq)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ewr__xkf.is_ascii, lir.
            Constant(ewr__xkf.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (iix__siz, gur__imatm):
            with iix__siz:
                context.nrt.incref(builder, string_type, tfca__yrctq)
                jkqbp__mpooq.data = ewr__xkf.data
                jkqbp__mpooq.meminfo = ewr__xkf.meminfo
                ohc__vhx.f1 = ewr__xkf.length
            with gur__imatm:
                wnoix__hthai = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                eopuk__ged = cgutils.get_or_insert_function(builder.module,
                    wnoix__hthai, name='unicode_to_utf8')
                jgqb__xbdl = context.get_constant_null(types.voidptr)
                bhd__vwo = builder.call(eopuk__ged, [jgqb__xbdl, ewr__xkf.
                    data, ewr__xkf.length, ewr__xkf.kind])
                ohc__vhx.f1 = bhd__vwo
                foqjb__ydu = builder.add(bhd__vwo, lir.Constant(lir.IntType
                    (64), 1))
                jkqbp__mpooq.meminfo = context.nrt.meminfo_alloc_aligned(
                    builder, size=foqjb__ydu, align=32)
                jkqbp__mpooq.data = context.nrt.meminfo_data(builder,
                    jkqbp__mpooq.meminfo)
                builder.call(eopuk__ged, [jkqbp__mpooq.data, ewr__xkf.data,
                    ewr__xkf.length, ewr__xkf.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    jkqbp__mpooq.data, [bhd__vwo]))
        ohc__vhx.f0 = jkqbp__mpooq._getvalue()
        return ohc__vhx._getvalue()
    return inrd__ebgrq(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        wnoix__hthai = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        ctn__tedjl = cgutils.get_or_insert_function(builder.module,
            wnoix__hthai, name='memcmp')
        return builder.call(ctn__tedjl, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    uceja__zhpci = n(10)

    def impl(n):
        if n == 0:
            return 1
        okips__seq = 0
        if n < 0:
            n = -n
            okips__seq += 1
        while n > 0:
            n = n // uceja__zhpci
            okips__seq += 1
        return okips__seq
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [kixy__odrpv] = args
        if isinstance(kixy__odrpv, StdStringType):
            return signature(types.float64, kixy__odrpv)
        if kixy__odrpv == string_type:
            return signature(types.float64, kixy__odrpv)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    ewr__xkf = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    wnoix__hthai = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    zmklx__iaetu = cgutils.get_or_insert_function(builder.module,
        wnoix__hthai, name='init_string_const')
    return builder.call(zmklx__iaetu, [ewr__xkf.data, ewr__xkf.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        aynze__rnmu = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(aynze__rnmu._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return aynze__rnmu
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ewr__xkf = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ewr__xkf.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xdso__iorhi = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, xdso__iorhi)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        mzl__afr, = args
        goe__jzfpe = types.List(string_type)
        wqo__ivnoh = numba.cpython.listobj.ListInstance.allocate(context,
            builder, goe__jzfpe, mzl__afr)
        wqo__ivnoh.size = mzl__afr
        jqfw__iyzsx = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        jqfw__iyzsx.data = wqo__ivnoh.value
        return jqfw__iyzsx._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            jjcdw__tjd = 0
            xnes__vozc = v
            if xnes__vozc < 0:
                jjcdw__tjd = 1
                xnes__vozc = -xnes__vozc
            if xnes__vozc < 1:
                ujtq__kht = 1
            else:
                ujtq__kht = 1 + int(np.floor(np.log10(xnes__vozc)))
            length = jjcdw__tjd + ujtq__kht + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    wnoix__hthai = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    zmklx__iaetu = cgutils.get_or_insert_function(builder.module,
        wnoix__hthai, name='str_to_float64')
    res = builder.call(zmklx__iaetu, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    wnoix__hthai = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    zmklx__iaetu = cgutils.get_or_insert_function(builder.module,
        wnoix__hthai, name='str_to_float32')
    res = builder.call(zmklx__iaetu, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    ewr__xkf = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    wnoix__hthai = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    zmklx__iaetu = cgutils.get_or_insert_function(builder.module,
        wnoix__hthai, name='str_to_int64')
    res = builder.call(zmklx__iaetu, (ewr__xkf.data, ewr__xkf.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ewr__xkf = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    wnoix__hthai = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    zmklx__iaetu = cgutils.get_or_insert_function(builder.module,
        wnoix__hthai, name='str_to_uint64')
    res = builder.call(zmklx__iaetu, (ewr__xkf.data, ewr__xkf.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        dhhtx__swnd = ', '.join('e{}'.format(wana__gvblk) for wana__gvblk in
            range(len(args)))
        if dhhtx__swnd:
            dhhtx__swnd += ', '
        wovko__xjp = ', '.join("{} = ''".format(a) for a in kws.keys())
        avv__duxf = f'def format_stub(string, {dhhtx__swnd} {wovko__xjp}):\n'
        avv__duxf += '    pass\n'
        ber__rhz = {}
        exec(avv__duxf, {}, ber__rhz)
        zptzw__rzqx = ber__rhz['format_stub']
        xnbin__dkjl = numba.core.utils.pysignature(zptzw__rzqx)
        yfgaj__pqw = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, yfgaj__pqw).replace(pysig=xnbin__dkjl)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    mkoen__frcx = pat is not None and len(pat) > 1
    if mkoen__frcx:
        vbwds__txvlp = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    wqo__ivnoh = len(arr)
    dfhg__vcm = 0
    yyjrd__znbd = 0
    for wana__gvblk in numba.parfors.parfor.internal_prange(wqo__ivnoh):
        if bodo.libs.array_kernels.isna(arr, wana__gvblk):
            continue
        if mkoen__frcx:
            cpotw__bic = vbwds__txvlp.split(arr[wana__gvblk], maxsplit=n)
        elif pat == '':
            cpotw__bic = [''] + list(arr[wana__gvblk]) + ['']
        else:
            cpotw__bic = arr[wana__gvblk].split(pat, n)
        dfhg__vcm += len(cpotw__bic)
        for s in cpotw__bic:
            yyjrd__znbd += bodo.libs.str_arr_ext.get_utf8_size(s)
    hjtf__vmie = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        wqo__ivnoh, (dfhg__vcm, yyjrd__znbd), bodo.libs.str_arr_ext.
        string_array_type)
    qlsdw__ogk = bodo.libs.array_item_arr_ext.get_offsets(hjtf__vmie)
    bpyax__vtptq = bodo.libs.array_item_arr_ext.get_null_bitmap(hjtf__vmie)
    pdom__yyoug = bodo.libs.array_item_arr_ext.get_data(hjtf__vmie)
    wore__gcn = 0
    for kimp__qzbp in numba.parfors.parfor.internal_prange(wqo__ivnoh):
        qlsdw__ogk[kimp__qzbp] = wore__gcn
        if bodo.libs.array_kernels.isna(arr, kimp__qzbp):
            bodo.libs.int_arr_ext.set_bit_to_arr(bpyax__vtptq, kimp__qzbp, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(bpyax__vtptq, kimp__qzbp, 1)
        if mkoen__frcx:
            cpotw__bic = vbwds__txvlp.split(arr[kimp__qzbp], maxsplit=n)
        elif pat == '':
            cpotw__bic = [''] + list(arr[kimp__qzbp]) + ['']
        else:
            cpotw__bic = arr[kimp__qzbp].split(pat, n)
        yhwnw__sla = len(cpotw__bic)
        for fwv__izine in range(yhwnw__sla):
            s = cpotw__bic[fwv__izine]
            pdom__yyoug[wore__gcn] = s
            wore__gcn += 1
    qlsdw__ogk[wqo__ivnoh] = wore__gcn
    return hjtf__vmie


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                gfy__tai = '-0x'
                x = x * -1
            else:
                gfy__tai = '0x'
            x = np.uint64(x)
            if x == 0:
                noq__byun = 1
            else:
                noq__byun = fast_ceil_log2(x + 1)
                noq__byun = (noq__byun + 3) // 4
            length = len(gfy__tai) + noq__byun
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, gfy__tai._data, len
                (gfy__tai), 1)
            int_to_hex(output, noq__byun, len(gfy__tai), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    rpd__eyr = 0 if x & x - 1 == 0 else 1
    sakqe__sapi = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    qibab__kpg = 32
    for wana__gvblk in range(len(sakqe__sapi)):
        dsf__aof = 0 if x & sakqe__sapi[wana__gvblk] == 0 else qibab__kpg
        rpd__eyr = rpd__eyr + dsf__aof
        x = x >> dsf__aof
        qibab__kpg = qibab__kpg >> 1
    return rpd__eyr


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        tneo__wdodf = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        wnoix__hthai = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        ixmdv__dbe = cgutils.get_or_insert_function(builder.module,
            wnoix__hthai, name='int_to_hex')
        rjh__bxbk = builder.inttoptr(builder.add(builder.ptrtoint(
            tneo__wdodf.data, lir.IntType(64)), header_len), lir.IntType(8)
            .as_pointer())
        builder.call(ixmdv__dbe, (rjh__bxbk, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
