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
        vyip__pskso = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, vyip__pskso)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        iawnc__pwmrv, qunwz__njasc, wgytc__gunb = args
        ntri__dbarw = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ntri__dbarw.data = iawnc__pwmrv
        ntri__dbarw.indices = qunwz__njasc
        ntri__dbarw.has_global_dictionary = wgytc__gunb
        context.nrt.incref(builder, signature.args[0], iawnc__pwmrv)
        context.nrt.incref(builder, signature.args[1], qunwz__njasc)
        return ntri__dbarw._getvalue()
    vpl__ltjy = DictionaryArrayType(data_t)
    wfsu__iik = vpl__ltjy(data_t, indices_t, types.bool_)
    return wfsu__iik, codegen


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
        obge__kjn = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(obge__kjn, [val])
        c.pyapi.decref(obge__kjn)
    ntri__dbarw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    dyjfr__xagay = c.pyapi.object_getattr_string(val, 'dictionary')
    cpj__jhxkv = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    hzwy__tzq = c.pyapi.call_method(dyjfr__xagay, 'to_numpy', (cpj__jhxkv,))
    ntri__dbarw.data = c.unbox(typ.data, hzwy__tzq).value
    aduhs__chvla = c.pyapi.object_getattr_string(val, 'indices')
    lhdy__achqs = c.context.insert_const_string(c.builder.module, 'pandas')
    cmxep__wabr = c.pyapi.import_module_noblock(lhdy__achqs)
    nzwz__zrls = c.pyapi.string_from_constant_string('Int32')
    upj__yel = c.pyapi.call_method(cmxep__wabr, 'array', (aduhs__chvla,
        nzwz__zrls))
    ntri__dbarw.indices = c.unbox(dict_indices_arr_type, upj__yel).value
    ntri__dbarw.has_global_dictionary = c.context.get_constant(types.bool_,
        False)
    c.pyapi.decref(dyjfr__xagay)
    c.pyapi.decref(cpj__jhxkv)
    c.pyapi.decref(hzwy__tzq)
    c.pyapi.decref(aduhs__chvla)
    c.pyapi.decref(cmxep__wabr)
    c.pyapi.decref(nzwz__zrls)
    c.pyapi.decref(upj__yel)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    xvu__lgsi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ntri__dbarw._getvalue(), is_error=xvu__lgsi)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    ntri__dbarw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, ntri__dbarw.data)
        cay__shh = c.box(typ.data, ntri__dbarw.data)
        rvf__fxwf = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, ntri__dbarw.indices)
        zesrq__yjl = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        wgd__vcy = cgutils.get_or_insert_function(c.builder.module,
            zesrq__yjl, name='box_dict_str_array')
        ruya__lsa = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, rvf__fxwf.data)
        kqsg__gqbo = c.builder.extract_value(ruya__lsa.shape, 0)
        axgmf__rha = ruya__lsa.data
        adxhe__eyfa = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, rvf__fxwf.null_bitmap).data
        hzwy__tzq = c.builder.call(wgd__vcy, [kqsg__gqbo, cay__shh,
            axgmf__rha, adxhe__eyfa])
        c.pyapi.decref(cay__shh)
    else:
        lhdy__achqs = c.context.insert_const_string(c.builder.module, 'pyarrow'
            )
        svn__qnhdc = c.pyapi.import_module_noblock(lhdy__achqs)
        sqcz__nxoc = c.pyapi.object_getattr_string(svn__qnhdc,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, ntri__dbarw.data)
        cay__shh = c.box(typ.data, ntri__dbarw.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, ntri__dbarw.
            indices)
        aduhs__chvla = c.box(dict_indices_arr_type, ntri__dbarw.indices)
        jvhtf__nmiw = c.pyapi.call_method(sqcz__nxoc, 'from_arrays', (
            aduhs__chvla, cay__shh))
        cpj__jhxkv = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        hzwy__tzq = c.pyapi.call_method(jvhtf__nmiw, 'to_numpy', (cpj__jhxkv,))
        c.pyapi.decref(svn__qnhdc)
        c.pyapi.decref(cay__shh)
        c.pyapi.decref(aduhs__chvla)
        c.pyapi.decref(sqcz__nxoc)
        c.pyapi.decref(jvhtf__nmiw)
        c.pyapi.decref(cpj__jhxkv)
    c.context.nrt.decref(c.builder, typ, val)
    return hzwy__tzq


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
    jxv__qje = pyval.dictionary.to_numpy(False)
    pks__gmal = pd.array(pyval.indices, 'Int32')
    jxv__qje = context.get_constant_generic(builder, typ.data, jxv__qje)
    pks__gmal = context.get_constant_generic(builder, dict_indices_arr_type,
        pks__gmal)
    ajmnd__jwbr = context.get_constant(types.bool_, False)
    onl__laeuy = lir.Constant.literal_struct([jxv__qje, pks__gmal, ajmnd__jwbr]
        )
    return onl__laeuy


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            efoo__aclfj = A._indices[ind]
            return A._data[efoo__aclfj]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        iawnc__pwmrv = A._data
        qunwz__njasc = A._indices
        kqsg__gqbo = len(qunwz__njasc)
        hfrmg__slbk = [get_str_arr_item_length(iawnc__pwmrv, i) for i in
            range(len(iawnc__pwmrv))]
        fqnc__men = 0
        for i in range(kqsg__gqbo):
            if not bodo.libs.array_kernels.isna(qunwz__njasc, i):
                fqnc__men += hfrmg__slbk[qunwz__njasc[i]]
        ado__nluob = pre_alloc_string_array(kqsg__gqbo, fqnc__men)
        for i in range(kqsg__gqbo):
            if bodo.libs.array_kernels.isna(qunwz__njasc, i):
                bodo.libs.array_kernels.setna(ado__nluob, i)
                continue
            ind = qunwz__njasc[i]
            if bodo.libs.array_kernels.isna(iawnc__pwmrv, ind):
                bodo.libs.array_kernels.setna(ado__nluob, i)
                continue
            ado__nluob[i] = iawnc__pwmrv[ind]
        return ado__nluob
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    efoo__aclfj = -1
    iawnc__pwmrv = arr._data
    for i in range(len(iawnc__pwmrv)):
        if bodo.libs.array_kernels.isna(iawnc__pwmrv, i):
            continue
        if iawnc__pwmrv[i] == val:
            efoo__aclfj = i
            break
    return efoo__aclfj


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    kqsg__gqbo = len(arr)
    efoo__aclfj = find_dict_ind(arr, val)
    if efoo__aclfj == -1:
        return init_bool_array(np.full(kqsg__gqbo, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == efoo__aclfj


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    kqsg__gqbo = len(arr)
    efoo__aclfj = find_dict_ind(arr, val)
    if efoo__aclfj == -1:
        return init_bool_array(np.full(kqsg__gqbo, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != efoo__aclfj


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
        xjot__kmhmv = arr._data
        ifln__kvh = bodo.libs.int_arr_ext.alloc_int_array(len(xjot__kmhmv),
            dtype)
        for flt__xmga in range(len(xjot__kmhmv)):
            if bodo.libs.array_kernels.isna(xjot__kmhmv, flt__xmga):
                bodo.libs.array_kernels.setna(ifln__kvh, flt__xmga)
                continue
            ifln__kvh[flt__xmga] = np.int64(xjot__kmhmv[flt__xmga])
        kqsg__gqbo = len(arr)
        qunwz__njasc = arr._indices
        ado__nluob = bodo.libs.int_arr_ext.alloc_int_array(kqsg__gqbo, dtype)
        for i in range(kqsg__gqbo):
            if bodo.libs.array_kernels.isna(qunwz__njasc, i):
                bodo.libs.array_kernels.setna(ado__nluob, i)
                continue
            ado__nluob[i] = ifln__kvh[qunwz__njasc[i]]
        return ado__nluob
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    oxmqm__wads = len(arrs)
    iebnm__olete = 'def impl(arrs, sep):\n'
    iebnm__olete += '  ind_map = {}\n'
    iebnm__olete += '  out_strs = []\n'
    iebnm__olete += '  n = len(arrs[0])\n'
    for i in range(oxmqm__wads):
        iebnm__olete += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(oxmqm__wads):
        iebnm__olete += f'  data{i} = arrs[{i}]._data\n'
    iebnm__olete += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    iebnm__olete += '  for i in range(n):\n'
    uclhi__ocv = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(oxmqm__wads)])
    iebnm__olete += f'    if {uclhi__ocv}:\n'
    iebnm__olete += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    iebnm__olete += '      continue\n'
    for i in range(oxmqm__wads):
        iebnm__olete += f'    ind{i} = indices{i}[i]\n'
    oje__vcxid = '(' + ', '.join(f'ind{i}' for i in range(oxmqm__wads)) + ')'
    iebnm__olete += f'    if {oje__vcxid} not in ind_map:\n'
    iebnm__olete += '      out_ind = len(out_strs)\n'
    iebnm__olete += f'      ind_map[{oje__vcxid}] = out_ind\n'
    olalz__iixwo = "''" if is_overload_none(sep) else 'sep'
    gsqm__bejc = ', '.join([f'data{i}[ind{i}]' for i in range(oxmqm__wads)])
    iebnm__olete += f'      v = {olalz__iixwo}.join([{gsqm__bejc}])\n'
    iebnm__olete += '      out_strs.append(v)\n'
    iebnm__olete += '    else:\n'
    iebnm__olete += f'      out_ind = ind_map[{oje__vcxid}]\n'
    iebnm__olete += '    out_indices[i] = out_ind\n'
    iebnm__olete += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    iebnm__olete += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    yzfgt__khh = {}
    exec(iebnm__olete, {'bodo': bodo, 'numba': numba, 'np': np}, yzfgt__khh)
    impl = yzfgt__khh['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    cbh__eyk = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    wfsu__iik = toty(fromty)
    log__dqy = context.compile_internal(builder, cbh__eyk, wfsu__iik, (val,))
    return impl_ret_new_ref(context, builder, toty, log__dqy)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    jxv__qje = arr._data
    ipnei__rzrg = len(jxv__qje)
    wxhb__vphs = pre_alloc_string_array(ipnei__rzrg, -1)
    if regex:
        xmpav__uahng = re.compile(pat, flags)
        for i in range(ipnei__rzrg):
            if bodo.libs.array_kernels.isna(jxv__qje, i):
                bodo.libs.array_kernels.setna(wxhb__vphs, i)
                continue
            wxhb__vphs[i] = xmpav__uahng.sub(repl=repl, string=jxv__qje[i])
    else:
        for i in range(ipnei__rzrg):
            if bodo.libs.array_kernels.isna(jxv__qje, i):
                bodo.libs.array_kernels.setna(wxhb__vphs, i)
                continue
            wxhb__vphs[i] = jxv__qje[i].replace(pat, repl)
    return init_dict_arr(wxhb__vphs, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    ntri__dbarw = arr._data
    gzn__mqoxw = len(ntri__dbarw)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gzn__mqoxw)
    for i in range(gzn__mqoxw):
        dict_arr_out[i] = ntri__dbarw[i].startswith(pat)
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    ado__nluob = bodo.libs.bool_arr_ext.alloc_bool_array(kdqc__gtxen)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = dict_arr_out[pks__gmal[i]]
    return ado__nluob


@register_jitable
def str_endswith(arr, pat, na):
    ntri__dbarw = arr._data
    gzn__mqoxw = len(ntri__dbarw)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gzn__mqoxw)
    for i in range(gzn__mqoxw):
        dict_arr_out[i] = ntri__dbarw[i].endswith(pat)
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    ado__nluob = bodo.libs.bool_arr_ext.alloc_bool_array(kdqc__gtxen)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = dict_arr_out[pks__gmal[i]]
    return ado__nluob


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    ntri__dbarw = arr._data
    zuds__poa = pd.Series(ntri__dbarw)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = zuds__poa.array._str_contains(pat, case, flags, na,
            regex)
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    ado__nluob = bodo.libs.bool_arr_ext.alloc_bool_array(kdqc__gtxen)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = dict_arr_out[pks__gmal[i]]
    return ado__nluob


@register_jitable
def str_contains_non_regex(arr, pat, case):
    ntri__dbarw = arr._data
    gzn__mqoxw = len(ntri__dbarw)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gzn__mqoxw)
    if not case:
        bjwgq__vyljy = pat.upper()
    for i in range(gzn__mqoxw):
        if case:
            dict_arr_out[i] = pat in ntri__dbarw[i]
        else:
            dict_arr_out[i] = bjwgq__vyljy in ntri__dbarw[i].upper()
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    ado__nluob = bodo.libs.bool_arr_ext.alloc_bool_array(kdqc__gtxen)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = dict_arr_out[pks__gmal[i]]
    return ado__nluob


@numba.njit
def str_match(arr, pat, case, flags, na):
    ntri__dbarw = arr._data
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    ado__nluob = bodo.libs.bool_arr_ext.alloc_bool_array(kdqc__gtxen)
    zuds__poa = pd.Series(ntri__dbarw)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = zuds__poa.array._str_match(pat, case, flags, na)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = dict_arr_out[pks__gmal[i]]
    return ado__nluob


def create_simple_str2str_methods(func_name, func_args):
    iebnm__olete = f"""def str_{func_name}({', '.join(func_args)}):
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
    yzfgt__khh = {}
    exec(iebnm__olete, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, yzfgt__khh)
    return yzfgt__khh[f'str_{func_name}']


def _register_simple_str2str_methods():
    booc__bwp = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in booc__bwp.keys():
        cbs__xcblq = create_simple_str2str_methods(func_name, booc__bwp[
            func_name])
        cbs__xcblq = register_jitable(cbs__xcblq)
        globals()[f'str_{func_name}'] = cbs__xcblq


_register_simple_str2str_methods()


@register_jitable
def str_index(arr, sub, start, end):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    ipnei__rzrg = len(jxv__qje)
    kdqc__gtxen = len(pks__gmal)
    jafu__koqt = bodo.libs.int_arr_ext.alloc_int_array(ipnei__rzrg, np.int64)
    ado__nluob = bodo.libs.int_arr_ext.alloc_int_array(kdqc__gtxen, np.int64)
    stle__tecja = False
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            bodo.libs.array_kernels.setna(jafu__koqt, i)
        else:
            jafu__koqt[i] = jxv__qje[i].find(sub, start, end)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(jafu__koqt, pks__gmal[i]):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = jafu__koqt[pks__gmal[i]]
            if ado__nluob[i] == -1:
                stle__tecja = True
    ycc__bkdj = 'substring not found' if stle__tecja else ''
    synchronize_error_njit('ValueError', ycc__bkdj)
    return ado__nluob


@register_jitable
def str_rindex(arr, sub, start, end):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    ipnei__rzrg = len(jxv__qje)
    kdqc__gtxen = len(pks__gmal)
    jafu__koqt = bodo.libs.int_arr_ext.alloc_int_array(ipnei__rzrg, np.int64)
    ado__nluob = bodo.libs.int_arr_ext.alloc_int_array(kdqc__gtxen, np.int64)
    stle__tecja = False
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            bodo.libs.array_kernels.setna(jafu__koqt, i)
        else:
            jafu__koqt[i] = jxv__qje[i].rindex(sub, start, end)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(jafu__koqt, pks__gmal[i]):
            bodo.libs.array_kernels.setna(ado__nluob, i)
        else:
            ado__nluob[i] = jafu__koqt[pks__gmal[i]]
            if ado__nluob[i] == -1:
                stle__tecja = True
    ycc__bkdj = 'substring not found' if stle__tecja else ''
    synchronize_error_njit('ValueError', ycc__bkdj)
    return ado__nluob


def create_find_methods(func_name):
    iebnm__olete = f"""def str_{func_name}(arr, sub, start, end):
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
    yzfgt__khh = {}
    exec(iebnm__olete, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, yzfgt__khh)
    return yzfgt__khh[f'str_{func_name}']


def _register_find_methods():
    wph__ncj = ['find', 'rfind']
    for func_name in wph__ncj:
        cbs__xcblq = create_find_methods(func_name)
        cbs__xcblq = register_jitable(cbs__xcblq)
        globals()[f'str_{func_name}'] = cbs__xcblq


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    ipnei__rzrg = len(jxv__qje)
    kdqc__gtxen = len(pks__gmal)
    jafu__koqt = bodo.libs.int_arr_ext.alloc_int_array(ipnei__rzrg, np.int64)
    njoc__gbv = bodo.libs.int_arr_ext.alloc_int_array(kdqc__gtxen, np.int64)
    regex = re.compile(pat, flags)
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            bodo.libs.array_kernels.setna(jafu__koqt, i)
            continue
        jafu__koqt[i] = bodo.libs.str_ext.str_findall_count(regex, jxv__qje[i])
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(pks__gmal, i
            ) or bodo.libs.array_kernels.isna(jafu__koqt, pks__gmal[i]):
            bodo.libs.array_kernels.setna(njoc__gbv, i)
        else:
            njoc__gbv[i] = jafu__koqt[pks__gmal[i]]
    return njoc__gbv


@register_jitable
def str_len(arr):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    kdqc__gtxen = len(pks__gmal)
    jafu__koqt = bodo.libs.array_kernels.get_arr_lens(jxv__qje, False)
    njoc__gbv = bodo.libs.int_arr_ext.alloc_int_array(kdqc__gtxen, np.int64)
    for i in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(pks__gmal, i
            ) or bodo.libs.array_kernels.isna(jafu__koqt, pks__gmal[i]):
            bodo.libs.array_kernels.setna(njoc__gbv, i)
        else:
            njoc__gbv[i] = jafu__koqt[pks__gmal[i]]
    return njoc__gbv


@register_jitable
def str_slice(arr, start, stop, step):
    jxv__qje = arr._data
    ipnei__rzrg = len(jxv__qje)
    wxhb__vphs = bodo.libs.str_arr_ext.pre_alloc_string_array(ipnei__rzrg, -1)
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            bodo.libs.array_kernels.setna(wxhb__vphs, i)
            continue
        wxhb__vphs[i] = jxv__qje[i][start:stop:step]
    return init_dict_arr(wxhb__vphs, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    ipnei__rzrg = len(jxv__qje)
    kdqc__gtxen = len(pks__gmal)
    wxhb__vphs = pre_alloc_string_array(ipnei__rzrg, -1)
    ado__nluob = pre_alloc_string_array(kdqc__gtxen, -1)
    for flt__xmga in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, flt__xmga) or not -len(
            jxv__qje[flt__xmga]) <= i < len(jxv__qje[flt__xmga]):
            bodo.libs.array_kernels.setna(wxhb__vphs, flt__xmga)
            continue
        wxhb__vphs[flt__xmga] = jxv__qje[flt__xmga][i]
    for flt__xmga in range(kdqc__gtxen):
        if bodo.libs.array_kernels.isna(pks__gmal, flt__xmga
            ) or bodo.libs.array_kernels.isna(wxhb__vphs, pks__gmal[flt__xmga]
            ):
            bodo.libs.array_kernels.setna(ado__nluob, flt__xmga)
            continue
        ado__nluob[flt__xmga] = wxhb__vphs[pks__gmal[flt__xmga]]
    return ado__nluob


@register_jitable
def str_repeat_int(arr, repeats):
    jxv__qje = arr._data
    ipnei__rzrg = len(jxv__qje)
    wxhb__vphs = pre_alloc_string_array(ipnei__rzrg, -1)
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            bodo.libs.array_kernels.setna(wxhb__vphs, i)
            continue
        wxhb__vphs[i] = jxv__qje[i] * repeats
    return init_dict_arr(wxhb__vphs, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    iebnm__olete = f"""def str_{func_name}(arr):
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
    yzfgt__khh = {}
    exec(iebnm__olete, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, yzfgt__khh)
    return yzfgt__khh[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        cbs__xcblq = create_str2bool_methods(func_name)
        cbs__xcblq = register_jitable(cbs__xcblq)
        globals()[f'str_{func_name}'] = cbs__xcblq


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    jxv__qje = arr._data
    pks__gmal = arr._indices
    ipnei__rzrg = len(jxv__qje)
    kdqc__gtxen = len(pks__gmal)
    regex = re.compile(pat, flags=flags)
    qhvy__gpg = []
    for xnp__usemt in range(n_cols):
        qhvy__gpg.append(pre_alloc_string_array(ipnei__rzrg, -1))
    gfum__daf = bodo.libs.bool_arr_ext.alloc_bool_array(ipnei__rzrg)
    gtjg__mafqq = pks__gmal.copy()
    for i in range(ipnei__rzrg):
        if bodo.libs.array_kernels.isna(jxv__qje, i):
            gfum__daf[i] = True
            for flt__xmga in range(n_cols):
                bodo.libs.array_kernels.setna(qhvy__gpg[flt__xmga], i)
            continue
        nvf__uhw = regex.search(jxv__qje[i])
        if nvf__uhw:
            gfum__daf[i] = False
            jtjzv__lqm = nvf__uhw.groups()
            for flt__xmga in range(n_cols):
                qhvy__gpg[flt__xmga][i] = jtjzv__lqm[flt__xmga]
        else:
            gfum__daf[i] = True
            for flt__xmga in range(n_cols):
                bodo.libs.array_kernels.setna(qhvy__gpg[flt__xmga], i)
    for i in range(kdqc__gtxen):
        if gfum__daf[gtjg__mafqq[i]]:
            bodo.libs.array_kernels.setna(gtjg__mafqq, i)
    yyq__nava = [init_dict_arr(qhvy__gpg[i], gtjg__mafqq.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return yyq__nava


def create_extractall_methods(is_multi_group):
    fbwlz__isrqg = '_multi' if is_multi_group else ''
    iebnm__olete = f"""def str_extractall{fbwlz__isrqg}(arr, regex, n_cols, index_arr):
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
    yzfgt__khh = {}
    exec(iebnm__olete, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, yzfgt__khh)
    return yzfgt__khh[f'str_extractall{fbwlz__isrqg}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        fbwlz__isrqg = '_multi' if is_multi_group else ''
        cbs__xcblq = create_extractall_methods(is_multi_group)
        cbs__xcblq = register_jitable(cbs__xcblq)
        globals()[f'str_extractall{fbwlz__isrqg}'] = cbs__xcblq


_register_extractall_methods()
