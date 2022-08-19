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
    zngxb__okkmj = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        xyaqi__mgarg, = args
        mur__dby = cgutils.create_struct_proxy(string_type)(context,
            builder, value=xyaqi__mgarg)
        icf__oit = cgutils.create_struct_proxy(utf8_str_type)(context, builder)
        ltdga__lkxev = cgutils.create_struct_proxy(zngxb__okkmj)(context,
            builder)
        is_ascii = builder.icmp_unsigned('==', mur__dby.is_ascii, lir.
            Constant(mur__dby.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (aqwew__gdgys, btvuu__shjvq):
            with aqwew__gdgys:
                context.nrt.incref(builder, string_type, xyaqi__mgarg)
                icf__oit.data = mur__dby.data
                icf__oit.meminfo = mur__dby.meminfo
                ltdga__lkxev.f1 = mur__dby.length
            with btvuu__shjvq:
                pzx__ubfwp = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                uxu__pvjom = cgutils.get_or_insert_function(builder.module,
                    pzx__ubfwp, name='unicode_to_utf8')
                tqhco__wrdfi = context.get_constant_null(types.voidptr)
                tcwa__hqtb = builder.call(uxu__pvjom, [tqhco__wrdfi,
                    mur__dby.data, mur__dby.length, mur__dby.kind])
                ltdga__lkxev.f1 = tcwa__hqtb
                tbu__qvgag = builder.add(tcwa__hqtb, lir.Constant(lir.
                    IntType(64), 1))
                icf__oit.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=tbu__qvgag, align=32)
                icf__oit.data = context.nrt.meminfo_data(builder, icf__oit.
                    meminfo)
                builder.call(uxu__pvjom, [icf__oit.data, mur__dby.data,
                    mur__dby.length, mur__dby.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    icf__oit.data, [tcwa__hqtb]))
        ltdga__lkxev.f0 = icf__oit._getvalue()
        return ltdga__lkxev._getvalue()
    return zngxb__okkmj(string_type), codegen


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
        pzx__ubfwp = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        ooaq__fdtw = cgutils.get_or_insert_function(builder.module,
            pzx__ubfwp, name='memcmp')
        return builder.call(ooaq__fdtw, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    xtbvw__rgk = n(10)

    def impl(n):
        if n == 0:
            return 1
        npt__vqoaq = 0
        if n < 0:
            n = -n
            npt__vqoaq += 1
        while n > 0:
            n = n // xtbvw__rgk
            npt__vqoaq += 1
        return npt__vqoaq
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
        [lkh__gcn] = args
        if isinstance(lkh__gcn, StdStringType):
            return signature(types.float64, lkh__gcn)
        if lkh__gcn == string_type:
            return signature(types.float64, lkh__gcn)


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
    mur__dby = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    pzx__ubfwp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tiq__xsxik = cgutils.get_or_insert_function(builder.module, pzx__ubfwp,
        name='init_string_const')
    return builder.call(tiq__xsxik, [mur__dby.data, mur__dby.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        djpw__tasmd = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(djpw__tasmd._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return djpw__tasmd
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    mur__dby = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return mur__dby.data


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
        nqtls__cpjfi = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, nqtls__cpjfi)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        gppgn__ricx, = args
        whok__gbl = types.List(string_type)
        had__uskvg = numba.cpython.listobj.ListInstance.allocate(context,
            builder, whok__gbl, gppgn__ricx)
        had__uskvg.size = gppgn__ricx
        giu__vxitt = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        giu__vxitt.data = had__uskvg.value
        return giu__vxitt._getvalue()
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
            xequ__hsq = 0
            zngpg__sco = v
            if zngpg__sco < 0:
                xequ__hsq = 1
                zngpg__sco = -zngpg__sco
            if zngpg__sco < 1:
                radfz__xrk = 1
            else:
                radfz__xrk = 1 + int(np.floor(np.log10(zngpg__sco)))
            length = xequ__hsq + radfz__xrk + 1 + 6
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
    pzx__ubfwp = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    tiq__xsxik = cgutils.get_or_insert_function(builder.module, pzx__ubfwp,
        name='str_to_float64')
    res = builder.call(tiq__xsxik, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    pzx__ubfwp = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    tiq__xsxik = cgutils.get_or_insert_function(builder.module, pzx__ubfwp,
        name='str_to_float32')
    res = builder.call(tiq__xsxik, (val,))
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
    mur__dby = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    pzx__ubfwp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    tiq__xsxik = cgutils.get_or_insert_function(builder.module, pzx__ubfwp,
        name='str_to_int64')
    res = builder.call(tiq__xsxik, (mur__dby.data, mur__dby.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    mur__dby = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    pzx__ubfwp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    tiq__xsxik = cgutils.get_or_insert_function(builder.module, pzx__ubfwp,
        name='str_to_uint64')
    res = builder.call(tiq__xsxik, (mur__dby.data, mur__dby.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        xlyan__zsah = ', '.join('e{}'.format(agylc__nccuc) for agylc__nccuc in
            range(len(args)))
        if xlyan__zsah:
            xlyan__zsah += ', '
        kkoiw__zcqb = ', '.join("{} = ''".format(a) for a in kws.keys())
        dwz__jqoes = f'def format_stub(string, {xlyan__zsah} {kkoiw__zcqb}):\n'
        dwz__jqoes += '    pass\n'
        ujivr__vca = {}
        exec(dwz__jqoes, {}, ujivr__vca)
        wbbm__oje = ujivr__vca['format_stub']
        mky__plhz = numba.core.utils.pysignature(wbbm__oje)
        ztre__hleci = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, ztre__hleci).replace(pysig=mky__plhz)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    czjuf__nhxs = pat is not None and len(pat) > 1
    if czjuf__nhxs:
        dzqwp__dsf = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    had__uskvg = len(arr)
    vbnye__pducn = 0
    pfk__ier = 0
    for agylc__nccuc in numba.parfors.parfor.internal_prange(had__uskvg):
        if bodo.libs.array_kernels.isna(arr, agylc__nccuc):
            continue
        if czjuf__nhxs:
            truzs__ydcoq = dzqwp__dsf.split(arr[agylc__nccuc], maxsplit=n)
        elif pat == '':
            truzs__ydcoq = [''] + list(arr[agylc__nccuc]) + ['']
        else:
            truzs__ydcoq = arr[agylc__nccuc].split(pat, n)
        vbnye__pducn += len(truzs__ydcoq)
        for s in truzs__ydcoq:
            pfk__ier += bodo.libs.str_arr_ext.get_utf8_size(s)
    oply__uodd = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        had__uskvg, (vbnye__pducn, pfk__ier), bodo.libs.str_arr_ext.
        string_array_type)
    slk__cwv = bodo.libs.array_item_arr_ext.get_offsets(oply__uodd)
    lvta__hicx = bodo.libs.array_item_arr_ext.get_null_bitmap(oply__uodd)
    rpeb__sudi = bodo.libs.array_item_arr_ext.get_data(oply__uodd)
    dtai__yawzn = 0
    for luiy__mrpoq in numba.parfors.parfor.internal_prange(had__uskvg):
        slk__cwv[luiy__mrpoq] = dtai__yawzn
        if bodo.libs.array_kernels.isna(arr, luiy__mrpoq):
            bodo.libs.int_arr_ext.set_bit_to_arr(lvta__hicx, luiy__mrpoq, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(lvta__hicx, luiy__mrpoq, 1)
        if czjuf__nhxs:
            truzs__ydcoq = dzqwp__dsf.split(arr[luiy__mrpoq], maxsplit=n)
        elif pat == '':
            truzs__ydcoq = [''] + list(arr[luiy__mrpoq]) + ['']
        else:
            truzs__ydcoq = arr[luiy__mrpoq].split(pat, n)
        bimw__uqotz = len(truzs__ydcoq)
        for aqnq__duc in range(bimw__uqotz):
            s = truzs__ydcoq[aqnq__duc]
            rpeb__sudi[dtai__yawzn] = s
            dtai__yawzn += 1
    slk__cwv[had__uskvg] = dtai__yawzn
    return oply__uodd


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                wnz__xrhso = '-0x'
                x = x * -1
            else:
                wnz__xrhso = '0x'
            x = np.uint64(x)
            if x == 0:
                urnpx__onnlf = 1
            else:
                urnpx__onnlf = fast_ceil_log2(x + 1)
                urnpx__onnlf = (urnpx__onnlf + 3) // 4
            length = len(wnz__xrhso) + urnpx__onnlf
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, wnz__xrhso._data,
                len(wnz__xrhso), 1)
            int_to_hex(output, urnpx__onnlf, len(wnz__xrhso), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    vozw__xnfzj = 0 if x & x - 1 == 0 else 1
    nwo__pfeyj = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    ikcq__ormel = 32
    for agylc__nccuc in range(len(nwo__pfeyj)):
        tgp__fmorf = 0 if x & nwo__pfeyj[agylc__nccuc] == 0 else ikcq__ormel
        vozw__xnfzj = vozw__xnfzj + tgp__fmorf
        x = x >> tgp__fmorf
        ikcq__ormel = ikcq__ormel >> 1
    return vozw__xnfzj


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        aeyru__lue = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        pzx__ubfwp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        naymn__xlg = cgutils.get_or_insert_function(builder.module,
            pzx__ubfwp, name='int_to_hex')
        bpmj__fravf = builder.inttoptr(builder.add(builder.ptrtoint(
            aeyru__lue.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(naymn__xlg, (bpmj__fravf, out_len, int_val))
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
