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
    rwa__fxqjh = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        xbtn__vhgn, = args
        zytk__byjj = cgutils.create_struct_proxy(string_type)(context,
            builder, value=xbtn__vhgn)
        umfxj__ykw = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        myjt__zocw = cgutils.create_struct_proxy(rwa__fxqjh)(context, builder)
        is_ascii = builder.icmp_unsigned('==', zytk__byjj.is_ascii, lir.
            Constant(zytk__byjj.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (ttzjq__rlvxg, gwt__twwsd):
            with ttzjq__rlvxg:
                context.nrt.incref(builder, string_type, xbtn__vhgn)
                umfxj__ykw.data = zytk__byjj.data
                umfxj__ykw.meminfo = zytk__byjj.meminfo
                myjt__zocw.f1 = zytk__byjj.length
            with gwt__twwsd:
                xxxrk__fzb = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                nmmed__onpv = cgutils.get_or_insert_function(builder.module,
                    xxxrk__fzb, name='unicode_to_utf8')
                zhuqo__ldqx = context.get_constant_null(types.voidptr)
                iow__dkpe = builder.call(nmmed__onpv, [zhuqo__ldqx,
                    zytk__byjj.data, zytk__byjj.length, zytk__byjj.kind])
                myjt__zocw.f1 = iow__dkpe
                ekjfb__jdb = builder.add(iow__dkpe, lir.Constant(lir.
                    IntType(64), 1))
                umfxj__ykw.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=ekjfb__jdb, align=32)
                umfxj__ykw.data = context.nrt.meminfo_data(builder,
                    umfxj__ykw.meminfo)
                builder.call(nmmed__onpv, [umfxj__ykw.data, zytk__byjj.data,
                    zytk__byjj.length, zytk__byjj.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    umfxj__ykw.data, [iow__dkpe]))
        myjt__zocw.f0 = umfxj__ykw._getvalue()
        return myjt__zocw._getvalue()
    return rwa__fxqjh(string_type), codegen


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
        xxxrk__fzb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        qviem__xavz = cgutils.get_or_insert_function(builder.module,
            xxxrk__fzb, name='memcmp')
        return builder.call(qviem__xavz, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    rqlhu__djq = n(10)

    def impl(n):
        if n == 0:
            return 1
        hnht__wlps = 0
        if n < 0:
            n = -n
            hnht__wlps += 1
        while n > 0:
            n = n // rqlhu__djq
            hnht__wlps += 1
        return hnht__wlps
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
        [yehqy__tmjym] = args
        if isinstance(yehqy__tmjym, StdStringType):
            return signature(types.float64, yehqy__tmjym)
        if yehqy__tmjym == string_type:
            return signature(types.float64, yehqy__tmjym)


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
    zytk__byjj = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    xxxrk__fzb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tta__vmsr = cgutils.get_or_insert_function(builder.module, xxxrk__fzb,
        name='init_string_const')
    return builder.call(tta__vmsr, [zytk__byjj.data, zytk__byjj.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        sztdm__jpy = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(sztdm__jpy._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return sztdm__jpy
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    zytk__byjj = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return zytk__byjj.data


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
        nycy__xdpey = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, nycy__xdpey)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        uas__dhsk, = args
        fnl__qkjhw = types.List(string_type)
        utd__sovah = numba.cpython.listobj.ListInstance.allocate(context,
            builder, fnl__qkjhw, uas__dhsk)
        utd__sovah.size = uas__dhsk
        pfqza__stmm = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        pfqza__stmm.data = utd__sovah.value
        return pfqza__stmm._getvalue()
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
            cix__nlbok = 0
            exau__sfh = v
            if exau__sfh < 0:
                cix__nlbok = 1
                exau__sfh = -exau__sfh
            if exau__sfh < 1:
                sjl__lvomx = 1
            else:
                sjl__lvomx = 1 + int(np.floor(np.log10(exau__sfh)))
            length = cix__nlbok + sjl__lvomx + 1 + 6
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
    xxxrk__fzb = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    tta__vmsr = cgutils.get_or_insert_function(builder.module, xxxrk__fzb,
        name='str_to_float64')
    res = builder.call(tta__vmsr, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    xxxrk__fzb = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    tta__vmsr = cgutils.get_or_insert_function(builder.module, xxxrk__fzb,
        name='str_to_float32')
    res = builder.call(tta__vmsr, (val,))
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
    zytk__byjj = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xxxrk__fzb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    tta__vmsr = cgutils.get_or_insert_function(builder.module, xxxrk__fzb,
        name='str_to_int64')
    res = builder.call(tta__vmsr, (zytk__byjj.data, zytk__byjj.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    zytk__byjj = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xxxrk__fzb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    tta__vmsr = cgutils.get_or_insert_function(builder.module, xxxrk__fzb,
        name='str_to_uint64')
    res = builder.call(tta__vmsr, (zytk__byjj.data, zytk__byjj.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        tzbi__lwya = ', '.join('e{}'.format(uakg__gxydi) for uakg__gxydi in
            range(len(args)))
        if tzbi__lwya:
            tzbi__lwya += ', '
        moo__wpq = ', '.join("{} = ''".format(a) for a in kws.keys())
        cwqy__gon = f'def format_stub(string, {tzbi__lwya} {moo__wpq}):\n'
        cwqy__gon += '    pass\n'
        mrq__ufp = {}
        exec(cwqy__gon, {}, mrq__ufp)
        ohgjf__uxy = mrq__ufp['format_stub']
        cgv__mha = numba.core.utils.pysignature(ohgjf__uxy)
        daajp__sspo = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, daajp__sspo).replace(pysig=cgv__mha)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    flsr__wqfz = pat is not None and len(pat) > 1
    if flsr__wqfz:
        jxu__bzv = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    utd__sovah = len(arr)
    xthxy__hyf = 0
    oujf__vzbs = 0
    for uakg__gxydi in numba.parfors.parfor.internal_prange(utd__sovah):
        if bodo.libs.array_kernels.isna(arr, uakg__gxydi):
            continue
        if flsr__wqfz:
            mxnci__bpqx = jxu__bzv.split(arr[uakg__gxydi], maxsplit=n)
        elif pat == '':
            mxnci__bpqx = [''] + list(arr[uakg__gxydi]) + ['']
        else:
            mxnci__bpqx = arr[uakg__gxydi].split(pat, n)
        xthxy__hyf += len(mxnci__bpqx)
        for s in mxnci__bpqx:
            oujf__vzbs += bodo.libs.str_arr_ext.get_utf8_size(s)
    npkmc__dxd = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        utd__sovah, (xthxy__hyf, oujf__vzbs), bodo.libs.str_arr_ext.
        string_array_type)
    wmnf__omt = bodo.libs.array_item_arr_ext.get_offsets(npkmc__dxd)
    ffd__bzo = bodo.libs.array_item_arr_ext.get_null_bitmap(npkmc__dxd)
    vnqsh__ena = bodo.libs.array_item_arr_ext.get_data(npkmc__dxd)
    zbp__lsgtp = 0
    for gecjg__ljhc in numba.parfors.parfor.internal_prange(utd__sovah):
        wmnf__omt[gecjg__ljhc] = zbp__lsgtp
        if bodo.libs.array_kernels.isna(arr, gecjg__ljhc):
            bodo.libs.int_arr_ext.set_bit_to_arr(ffd__bzo, gecjg__ljhc, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(ffd__bzo, gecjg__ljhc, 1)
        if flsr__wqfz:
            mxnci__bpqx = jxu__bzv.split(arr[gecjg__ljhc], maxsplit=n)
        elif pat == '':
            mxnci__bpqx = [''] + list(arr[gecjg__ljhc]) + ['']
        else:
            mxnci__bpqx = arr[gecjg__ljhc].split(pat, n)
        zdiz__ndg = len(mxnci__bpqx)
        for fiwfl__aopnv in range(zdiz__ndg):
            s = mxnci__bpqx[fiwfl__aopnv]
            vnqsh__ena[zbp__lsgtp] = s
            zbp__lsgtp += 1
    wmnf__omt[utd__sovah] = zbp__lsgtp
    return npkmc__dxd


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                pdtur__hvkp = '-0x'
                x = x * -1
            else:
                pdtur__hvkp = '0x'
            x = np.uint64(x)
            if x == 0:
                vyqm__wvg = 1
            else:
                vyqm__wvg = fast_ceil_log2(x + 1)
                vyqm__wvg = (vyqm__wvg + 3) // 4
            length = len(pdtur__hvkp) + vyqm__wvg
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, pdtur__hvkp._data,
                len(pdtur__hvkp), 1)
            int_to_hex(output, vyqm__wvg, len(pdtur__hvkp), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    wkev__pylw = 0 if x & x - 1 == 0 else 1
    pjd__gsf = [np.uint64(18446744069414584320), np.uint64(4294901760), np.
        uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    zvb__qle = 32
    for uakg__gxydi in range(len(pjd__gsf)):
        tun__loed = 0 if x & pjd__gsf[uakg__gxydi] == 0 else zvb__qle
        wkev__pylw = wkev__pylw + tun__loed
        x = x >> tun__loed
        zvb__qle = zvb__qle >> 1
    return wkev__pylw


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        ugrx__rodq = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        xxxrk__fzb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        pdri__ntrnx = cgutils.get_or_insert_function(builder.module,
            xxxrk__fzb, name='int_to_hex')
        uevhl__yiqe = builder.inttoptr(builder.add(builder.ptrtoint(
            ugrx__rodq.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(pdri__ntrnx, (uevhl__yiqe, out_len, int_val))
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
