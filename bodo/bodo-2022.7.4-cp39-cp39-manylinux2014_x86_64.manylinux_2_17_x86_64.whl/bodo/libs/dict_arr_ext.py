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
        fqlbh__wat = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, fqlbh__wat)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        cft__wozk, lrc__yistr, zxe__blao = args
        kye__agxl = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        kye__agxl.data = cft__wozk
        kye__agxl.indices = lrc__yistr
        kye__agxl.has_global_dictionary = zxe__blao
        context.nrt.incref(builder, signature.args[0], cft__wozk)
        context.nrt.incref(builder, signature.args[1], lrc__yistr)
        return kye__agxl._getvalue()
    jld__krbq = DictionaryArrayType(data_t)
    jsyof__eztsu = jld__krbq(data_t, indices_t, types.bool_)
    return jsyof__eztsu, codegen


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
        uvoa__farqo = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(uvoa__farqo, [val])
        c.pyapi.decref(uvoa__farqo)
    kye__agxl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vck__iay = c.pyapi.object_getattr_string(val, 'dictionary')
    ckx__grqht = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    pld__dno = c.pyapi.call_method(vck__iay, 'to_numpy', (ckx__grqht,))
    kye__agxl.data = c.unbox(typ.data, pld__dno).value
    dhnut__xdck = c.pyapi.object_getattr_string(val, 'indices')
    apei__htop = c.context.insert_const_string(c.builder.module, 'pandas')
    pcze__qtcp = c.pyapi.import_module_noblock(apei__htop)
    fgfs__zbj = c.pyapi.string_from_constant_string('Int32')
    izwjx__pbck = c.pyapi.call_method(pcze__qtcp, 'array', (dhnut__xdck,
        fgfs__zbj))
    kye__agxl.indices = c.unbox(dict_indices_arr_type, izwjx__pbck).value
    kye__agxl.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(vck__iay)
    c.pyapi.decref(ckx__grqht)
    c.pyapi.decref(pld__dno)
    c.pyapi.decref(dhnut__xdck)
    c.pyapi.decref(pcze__qtcp)
    c.pyapi.decref(fgfs__zbj)
    c.pyapi.decref(izwjx__pbck)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    hdtxt__pimby = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kye__agxl._getvalue(), is_error=hdtxt__pimby)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    kye__agxl = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, kye__agxl.data)
        ujrnp__lcukg = c.box(typ.data, kye__agxl.data)
        bxmh__swcgh = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, kye__agxl.indices)
        mmad__gaaye = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        qkz__kto = cgutils.get_or_insert_function(c.builder.module,
            mmad__gaaye, name='box_dict_str_array')
        sdfq__qgaj = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, bxmh__swcgh.data)
        zli__rrlmi = c.builder.extract_value(sdfq__qgaj.shape, 0)
        ooqmo__ayo = sdfq__qgaj.data
        wnabt__bztca = cgutils.create_struct_proxy(types.Array(types.int8, 
            1, 'C'))(c.context, c.builder, bxmh__swcgh.null_bitmap).data
        pld__dno = c.builder.call(qkz__kto, [zli__rrlmi, ujrnp__lcukg,
            ooqmo__ayo, wnabt__bztca])
        c.pyapi.decref(ujrnp__lcukg)
    else:
        apei__htop = c.context.insert_const_string(c.builder.module, 'pyarrow')
        ous__ngap = c.pyapi.import_module_noblock(apei__htop)
        zzt__hfs = c.pyapi.object_getattr_string(ous__ngap, 'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, kye__agxl.data)
        ujrnp__lcukg = c.box(typ.data, kye__agxl.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, kye__agxl.
            indices)
        dhnut__xdck = c.box(dict_indices_arr_type, kye__agxl.indices)
        lpnvo__dqwqw = c.pyapi.call_method(zzt__hfs, 'from_arrays', (
            dhnut__xdck, ujrnp__lcukg))
        ckx__grqht = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        pld__dno = c.pyapi.call_method(lpnvo__dqwqw, 'to_numpy', (ckx__grqht,))
        c.pyapi.decref(ous__ngap)
        c.pyapi.decref(ujrnp__lcukg)
        c.pyapi.decref(dhnut__xdck)
        c.pyapi.decref(zzt__hfs)
        c.pyapi.decref(lpnvo__dqwqw)
        c.pyapi.decref(ckx__grqht)
    c.context.nrt.decref(c.builder, typ, val)
    return pld__dno


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
    pbz__fea = pyval.dictionary.to_numpy(False)
    qxxo__vcav = pd.array(pyval.indices, 'Int32')
    pbz__fea = context.get_constant_generic(builder, typ.data, pbz__fea)
    qxxo__vcav = context.get_constant_generic(builder,
        dict_indices_arr_type, qxxo__vcav)
    vsda__hzad = context.get_constant(types.bool_, False)
    uohv__idvac = lir.Constant.literal_struct([pbz__fea, qxxo__vcav,
        vsda__hzad])
    return uohv__idvac


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            jbpb__gurca = A._indices[ind]
            return A._data[jbpb__gurca]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        cft__wozk = A._data
        lrc__yistr = A._indices
        zli__rrlmi = len(lrc__yistr)
        wtk__awfj = [get_str_arr_item_length(cft__wozk, i) for i in range(
            len(cft__wozk))]
        jeiul__yfet = 0
        for i in range(zli__rrlmi):
            if not bodo.libs.array_kernels.isna(lrc__yistr, i):
                jeiul__yfet += wtk__awfj[lrc__yistr[i]]
        fop__wcm = pre_alloc_string_array(zli__rrlmi, jeiul__yfet)
        for i in range(zli__rrlmi):
            if bodo.libs.array_kernels.isna(lrc__yistr, i):
                bodo.libs.array_kernels.setna(fop__wcm, i)
                continue
            ind = lrc__yistr[i]
            if bodo.libs.array_kernels.isna(cft__wozk, ind):
                bodo.libs.array_kernels.setna(fop__wcm, i)
                continue
            fop__wcm[i] = cft__wozk[ind]
        return fop__wcm
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    jbpb__gurca = -1
    cft__wozk = arr._data
    for i in range(len(cft__wozk)):
        if bodo.libs.array_kernels.isna(cft__wozk, i):
            continue
        if cft__wozk[i] == val:
            jbpb__gurca = i
            break
    return jbpb__gurca


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    zli__rrlmi = len(arr)
    jbpb__gurca = find_dict_ind(arr, val)
    if jbpb__gurca == -1:
        return init_bool_array(np.full(zli__rrlmi, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == jbpb__gurca


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    zli__rrlmi = len(arr)
    jbpb__gurca = find_dict_ind(arr, val)
    if jbpb__gurca == -1:
        return init_bool_array(np.full(zli__rrlmi, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != jbpb__gurca


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
        ivo__iqje = arr._data
        snfst__qzjp = bodo.libs.int_arr_ext.alloc_int_array(len(ivo__iqje),
            dtype)
        for xolo__rwv in range(len(ivo__iqje)):
            if bodo.libs.array_kernels.isna(ivo__iqje, xolo__rwv):
                bodo.libs.array_kernels.setna(snfst__qzjp, xolo__rwv)
                continue
            snfst__qzjp[xolo__rwv] = np.int64(ivo__iqje[xolo__rwv])
        zli__rrlmi = len(arr)
        lrc__yistr = arr._indices
        fop__wcm = bodo.libs.int_arr_ext.alloc_int_array(zli__rrlmi, dtype)
        for i in range(zli__rrlmi):
            if bodo.libs.array_kernels.isna(lrc__yistr, i):
                bodo.libs.array_kernels.setna(fop__wcm, i)
                continue
            fop__wcm[i] = snfst__qzjp[lrc__yistr[i]]
        return fop__wcm
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    vrlds__boqie = len(arrs)
    mqv__lyml = 'def impl(arrs, sep):\n'
    mqv__lyml += '  ind_map = {}\n'
    mqv__lyml += '  out_strs = []\n'
    mqv__lyml += '  n = len(arrs[0])\n'
    for i in range(vrlds__boqie):
        mqv__lyml += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(vrlds__boqie):
        mqv__lyml += f'  data{i} = arrs[{i}]._data\n'
    mqv__lyml += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    mqv__lyml += '  for i in range(n):\n'
    mig__toy = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(vrlds__boqie)])
    mqv__lyml += f'    if {mig__toy}:\n'
    mqv__lyml += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    mqv__lyml += '      continue\n'
    for i in range(vrlds__boqie):
        mqv__lyml += f'    ind{i} = indices{i}[i]\n'
    qre__oadm = '(' + ', '.join(f'ind{i}' for i in range(vrlds__boqie)) + ')'
    mqv__lyml += f'    if {qre__oadm} not in ind_map:\n'
    mqv__lyml += '      out_ind = len(out_strs)\n'
    mqv__lyml += f'      ind_map[{qre__oadm}] = out_ind\n'
    cme__qyhpd = "''" if is_overload_none(sep) else 'sep'
    mesiu__jjy = ', '.join([f'data{i}[ind{i}]' for i in range(vrlds__boqie)])
    mqv__lyml += f'      v = {cme__qyhpd}.join([{mesiu__jjy}])\n'
    mqv__lyml += '      out_strs.append(v)\n'
    mqv__lyml += '    else:\n'
    mqv__lyml += f'      out_ind = ind_map[{qre__oadm}]\n'
    mqv__lyml += '    out_indices[i] = out_ind\n'
    mqv__lyml += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    mqv__lyml += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    edjfv__ihg = {}
    exec(mqv__lyml, {'bodo': bodo, 'numba': numba, 'np': np}, edjfv__ihg)
    impl = edjfv__ihg['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    lum__ogwq = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    jsyof__eztsu = toty(fromty)
    xrdlh__bxkhc = context.compile_internal(builder, lum__ogwq,
        jsyof__eztsu, (val,))
    return impl_ret_new_ref(context, builder, toty, xrdlh__bxkhc)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    pbz__fea = arr._data
    ahhw__febkw = len(pbz__fea)
    jptpl__aqel = pre_alloc_string_array(ahhw__febkw, -1)
    if regex:
        ixfoc__qwg = re.compile(pat, flags)
        for i in range(ahhw__febkw):
            if bodo.libs.array_kernels.isna(pbz__fea, i):
                bodo.libs.array_kernels.setna(jptpl__aqel, i)
                continue
            jptpl__aqel[i] = ixfoc__qwg.sub(repl=repl, string=pbz__fea[i])
    else:
        for i in range(ahhw__febkw):
            if bodo.libs.array_kernels.isna(pbz__fea, i):
                bodo.libs.array_kernels.setna(jptpl__aqel, i)
                continue
            jptpl__aqel[i] = pbz__fea[i].replace(pat, repl)
    return init_dict_arr(jptpl__aqel, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    kye__agxl = arr._data
    gapy__kzce = len(kye__agxl)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gapy__kzce)
    for i in range(gapy__kzce):
        dict_arr_out[i] = kye__agxl[i].startswith(pat)
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    fop__wcm = bodo.libs.bool_arr_ext.alloc_bool_array(wea__xcm)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = dict_arr_out[qxxo__vcav[i]]
    return fop__wcm


@register_jitable
def str_endswith(arr, pat, na):
    kye__agxl = arr._data
    gapy__kzce = len(kye__agxl)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gapy__kzce)
    for i in range(gapy__kzce):
        dict_arr_out[i] = kye__agxl[i].endswith(pat)
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    fop__wcm = bodo.libs.bool_arr_ext.alloc_bool_array(wea__xcm)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = dict_arr_out[qxxo__vcav[i]]
    return fop__wcm


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    kye__agxl = arr._data
    adh__wjd = pd.Series(kye__agxl)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = adh__wjd.array._str_contains(pat, case, flags, na, regex
            )
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    fop__wcm = bodo.libs.bool_arr_ext.alloc_bool_array(wea__xcm)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = dict_arr_out[qxxo__vcav[i]]
    return fop__wcm


@register_jitable
def str_contains_non_regex(arr, pat, case):
    kye__agxl = arr._data
    gapy__kzce = len(kye__agxl)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gapy__kzce)
    if not case:
        fyea__aau = pat.upper()
    for i in range(gapy__kzce):
        if case:
            dict_arr_out[i] = pat in kye__agxl[i]
        else:
            dict_arr_out[i] = fyea__aau in kye__agxl[i].upper()
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    fop__wcm = bodo.libs.bool_arr_ext.alloc_bool_array(wea__xcm)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = dict_arr_out[qxxo__vcav[i]]
    return fop__wcm


@numba.njit
def str_match(arr, pat, case, flags, na):
    kye__agxl = arr._data
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    fop__wcm = bodo.libs.bool_arr_ext.alloc_bool_array(wea__xcm)
    adh__wjd = pd.Series(kye__agxl)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = adh__wjd.array._str_match(pat, case, flags, na)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = dict_arr_out[qxxo__vcav[i]]
    return fop__wcm


def create_simple_str2str_methods(func_name, func_args):
    mqv__lyml = f"""def str_{func_name}({', '.join(func_args)}):
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
    edjfv__ihg = {}
    exec(mqv__lyml, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, edjfv__ihg)
    return edjfv__ihg[f'str_{func_name}']


def _register_simple_str2str_methods():
    buh__unj = {**dict.fromkeys(['capitalize', 'lower', 'swapcase', 'title',
        'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip', 'strip'],
        ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust', 'rjust'],
        ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'], ('arr',
        'width'))}
    for func_name in buh__unj.keys():
        btfaf__pfwu = create_simple_str2str_methods(func_name, buh__unj[
            func_name])
        btfaf__pfwu = register_jitable(btfaf__pfwu)
        globals()[f'str_{func_name}'] = btfaf__pfwu


_register_simple_str2str_methods()


@register_jitable
def str_index(arr, sub, start, end):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    ahhw__febkw = len(pbz__fea)
    wea__xcm = len(qxxo__vcav)
    tlpya__cbhw = bodo.libs.int_arr_ext.alloc_int_array(ahhw__febkw, np.int64)
    fop__wcm = bodo.libs.int_arr_ext.alloc_int_array(wea__xcm, np.int64)
    dkyrx__ngvdf = False
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            bodo.libs.array_kernels.setna(tlpya__cbhw, i)
        else:
            tlpya__cbhw[i] = pbz__fea[i].find(sub, start, end)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(tlpya__cbhw, qxxo__vcav[i]):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = tlpya__cbhw[qxxo__vcav[i]]
            if fop__wcm[i] == -1:
                dkyrx__ngvdf = True
    dnh__efe = 'substring not found' if dkyrx__ngvdf else ''
    synchronize_error_njit('ValueError', dnh__efe)
    return fop__wcm


@register_jitable
def str_rindex(arr, sub, start, end):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    ahhw__febkw = len(pbz__fea)
    wea__xcm = len(qxxo__vcav)
    tlpya__cbhw = bodo.libs.int_arr_ext.alloc_int_array(ahhw__febkw, np.int64)
    fop__wcm = bodo.libs.int_arr_ext.alloc_int_array(wea__xcm, np.int64)
    dkyrx__ngvdf = False
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            bodo.libs.array_kernels.setna(tlpya__cbhw, i)
        else:
            tlpya__cbhw[i] = pbz__fea[i].rindex(sub, start, end)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(arr, i
            ) or bodo.libs.array_kernels.isna(tlpya__cbhw, qxxo__vcav[i]):
            bodo.libs.array_kernels.setna(fop__wcm, i)
        else:
            fop__wcm[i] = tlpya__cbhw[qxxo__vcav[i]]
            if fop__wcm[i] == -1:
                dkyrx__ngvdf = True
    dnh__efe = 'substring not found' if dkyrx__ngvdf else ''
    synchronize_error_njit('ValueError', dnh__efe)
    return fop__wcm


def create_find_methods(func_name):
    mqv__lyml = f"""def str_{func_name}(arr, sub, start, end):
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
    edjfv__ihg = {}
    exec(mqv__lyml, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, edjfv__ihg)
    return edjfv__ihg[f'str_{func_name}']


def _register_find_methods():
    cbl__epvol = ['find', 'rfind']
    for func_name in cbl__epvol:
        btfaf__pfwu = create_find_methods(func_name)
        btfaf__pfwu = register_jitable(btfaf__pfwu)
        globals()[f'str_{func_name}'] = btfaf__pfwu


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    ahhw__febkw = len(pbz__fea)
    wea__xcm = len(qxxo__vcav)
    tlpya__cbhw = bodo.libs.int_arr_ext.alloc_int_array(ahhw__febkw, np.int64)
    onutq__eei = bodo.libs.int_arr_ext.alloc_int_array(wea__xcm, np.int64)
    regex = re.compile(pat, flags)
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            bodo.libs.array_kernels.setna(tlpya__cbhw, i)
            continue
        tlpya__cbhw[i] = bodo.libs.str_ext.str_findall_count(regex, pbz__fea[i]
            )
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(qxxo__vcav, i
            ) or bodo.libs.array_kernels.isna(tlpya__cbhw, qxxo__vcav[i]):
            bodo.libs.array_kernels.setna(onutq__eei, i)
        else:
            onutq__eei[i] = tlpya__cbhw[qxxo__vcav[i]]
    return onutq__eei


@register_jitable
def str_len(arr):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    wea__xcm = len(qxxo__vcav)
    tlpya__cbhw = bodo.libs.array_kernels.get_arr_lens(pbz__fea, False)
    onutq__eei = bodo.libs.int_arr_ext.alloc_int_array(wea__xcm, np.int64)
    for i in range(wea__xcm):
        if bodo.libs.array_kernels.isna(qxxo__vcav, i
            ) or bodo.libs.array_kernels.isna(tlpya__cbhw, qxxo__vcav[i]):
            bodo.libs.array_kernels.setna(onutq__eei, i)
        else:
            onutq__eei[i] = tlpya__cbhw[qxxo__vcav[i]]
    return onutq__eei


@register_jitable
def str_slice(arr, start, stop, step):
    pbz__fea = arr._data
    ahhw__febkw = len(pbz__fea)
    jptpl__aqel = bodo.libs.str_arr_ext.pre_alloc_string_array(ahhw__febkw, -1)
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            bodo.libs.array_kernels.setna(jptpl__aqel, i)
            continue
        jptpl__aqel[i] = pbz__fea[i][start:stop:step]
    return init_dict_arr(jptpl__aqel, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    ahhw__febkw = len(pbz__fea)
    wea__xcm = len(qxxo__vcav)
    jptpl__aqel = pre_alloc_string_array(ahhw__febkw, -1)
    fop__wcm = pre_alloc_string_array(wea__xcm, -1)
    for xolo__rwv in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, xolo__rwv) or not -len(
            pbz__fea[xolo__rwv]) <= i < len(pbz__fea[xolo__rwv]):
            bodo.libs.array_kernels.setna(jptpl__aqel, xolo__rwv)
            continue
        jptpl__aqel[xolo__rwv] = pbz__fea[xolo__rwv][i]
    for xolo__rwv in range(wea__xcm):
        if bodo.libs.array_kernels.isna(qxxo__vcav, xolo__rwv
            ) or bodo.libs.array_kernels.isna(jptpl__aqel, qxxo__vcav[
            xolo__rwv]):
            bodo.libs.array_kernels.setna(fop__wcm, xolo__rwv)
            continue
        fop__wcm[xolo__rwv] = jptpl__aqel[qxxo__vcav[xolo__rwv]]
    return fop__wcm


@register_jitable
def str_repeat_int(arr, repeats):
    pbz__fea = arr._data
    ahhw__febkw = len(pbz__fea)
    jptpl__aqel = pre_alloc_string_array(ahhw__febkw, -1)
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            bodo.libs.array_kernels.setna(jptpl__aqel, i)
            continue
        jptpl__aqel[i] = pbz__fea[i] * repeats
    return init_dict_arr(jptpl__aqel, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    mqv__lyml = f"""def str_{func_name}(arr):
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
    edjfv__ihg = {}
    exec(mqv__lyml, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, edjfv__ihg)
    return edjfv__ihg[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        btfaf__pfwu = create_str2bool_methods(func_name)
        btfaf__pfwu = register_jitable(btfaf__pfwu)
        globals()[f'str_{func_name}'] = btfaf__pfwu


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    pbz__fea = arr._data
    qxxo__vcav = arr._indices
    ahhw__febkw = len(pbz__fea)
    wea__xcm = len(qxxo__vcav)
    regex = re.compile(pat, flags=flags)
    dldv__krv = []
    for vdvyt__twmfe in range(n_cols):
        dldv__krv.append(pre_alloc_string_array(ahhw__febkw, -1))
    yzqi__zryr = bodo.libs.bool_arr_ext.alloc_bool_array(ahhw__febkw)
    lfm__ghfi = qxxo__vcav.copy()
    for i in range(ahhw__febkw):
        if bodo.libs.array_kernels.isna(pbz__fea, i):
            yzqi__zryr[i] = True
            for xolo__rwv in range(n_cols):
                bodo.libs.array_kernels.setna(dldv__krv[xolo__rwv], i)
            continue
        dzvy__ijt = regex.search(pbz__fea[i])
        if dzvy__ijt:
            yzqi__zryr[i] = False
            pmykl__eta = dzvy__ijt.groups()
            for xolo__rwv in range(n_cols):
                dldv__krv[xolo__rwv][i] = pmykl__eta[xolo__rwv]
        else:
            yzqi__zryr[i] = True
            for xolo__rwv in range(n_cols):
                bodo.libs.array_kernels.setna(dldv__krv[xolo__rwv], i)
    for i in range(wea__xcm):
        if yzqi__zryr[lfm__ghfi[i]]:
            bodo.libs.array_kernels.setna(lfm__ghfi, i)
    seo__yaaj = [init_dict_arr(dldv__krv[i], lfm__ghfi.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return seo__yaaj


def create_extractall_methods(is_multi_group):
    hucta__kmfn = '_multi' if is_multi_group else ''
    mqv__lyml = f"""def str_extractall{hucta__kmfn}(arr, regex, n_cols, index_arr):
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
    edjfv__ihg = {}
    exec(mqv__lyml, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, edjfv__ihg)
    return edjfv__ihg[f'str_extractall{hucta__kmfn}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        hucta__kmfn = '_multi' if is_multi_group else ''
        btfaf__pfwu = create_extractall_methods(is_multi_group)
        btfaf__pfwu = register_jitable(btfaf__pfwu)
        globals()[f'str_extractall{hucta__kmfn}'] = btfaf__pfwu


_register_extractall_methods()
