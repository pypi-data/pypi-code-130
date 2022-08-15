"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type

    def __len__(self):
        return len(self.tuple_typ)


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yjpio__ukcje = [('data', fe_type.tuple_typ), ('null_values',
            fe_type.null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, yjpio__ukcje)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        wyyc__ryj = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        wyyc__ryj.data = data_tuple
        wyyc__ryj.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return wyyc__ryj._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    alo__vzu = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, alo__vzu.data)
    c.context.nrt.incref(c.builder, typ.null_typ, alo__vzu.null_values)
    oiu__ojl = c.pyapi.from_native_value(typ.tuple_typ, alo__vzu.data, c.
        env_manager)
    kggkl__tpyhy = c.pyapi.from_native_value(typ.null_typ, alo__vzu.
        null_values, c.env_manager)
    pnx__dbf = c.context.get_constant(types.int64, len(typ.tuple_typ))
    vffx__cnps = c.pyapi.list_new(pnx__dbf)
    with cgutils.for_range(c.builder, pnx__dbf) as qqyv__lhfmh:
        i = qqyv__lhfmh.index
        ugo__yfbn = c.pyapi.long_from_longlong(i)
        cavyc__fjhrw = c.pyapi.object_getitem(kggkl__tpyhy, ugo__yfbn)
        lteg__huj = c.pyapi.to_native_value(types.bool_, cavyc__fjhrw).value
        with c.builder.if_else(lteg__huj) as (agai__ycu, gpy__tnzx):
            with agai__ycu:
                c.pyapi.list_setitem(vffx__cnps, i, c.pyapi.make_none())
            with gpy__tnzx:
                ljrkj__fkupa = c.pyapi.object_getitem(oiu__ojl, ugo__yfbn)
                c.pyapi.list_setitem(vffx__cnps, i, ljrkj__fkupa)
        c.pyapi.decref(ugo__yfbn)
        c.pyapi.decref(cavyc__fjhrw)
    ievc__rkb = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    sjof__btq = c.pyapi.call_function_objargs(ievc__rkb, (vffx__cnps,))
    c.pyapi.decref(oiu__ojl)
    c.pyapi.decref(kggkl__tpyhy)
    c.pyapi.decref(ievc__rkb)
    c.pyapi.decref(vffx__cnps)
    c.context.nrt.decref(c.builder, typ, val)
    return sjof__btq


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    wyyc__ryj = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (wyyc__ryj.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    sstru__gmdp = 'def impl(val1, val2):\n'
    sstru__gmdp += '    data_tup1 = val1._data\n'
    sstru__gmdp += '    null_tup1 = val1._null_values\n'
    sstru__gmdp += '    data_tup2 = val2._data\n'
    sstru__gmdp += '    null_tup2 = val2._null_values\n'
    xrg__lwpke = val1._tuple_typ
    for i in range(len(xrg__lwpke)):
        sstru__gmdp += f'    null1_{i} = null_tup1[{i}]\n'
        sstru__gmdp += f'    null2_{i} = null_tup2[{i}]\n'
        sstru__gmdp += f'    data1_{i} = data_tup1[{i}]\n'
        sstru__gmdp += f'    data2_{i} = data_tup2[{i}]\n'
        sstru__gmdp += f'    if null1_{i} != null2_{i}:\n'
        sstru__gmdp += '        return False\n'
        sstru__gmdp += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        sstru__gmdp += f'        return False\n'
    sstru__gmdp += f'    return True\n'
    mrdl__tboo = {}
    exec(sstru__gmdp, {}, mrdl__tboo)
    impl = mrdl__tboo['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    sstru__gmdp = 'def impl(nullable_tup):\n'
    sstru__gmdp += '    data_tup = nullable_tup._data\n'
    sstru__gmdp += '    null_tup = nullable_tup._null_values\n'
    sstru__gmdp += (
        '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n')
    sstru__gmdp += '    acc = _PyHASH_XXPRIME_5\n'
    xrg__lwpke = nullable_tup._tuple_typ
    for i in range(len(xrg__lwpke)):
        sstru__gmdp += f'    null_val_{i} = null_tup[{i}]\n'
        sstru__gmdp += f'    null_lane_{i} = hash(null_val_{i})\n'
        sstru__gmdp += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        sstru__gmdp += '        return -1\n'
        sstru__gmdp += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        sstru__gmdp += (
            '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        sstru__gmdp += '    acc *= _PyHASH_XXPRIME_1\n'
        sstru__gmdp += f'    if not null_val_{i}:\n'
        sstru__gmdp += f'        lane_{i} = hash(data_tup[{i}])\n'
        sstru__gmdp += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        sstru__gmdp += f'            return -1\n'
        sstru__gmdp += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        sstru__gmdp += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        sstru__gmdp += '        acc *= _PyHASH_XXPRIME_1\n'
    sstru__gmdp += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    sstru__gmdp += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    sstru__gmdp += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    sstru__gmdp += '    return numba.cpython.hashing.process_return(acc)\n'
    mrdl__tboo = {}
    exec(sstru__gmdp, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, mrdl__tboo)
    impl = mrdl__tboo['impl']
    return impl
