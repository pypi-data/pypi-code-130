"""Array of tuple values, implemented by reusing array of structs implementation.
"""
import operator
import numba
import numpy as np
from numba.core import types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.struct_arr_ext import StructArrayType, box_struct_arr, unbox_struct_array


class TupleArrayType(types.ArrayCompatible):

    def __init__(self, data):
        self.data = data
        super(TupleArrayType, self).__init__(name='TupleArrayType({})'.
            format(data))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.BaseTuple.from_types(tuple(bcin__oguct.dtype for
            bcin__oguct in self.data))

    def copy(self):
        return TupleArrayType(self.data)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(TupleArrayType)
class TupleArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iaw__uewvq = [('data', StructArrayType(fe_type.data))]
        models.StructModel.__init__(self, dmm, fe_type, iaw__uewvq)


make_attribute_wrapper(TupleArrayType, 'data', '_data')


@intrinsic
def init_tuple_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, StructArrayType)
    nvgv__kwuku = TupleArrayType(data_typ.data)

    def codegen(context, builder, sig, args):
        mjmk__wbp, = args
        iqhr__qnjg = context.make_helper(builder, nvgv__kwuku)
        iqhr__qnjg.data = mjmk__wbp
        context.nrt.incref(builder, data_typ, mjmk__wbp)
        return iqhr__qnjg._getvalue()
    return nvgv__kwuku(data_typ), codegen


@unbox(TupleArrayType)
def unbox_tuple_array(typ, val, c):
    data_typ = StructArrayType(typ.data)
    spbg__pteyb = unbox_struct_array(data_typ, val, c, is_tuple_array=True)
    mjmk__wbp = spbg__pteyb.value
    iqhr__qnjg = c.context.make_helper(c.builder, typ)
    iqhr__qnjg.data = mjmk__wbp
    qclyh__yxea = spbg__pteyb.is_error
    return NativeValue(iqhr__qnjg._getvalue(), is_error=qclyh__yxea)


@box(TupleArrayType)
def box_tuple_arr(typ, val, c):
    data_typ = StructArrayType(typ.data)
    iqhr__qnjg = c.context.make_helper(c.builder, typ, val)
    arr = box_struct_arr(data_typ, iqhr__qnjg.data, c, is_tuple_array=True)
    return arr


@numba.njit
def pre_alloc_tuple_array(n, nested_counts, dtypes):
    return init_tuple_arr(bodo.libs.struct_arr_ext.pre_alloc_struct_array(n,
        nested_counts, dtypes, None))


def pre_alloc_tuple_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_tuple_arr_ext_pre_alloc_tuple_array
    ) = pre_alloc_tuple_array_equiv


@overload(operator.getitem, no_unliteral=True)
def tuple_arr_getitem(arr, ind):
    if not isinstance(arr, TupleArrayType):
        return
    if isinstance(ind, types.Integer):
        qxx__ukmi = 'def impl(arr, ind):\n'
        fzv__pnp = ','.join(f'get_data(arr._data)[{tysuq__bsylm}][ind]' for
            tysuq__bsylm in range(len(arr.data)))
        qxx__ukmi += f'  return ({fzv__pnp})\n'
        qxcwx__roby = {}
        exec(qxx__ukmi, {'get_data': bodo.libs.struct_arr_ext.get_data},
            qxcwx__roby)
        byrl__rihub = qxcwx__roby['impl']
        return byrl__rihub

    def impl_arr(arr, ind):
        return init_tuple_arr(arr._data[ind])
    return impl_arr


@overload(operator.setitem, no_unliteral=True)
def tuple_arr_setitem(arr, ind, val):
    if not isinstance(arr, TupleArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        zhzh__rahjc = len(arr.data)
        qxx__ukmi = 'def impl(arr, ind, val):\n'
        qxx__ukmi += '  data = get_data(arr._data)\n'
        qxx__ukmi += '  null_bitmap = get_null_bitmap(arr._data)\n'
        qxx__ukmi += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for tysuq__bsylm in range(zhzh__rahjc):
            qxx__ukmi += f'  data[{tysuq__bsylm}][ind] = val[{tysuq__bsylm}]\n'
        qxcwx__roby = {}
        exec(qxx__ukmi, {'get_data': bodo.libs.struct_arr_ext.get_data,
            'get_null_bitmap': bodo.libs.struct_arr_ext.get_null_bitmap,
            'set_bit_to_arr': bodo.libs.int_arr_ext.set_bit_to_arr},
            qxcwx__roby)
        byrl__rihub = qxcwx__roby['impl']
        return byrl__rihub

    def impl_arr(arr, ind, val):
        val = bodo.utils.conversion.coerce_to_array(val, use_nullable_array
            =True)
        arr._data[ind] = val._data
    return impl_arr


@overload(len, no_unliteral=True)
def overload_tuple_arr_len(A):
    if isinstance(A, TupleArrayType):
        return lambda A: len(A._data)


@overload_attribute(TupleArrayType, 'shape')
def overload_tuple_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(TupleArrayType, 'dtype')
def overload_tuple_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(TupleArrayType, 'ndim')
def overload_tuple_arr_ndim(A):
    return lambda A: 1


@overload_attribute(TupleArrayType, 'nbytes')
def overload_tuple_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(TupleArrayType, 'copy', no_unliteral=True)
def overload_tuple_arr_copy(A):

    def copy_impl(A):
        return init_tuple_arr(A._data.copy())
    return copy_impl
