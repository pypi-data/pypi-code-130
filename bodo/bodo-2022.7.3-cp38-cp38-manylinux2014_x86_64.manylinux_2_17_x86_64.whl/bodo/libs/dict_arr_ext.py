"""Dictionary encoded array data type, similar to DictionaryArray of Arrow.
The purpose is to improve memory consumption and performance over string_array_type for
string arrays that have a lot of repetitive values (typical in practice).
Can be extended to be used with types other than strings as well.
See:
https://bodo.atlassian.net/browse/BE-2295
https://bodo.atlassian.net/wiki/spaces/B/pages/993722369/Dictionary-encoded+String+Array+Support+in+Parquet+read+compute+...
https://arrow.apache.org/docs/cpp/api/array.html#dictionary-encoded
"""
import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo
from bodo.libs import hstr_ext
from bodo.libs.bool_arr_ext import init_bool_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, get_str_arr_item_length, overload_str_arr_astype, pre_alloc_string_array, string_array_type
from bodo.utils.typing import BodoArrayIterator, is_overload_none, raise_bodo_error
from bodo.utils.utils import synchronize_error_njit
ll.add_symbol('box_dict_str_array', hstr_ext.box_dict_str_array)
dict_indices_arr_type = IntegerArrayType(types.int32)


class DictionaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, arr_data_type):
        self.data = arr_data_type
        super(DictionaryArrayType, self).__init__(name=
            f'DictionaryArrayType({arr_data_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self.data.dtype

    def copy(self):
        return DictionaryArrayType(self.data)

    @property
    def indices_type(self):
        return dict_indices_arr_type

    @property
    def indices_dtype(self):
        return dict_indices_arr_type.dtype

    def unify(self, typingctx, other):
        if other == string_array_type:
            return string_array_type


dict_str_arr_type = DictionaryArrayType(string_array_type)


@register_model(DictionaryArrayType)
class DictionaryArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ksuy__ujx = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, ksuy__ujx)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        ybdv__rta, tij__wmx, svd__bdqve = args
        iuxg__ixa = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        iuxg__ixa.data = ybdv__rta
        iuxg__ixa.indices = tij__wmx
        iuxg__ixa.has_global_dictionary = svd__bdqve
        context.nrt.incref(builder, signature.args[0], ybdv__rta)
        context.nrt.incref(builder, signature.args[1], tij__wmx)
        return iuxg__ixa._getvalue()
    dplc__swqvu = DictionaryArrayType(data_t)
    flpf__cusq = dplc__swqvu(data_t, indices_t, types.bool_)
    return flpf__cusq, codegen


@typeof_impl.register(pa.DictionaryArray)
def typeof_dict_value(val, c):
    if val.type.value_type == pa.string():
        return dict_str_arr_type


def to_pa_dict_arr(A):
    if isinstance(A, pa.DictionaryArray):
        return A
    for i in range(len(A)):
        if pd.isna(A[i]):
            A[i] = None
    return pa.array(A).dictionary_encode()


@unbox(DictionaryArrayType)
def unbox_dict_arr(typ, val, c):
    if bodo.hiframes.boxing._use_dict_str_type:
        nfk__kkdx = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(nfk__kkdx, [val])
        c.pyapi.decref(nfk__kkdx)
    iuxg__ixa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nera__tnk = c.pyapi.object_getattr_string(val, 'dictionary')
    gzs__qgog = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    wygca__gsej = c.pyapi.call_method(nera__tnk, 'to_numpy', (gzs__qgog,))
    iuxg__ixa.data = c.unbox(typ.data, wygca__gsej).value
    ohe__drgh = c.pyapi.object_getattr_string(val, 'indices')
    svbmb__srn = c.context.insert_const_string(c.builder.module, 'pandas')
    suiwy__kvgkc = c.pyapi.import_module_noblock(svbmb__srn)
    xuujv__fet = c.pyapi.string_from_constant_string('Int32')
    bgi__fiuj = c.pyapi.call_method(suiwy__kvgkc, 'array', (ohe__drgh,
        xuujv__fet))
    iuxg__ixa.indices = c.unbox(dict_indices_arr_type, bgi__fiuj).value
    iuxg__ixa.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(nera__tnk)
    c.pyapi.decref(gzs__qgog)
    c.pyapi.decref(wygca__gsej)
    c.pyapi.decref(ohe__drgh)
    c.pyapi.decref(suiwy__kvgkc)
    c.pyapi.decref(xuujv__fet)
    c.pyapi.decref(bgi__fiuj)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    kqn__wwtfo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iuxg__ixa._getvalue(), is_error=kqn__wwtfo)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    iuxg__ixa = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, iuxg__ixa.data)
        jfx__wqyo = c.box(typ.data, iuxg__ixa.data)
        ucf__apgwy = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, iuxg__ixa.indices)
        pfv__peeko = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        suykm__bdw = cgutils.get_or_insert_function(c.builder.module,
            pfv__peeko, name='box_dict_str_array')
        iad__tyj = cgutils.create_struct_proxy(types.Array(types.int32, 1, 'C')
            )(c.context, c.builder, ucf__apgwy.data)
        ehxw__ssxis = c.builder.extract_value(iad__tyj.shape, 0)
        btmyy__xbg = iad__tyj.data
        wiami__npm = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, ucf__apgwy.null_bitmap).data
        wygca__gsej = c.builder.call(suykm__bdw, [ehxw__ssxis, jfx__wqyo,
            btmyy__xbg, wiami__npm])
        c.pyapi.decref(jfx__wqyo)
    else:
        svbmb__srn = c.context.insert_const_string(c.builder.module, 'pyarrow')
        zba__aleam = c.pyapi.import_module_noblock(svbmb__srn)
        yhrjb__kpzp = c.pyapi.object_getattr_string(zba__aleam,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, iuxg__ixa.data)
        jfx__wqyo = c.box(typ.data, iuxg__ixa.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, iuxg__ixa.
            indices)
        ohe__drgh = c.box(dict_indices_arr_type, iuxg__ixa.indices)
        hgyxw__dtkhz = c.pyapi.call_method(yhrjb__kpzp, 'from_arrays', (
            ohe__drgh, jfx__wqyo))
        gzs__qgog = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        wygca__gsej = c.pyapi.call_method(hgyxw__dtkhz, 'to_numpy', (
            gzs__qgog,))
        c.pyapi.decref(zba__aleam)
        c.pyapi.decref(jfx__wqyo)
        c.pyapi.decref(ohe__drgh)
        c.pyapi.decref(yhrjb__kpzp)
        c.pyapi.decref(hgyxw__dtkhz)
        c.pyapi.decref(gzs__qgog)
    c.context.nrt.decref(c.builder, typ, val)
    return wygca__gsej


@overload(len, no_unliteral=True)
def overload_dict_arr_len(A):
    if isinstance(A, DictionaryArrayType):
        return lambda A: len(A._indices)


@overload_attribute(DictionaryArrayType, 'shape')
def overload_dict_arr_shape(A):
    return lambda A: (len(A._indices),)


@overload_attribute(DictionaryArrayType, 'ndim')
def overload_dict_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DictionaryArrayType, 'size')
def overload_dict_arr_size(A):
    return lambda A: len(A._indices)


@overload_method(DictionaryArrayType, 'tolist', no_unliteral=True)
def overload_dict_arr_tolist(A):
    return lambda A: list(A)


overload_method(DictionaryArrayType, 'astype', no_unliteral=True)(
    overload_str_arr_astype)


@overload_method(DictionaryArrayType, 'copy', no_unliteral=True)
def overload_dict_arr_copy(A):

    def copy_impl(A):
        return init_dict_arr(A._data.copy(), A._indices.copy(), A.
            _has_global_dictionary)
    return copy_impl


@overload_attribute(DictionaryArrayType, 'dtype')
def overload_dict_arr_dtype(A):
    return lambda A: A._data.dtype


@overload_attribute(DictionaryArrayType, 'nbytes')
def dict_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._indices.nbytes


@lower_constant(DictionaryArrayType)
def lower_constant_dict_arr(context, builder, typ, pyval):
    if bodo.hiframes.boxing._use_dict_str_type and isinstance(pyval, np.ndarray
        ):
        pyval = pa.array(pyval).dictionary_encode()
    fyfma__onnil = pyval.dictionary.to_numpy(False)
    olflk__gprt = pd.array(pyval.indices, 'Int32')
    fyfma__onnil = context.get_constant_generic(builder, typ.data, fyfma__onnil
        )
    olflk__gprt = context.get_constant_generic(builder,
        dict_indices_arr_type, olflk__gprt)
    bcg__ijb = context.get_constant(types.bool_, False)
    jzbub__iax = lir.Constant.literal_struct([fyfma__onnil, olflk__gprt,
        bcg__ijb])
    return jzbub__iax


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            jqei__iza = A._indices[ind]
            return A._data[jqei__iza]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        ybdv__rta = A._data
        tij__wmx = A._indices
        ehxw__ssxis = len(tij__wmx)
        yowa__gmhu = [get_str_arr_item_length(ybdv__rta, i) for i in range(
            len(ybdv__rta))]
        acz__eut = 0
        for i in range(ehxw__ssxis):
            if not bodo.libs.array_kernels.isna(tij__wmx, i):
                acz__eut += yowa__gmhu[tij__wmx[i]]
        riakl__kprk = pre_alloc_string_array(ehxw__ssxis, acz__eut)
        for i in range(ehxw__ssxis):
            if bodo.libs.array_kernels.isna(tij__wmx, i):
                bodo.libs.array_kernels.setna(riakl__kprk, i)
                continue
            ind = tij__wmx[i]
            if bodo.libs.array_kernels.isna(ybdv__rta, ind):
                bodo.libs.array_kernels.setna(riakl__kprk, i)
                continue
            riakl__kprk[i] = ybdv__rta[ind]
        return riakl__kprk
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    jqei__iza = -1
    ybdv__rta = arr._data
    for i in range(len(ybdv__rta)):
        if bodo.libs.array_kernels.isna(ybdv__rta, i):
            continue
        if ybdv__rta[i] == val:
            jqei__iza = i
            break
    return jqei__iza


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    ehxw__ssxis = len(arr)
    jqei__iza = find_dict_ind(arr, val)
    if jqei__iza == -1:
        return init_bool_array(np.full(ehxw__ssxis, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == jqei__iza


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    ehxw__ssxis = len(arr)
    jqei__iza = find_dict_ind(arr, val)
    if jqei__iza == -1:
        return init_bool_array(np.full(ehxw__ssxis, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != jqei__iza


def get_binary_op_overload(op, lhs, rhs):
    if op == operator.eq:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(rhs, lhs)
    if op == operator.ne:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(rhs, lhs)


def convert_dict_arr_to_int(arr, dtype):
    return arr


@overload(convert_dict_arr_to_int)
def convert_dict_arr_to_int_overload(arr, dtype):

    def impl(arr, dtype):
        milf__yvrs = arr._data
        tbfbm__phs = bodo.libs.int_arr_ext.alloc_int_array(len(milf__yvrs),
            dtype)
        for xknxi__nnsf in range(len(milf__yvrs)):
            if bodo.libs.array_kernels.isna(milf__yvrs, xknxi__nnsf):
                bodo.libs.array_kernels.setna(tbfbm__phs, xknxi__nnsf)
                continue
            tbfbm__phs[xknxi__nnsf] = np.int64(milf__yvrs[xknxi__nnsf])
        ehxw__ssxis = len(arr)
        tij__wmx = arr._indices
        riakl__kprk = bodo.libs.int_arr_ext.alloc_int_array(ehxw__ssxis, dtype)
        for i in range(ehxw__ssxis):
            if bodo.libs.array_kernels.isna(tij__wmx, i):
                bodo.libs.array_kernels.setna(riakl__kprk, i)
                continue
            riakl__kprk[i] = tbfbm__phs[tij__wmx[i]]
        return riakl__kprk
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    snonu__ports = len(arrs)
    ltxs__xvrd = 'def impl(arrs, sep):\n'
    ltxs__xvrd += '  ind_map = {}\n'
    ltxs__xvrd += '  out_strs = []\n'
    ltxs__xvrd += '  n = len(arrs[0])\n'
    for i in range(snonu__ports):
        ltxs__xvrd += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(snonu__ports):
        ltxs__xvrd += f'  data{i} = arrs[{i}]._data\n'
    ltxs__xvrd += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    ltxs__xvrd += '  for i in range(n):\n'
    ojwm__cgnj = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(snonu__ports)])
    ltxs__xvrd += f'    if {ojwm__cgnj}:\n'
    ltxs__xvrd += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    ltxs__xvrd += '      continue\n'
    for i in range(snonu__ports):
        ltxs__xvrd += f'    ind{i} = indices{i}[i]\n'
    fhcjd__thbhf = '(' + ', '.join(f'ind{i}' for i in range(snonu__ports)
        ) + ')'
    ltxs__xvrd += f'    if {fhcjd__thbhf} not in ind_map:\n'
    ltxs__xvrd += '      out_ind = len(out_strs)\n'
    ltxs__xvrd += f'      ind_map[{fhcjd__thbhf}] = out_ind\n'
    utxqi__qfvl = "''" if is_overload_none(sep) else 'sep'
    irlx__qtuy = ', '.join([f'data{i}[ind{i}]' for i in range(snonu__ports)])
    ltxs__xvrd += f'      v = {utxqi__qfvl}.join([{irlx__qtuy}])\n'
    ltxs__xvrd += '      out_strs.append(v)\n'
    ltxs__xvrd += '    else:\n'
    ltxs__xvrd += f'      out_ind = ind_map[{fhcjd__thbhf}]\n'
    ltxs__xvrd += '    out_indices[i] = out_ind\n'
    ltxs__xvrd += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    ltxs__xvrd += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    oanay__kwku = {}
    exec(ltxs__xvrd, {'bodo': bodo, 'numba': numba, 'np': np}, oanay__kwku)
    impl = oanay__kwku['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    gwc__jnf = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    flpf__cusq = toty(fromty)
    htx__xdx = context.compile_internal(builder, gwc__jnf, flpf__cusq, (val,))
    return impl_ret_new_ref(context, builder, toty, htx__xdx)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    fyfma__onnil = arr._data
    trz__mzoih = len(fyfma__onnil)
    xsf__ulka = pre_alloc_string_array(trz__mzoih, -1)
    if regex:
        ora__qqtcs = re.compile(pat, flags)
        for i in range(trz__mzoih):
            if bodo.libs.array_kernels.isna(fyfma__onnil, i):
                bodo.libs.array_kernels.setna(xsf__ulka, i)
                continue
            xsf__ulka[i] = ora__qqtcs.sub(repl=repl, string=fyfma__onnil[i])
    else:
        for i in range(trz__mzoih):
            if bodo.libs.array_kernels.isna(fyfma__onnil, i):
                bodo.libs.array_kernels.setna(xsf__ulka, i)
                continue
            xsf__ulka[i] = fyfma__onnil[i].replace(pat, repl)
    return init_dict_arr(xsf__ulka, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    iuxg__ixa = arr._data
    miw__rmx = len(iuxg__ixa)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(miw__rmx)
    for i in range(miw__rmx):
        dict_arr_out[i] = iuxg__ixa[i].startswith(pat)
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    riakl__kprk = bodo.libs.bool_arr_ext.alloc_bool_array(ebdg__dhpg)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = dict_arr_out[olflk__gprt[i]]
    return riakl__kprk


@register_jitable
def str_endswith(arr, pat, na):
    iuxg__ixa = arr._data
    miw__rmx = len(iuxg__ixa)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(miw__rmx)
    for i in range(miw__rmx):
        dict_arr_out[i] = iuxg__ixa[i].endswith(pat)
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    riakl__kprk = bodo.libs.bool_arr_ext.alloc_bool_array(ebdg__dhpg)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = dict_arr_out[olflk__gprt[i]]
    return riakl__kprk


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    iuxg__ixa = arr._data
    nykug__posdd = pd.Series(iuxg__ixa)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = nykug__posdd.array._str_contains(pat, case, flags,
            na, regex)
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    riakl__kprk = bodo.libs.bool_arr_ext.alloc_bool_array(ebdg__dhpg)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = dict_arr_out[olflk__gprt[i]]
    return riakl__kprk


@register_jitable
def str_contains_non_regex(arr, pat, case):
    iuxg__ixa = arr._data
    miw__rmx = len(iuxg__ixa)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(miw__rmx)
    if not case:
        jeinp__cuy = pat.upper()
    for i in range(miw__rmx):
        if case:
            dict_arr_out[i] = pat in iuxg__ixa[i]
        else:
            dict_arr_out[i] = jeinp__cuy in iuxg__ixa[i].upper()
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    riakl__kprk = bodo.libs.bool_arr_ext.alloc_bool_array(ebdg__dhpg)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = dict_arr_out[olflk__gprt[i]]
    return riakl__kprk


@numba.njit
def str_match(arr, pat, case, flags, na):
    iuxg__ixa = arr._data
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    riakl__kprk = bodo.libs.bool_arr_ext.alloc_bool_array(ebdg__dhpg)
    nykug__posdd = pd.Series(iuxg__ixa)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = nykug__posdd.array._str_match(pat, case, flags, na)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = dict_arr_out[olflk__gprt[i]]
    return riakl__kprk


def create_simple_str2str_methods(func_name, func_args):
    ltxs__xvrd = f"""def str_{func_name}({', '.join(func_args)}):
    data_arr = arr._data
    n_data = len(data_arr)
    out_str_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_data, -1)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_str_arr, i)
            continue
        out_str_arr[i] = data_arr[i].{func_name}({', '.join(func_args[1:])})
    return init_dict_arr(out_str_arr, arr._indices.copy(), arr._has_global_dictionary)
"""
    oanay__kwku = {}
    exec(ltxs__xvrd, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, oanay__kwku)
    return oanay__kwku[f'str_{func_name}']


def _register_simple_str2str_methods():
    ayazs__rbp = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in ayazs__rbp.keys():
        qfhdq__lcz = create_simple_str2str_methods(func_name, ayazs__rbp[
            func_name])
        qfhdq__lcz = register_jitable(qfhdq__lcz)
        globals()[f'str_{func_name}'] = qfhdq__lcz


_register_simple_str2str_methods()


@register_jitable
def str_index(arr, sub, start, end):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    trz__mzoih = len(fyfma__onnil)
    ebdg__dhpg = len(olflk__gprt)
    lry__mrg = bodo.libs.int_arr_ext.alloc_int_array(trz__mzoih, np.int64)
    riakl__kprk = bodo.libs.int_arr_ext.alloc_int_array(ebdg__dhpg, np.int64)
    tjgis__yli = False
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            bodo.libs.array_kernels.setna(lry__mrg, i)
        else:
            lry__mrg[i] = fyfma__onnil[i].find(sub, start, end)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(lry__mrg, olflk__gprt[i]):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = lry__mrg[olflk__gprt[i]]
            if riakl__kprk[i] == -1:
                tjgis__yli = True
    ouuyh__tdvbd = 'substring not found' if tjgis__yli else ''
    synchronize_error_njit('ValueError', ouuyh__tdvbd)
    return riakl__kprk


@register_jitable
def str_rindex(arr, sub, start, end):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    trz__mzoih = len(fyfma__onnil)
    ebdg__dhpg = len(olflk__gprt)
    lry__mrg = bodo.libs.int_arr_ext.alloc_int_array(trz__mzoih, np.int64)
    riakl__kprk = bodo.libs.int_arr_ext.alloc_int_array(ebdg__dhpg, np.int64)
    tjgis__yli = False
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            bodo.libs.array_kernels.setna(lry__mrg, i)
        else:
            lry__mrg[i] = fyfma__onnil[i].rindex(sub, start, end)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(lry__mrg, olflk__gprt[i]):
            bodo.libs.array_kernels.setna(riakl__kprk, i)
        else:
            riakl__kprk[i] = lry__mrg[olflk__gprt[i]]
            if riakl__kprk[i] == -1:
                tjgis__yli = True
    ouuyh__tdvbd = 'substring not found' if tjgis__yli else ''
    synchronize_error_njit('ValueError', ouuyh__tdvbd)
    return riakl__kprk


def create_find_methods(func_name):
    ltxs__xvrd = f"""def str_{func_name}(arr, sub, start, end):
  data_arr = arr._data
  indices_arr = arr._indices
  n_data = len(data_arr)
  n_indices = len(indices_arr)
  tmp_dict_arr = bodo.libs.int_arr_ext.alloc_int_array(n_data, np.int64)
  out_int_arr = bodo.libs.int_arr_ext.alloc_int_array(n_indices, np.int64)
  for i in range(n_data):
    if bodo.libs.array_kernels.isna(data_arr, i):
      bodo.libs.array_kernels.setna(tmp_dict_arr, i)
      continue
    tmp_dict_arr[i] = data_arr[i].{func_name}(sub, start, end)
  for i in range(n_indices):
    if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
      tmp_dict_arr, indices_arr[i]
    ):
      bodo.libs.array_kernels.setna(out_int_arr, i)
    else:
      out_int_arr[i] = tmp_dict_arr[indices_arr[i]]
  return out_int_arr"""
    oanay__kwku = {}
    exec(ltxs__xvrd, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, oanay__kwku)
    return oanay__kwku[f'str_{func_name}']


def _register_find_methods():
    krk__rtjb = ['find', 'rfind']
    for func_name in krk__rtjb:
        qfhdq__lcz = create_find_methods(func_name)
        qfhdq__lcz = register_jitable(qfhdq__lcz)
        globals()[f'str_{func_name}'] = qfhdq__lcz


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    trz__mzoih = len(fyfma__onnil)
    ebdg__dhpg = len(olflk__gprt)
    lry__mrg = bodo.libs.int_arr_ext.alloc_int_array(trz__mzoih, np.int64)
    atprl__ged = bodo.libs.int_arr_ext.alloc_int_array(ebdg__dhpg, np.int64)
    regex = re.compile(pat, flags)
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            bodo.libs.array_kernels.setna(lry__mrg, i)
            continue
        lry__mrg[i] = bodo.libs.str_ext.str_findall_count(regex,
            fyfma__onnil[i])
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(olflk__gprt, i
            ) or bodo.libs.array_kernels.isna(lry__mrg, olflk__gprt[i]):
            bodo.libs.array_kernels.setna(atprl__ged, i)
        else:
            atprl__ged[i] = lry__mrg[olflk__gprt[i]]
    return atprl__ged


@register_jitable
def str_len(arr):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    ebdg__dhpg = len(olflk__gprt)
    lry__mrg = bodo.libs.array_kernels.get_arr_lens(fyfma__onnil, False)
    atprl__ged = bodo.libs.int_arr_ext.alloc_int_array(ebdg__dhpg, np.int64)
    for i in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(olflk__gprt, i
            ) or bodo.libs.array_kernels.isna(lry__mrg, olflk__gprt[i]):
            bodo.libs.array_kernels.setna(atprl__ged, i)
        else:
            atprl__ged[i] = lry__mrg[olflk__gprt[i]]
    return atprl__ged


@register_jitable
def str_slice(arr, start, stop, step):
    fyfma__onnil = arr._data
    trz__mzoih = len(fyfma__onnil)
    xsf__ulka = bodo.libs.str_arr_ext.pre_alloc_string_array(trz__mzoih, -1)
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            bodo.libs.array_kernels.setna(xsf__ulka, i)
            continue
        xsf__ulka[i] = fyfma__onnil[i][start:stop:step]
    return init_dict_arr(xsf__ulka, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    trz__mzoih = len(fyfma__onnil)
    ebdg__dhpg = len(olflk__gprt)
    xsf__ulka = pre_alloc_string_array(trz__mzoih, -1)
    riakl__kprk = pre_alloc_string_array(ebdg__dhpg, -1)
    for xknxi__nnsf in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, xknxi__nnsf) or not -len(
            fyfma__onnil[xknxi__nnsf]) <= i < len(fyfma__onnil[xknxi__nnsf]):
            bodo.libs.array_kernels.setna(xsf__ulka, xknxi__nnsf)
            continue
        xsf__ulka[xknxi__nnsf] = fyfma__onnil[xknxi__nnsf][i]
    for xknxi__nnsf in range(ebdg__dhpg):
        if bodo.libs.array_kernels.isna(olflk__gprt, xknxi__nnsf
            ) or bodo.libs.array_kernels.isna(xsf__ulka, olflk__gprt[
            xknxi__nnsf]):
            bodo.libs.array_kernels.setna(riakl__kprk, xknxi__nnsf)
            continue
        riakl__kprk[xknxi__nnsf] = xsf__ulka[olflk__gprt[xknxi__nnsf]]
    return riakl__kprk


@register_jitable
def str_repeat_int(arr, repeats):
    fyfma__onnil = arr._data
    trz__mzoih = len(fyfma__onnil)
    xsf__ulka = pre_alloc_string_array(trz__mzoih, -1)
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            bodo.libs.array_kernels.setna(xsf__ulka, i)
            continue
        xsf__ulka[i] = fyfma__onnil[i] * repeats
    return init_dict_arr(xsf__ulka, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    ltxs__xvrd = f"""def str_{func_name}(arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    out_dict_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_data)
    out_bool_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_indices)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_dict_arr, i)
            continue
        out_dict_arr[i] = np.bool_(data_arr[i].{func_name}())
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
            data_arr, indices_arr[i]        ):
            bodo.libs.array_kernels.setna(out_bool_arr, i)
        else:
            out_bool_arr[i] = out_dict_arr[indices_arr[i]]
    return out_bool_arr"""
    oanay__kwku = {}
    exec(ltxs__xvrd, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, oanay__kwku)
    return oanay__kwku[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        qfhdq__lcz = create_str2bool_methods(func_name)
        qfhdq__lcz = register_jitable(qfhdq__lcz)
        globals()[f'str_{func_name}'] = qfhdq__lcz


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    fyfma__onnil = arr._data
    olflk__gprt = arr._indices
    trz__mzoih = len(fyfma__onnil)
    ebdg__dhpg = len(olflk__gprt)
    regex = re.compile(pat, flags=flags)
    aul__vnhka = []
    for nmd__vohyy in range(n_cols):
        aul__vnhka.append(pre_alloc_string_array(trz__mzoih, -1))
    gmfb__gcwo = bodo.libs.bool_arr_ext.alloc_bool_array(trz__mzoih)
    cvvz__wykoa = olflk__gprt.copy()
    for i in range(trz__mzoih):
        if bodo.libs.array_kernels.isna(fyfma__onnil, i):
            gmfb__gcwo[i] = True
            for xknxi__nnsf in range(n_cols):
                bodo.libs.array_kernels.setna(aul__vnhka[xknxi__nnsf], i)
            continue
        whos__xxith = regex.search(fyfma__onnil[i])
        if whos__xxith:
            gmfb__gcwo[i] = False
            iny__cnexx = whos__xxith.groups()
            for xknxi__nnsf in range(n_cols):
                aul__vnhka[xknxi__nnsf][i] = iny__cnexx[xknxi__nnsf]
        else:
            gmfb__gcwo[i] = True
            for xknxi__nnsf in range(n_cols):
                bodo.libs.array_kernels.setna(aul__vnhka[xknxi__nnsf], i)
    for i in range(ebdg__dhpg):
        if gmfb__gcwo[cvvz__wykoa[i]]:
            bodo.libs.array_kernels.setna(cvvz__wykoa, i)
    neyvr__yqf = [init_dict_arr(aul__vnhka[i], cvvz__wykoa.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return neyvr__yqf


def create_extractall_methods(is_multi_group):
    mllez__vdn = '_multi' if is_multi_group else ''
    ltxs__xvrd = f"""def str_extractall{mllez__vdn}(arr, regex, n_cols, index_arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    indices_count = [0 for _ in range(n_data)]
    for i in range(n_indices):
        if not bodo.libs.array_kernels.isna(indices_arr, i):
            indices_count[indices_arr[i]] += 1
    dict_group_count = []
    out_dict_len = out_ind_len = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        dict_group_count.append((out_dict_len, len(m)))
        out_dict_len += len(m)
        out_ind_len += indices_count[i] * len(m)
    out_dict_arr_list = []
    for _ in range(n_cols):
        out_dict_arr_list.append(pre_alloc_string_array(out_dict_len, -1))
    out_indices_arr = bodo.libs.int_arr_ext.alloc_int_array(out_ind_len, np.int32)
    out_ind_arr = bodo.utils.utils.alloc_type(out_ind_len, index_arr, (-1,))
    out_match_arr = np.empty(out_ind_len, np.int64)
    curr_ind = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        for s in m:
            for j in range(n_cols):
                out_dict_arr_list[j][curr_ind] = s{'[j]' if is_multi_group else ''}
            curr_ind += 1
    curr_ind = 0
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i):
            continue
        n_rows = dict_group_count[indices_arr[i]][1]
        for k in range(n_rows):
            out_indices_arr[curr_ind] = dict_group_count[indices_arr[i]][0] + k
            out_ind_arr[curr_ind] = index_arr[i]
            out_match_arr[curr_ind] = k
            curr_ind += 1
    out_arr_list = [
        init_dict_arr(
            out_dict_arr_list[i], out_indices_arr.copy(), arr._has_global_dictionary
        )
        for i in range(n_cols)
    ]
    return (out_ind_arr, out_match_arr, out_arr_list) 
"""
    oanay__kwku = {}
    exec(ltxs__xvrd, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, oanay__kwku)
    return oanay__kwku[f'str_extractall{mllez__vdn}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        mllez__vdn = '_multi' if is_multi_group else ''
        qfhdq__lcz = create_extractall_methods(is_multi_group)
        qfhdq__lcz = register_jitable(qfhdq__lcz)
        globals()[f'str_extractall{mllez__vdn}'] = qfhdq__lcz


_register_extractall_methods()
