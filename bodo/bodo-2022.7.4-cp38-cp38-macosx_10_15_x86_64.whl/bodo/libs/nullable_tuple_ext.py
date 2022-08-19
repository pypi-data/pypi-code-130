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
        jqj__roz = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, jqj__roz)


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
        xkxx__sbuqr = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        xkxx__sbuqr.data = data_tuple
        xkxx__sbuqr.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return xkxx__sbuqr._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    bhnq__gjua = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, bhnq__gjua.data)
    c.context.nrt.incref(c.builder, typ.null_typ, bhnq__gjua.null_values)
    hwm__sme = c.pyapi.from_native_value(typ.tuple_typ, bhnq__gjua.data, c.
        env_manager)
    fyk__jgeim = c.pyapi.from_native_value(typ.null_typ, bhnq__gjua.
        null_values, c.env_manager)
    bzty__xuj = c.context.get_constant(types.int64, len(typ.tuple_typ))
    xau__jnxtu = c.pyapi.list_new(bzty__xuj)
    with cgutils.for_range(c.builder, bzty__xuj) as novu__dzdv:
        i = novu__dzdv.index
        ghy__ylzf = c.pyapi.long_from_longlong(i)
        vkpiu__qigza = c.pyapi.object_getitem(fyk__jgeim, ghy__ylzf)
        iqsn__iqurq = c.pyapi.to_native_value(types.bool_, vkpiu__qigza).value
        with c.builder.if_else(iqsn__iqurq) as (ujeh__qcgad, mzzoo__smtxt):
            with ujeh__qcgad:
                c.pyapi.list_setitem(xau__jnxtu, i, c.pyapi.make_none())
            with mzzoo__smtxt:
                vllqs__fyfs = c.pyapi.object_getitem(hwm__sme, ghy__ylzf)
                c.pyapi.list_setitem(xau__jnxtu, i, vllqs__fyfs)
        c.pyapi.decref(ghy__ylzf)
        c.pyapi.decref(vkpiu__qigza)
    dmi__aucn = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    kpi__ghhkc = c.pyapi.call_function_objargs(dmi__aucn, (xau__jnxtu,))
    c.pyapi.decref(hwm__sme)
    c.pyapi.decref(fyk__jgeim)
    c.pyapi.decref(dmi__aucn)
    c.pyapi.decref(xau__jnxtu)
    c.context.nrt.decref(c.builder, typ, val)
    return kpi__ghhkc


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
    xkxx__sbuqr = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (xkxx__sbuqr.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    fsbdl__vwoe = 'def impl(val1, val2):\n'
    fsbdl__vwoe += '    data_tup1 = val1._data\n'
    fsbdl__vwoe += '    null_tup1 = val1._null_values\n'
    fsbdl__vwoe += '    data_tup2 = val2._data\n'
    fsbdl__vwoe += '    null_tup2 = val2._null_values\n'
    sblda__zcqx = val1._tuple_typ
    for i in range(len(sblda__zcqx)):
        fsbdl__vwoe += f'    null1_{i} = null_tup1[{i}]\n'
        fsbdl__vwoe += f'    null2_{i} = null_tup2[{i}]\n'
        fsbdl__vwoe += f'    data1_{i} = data_tup1[{i}]\n'
        fsbdl__vwoe += f'    data2_{i} = data_tup2[{i}]\n'
        fsbdl__vwoe += f'    if null1_{i} != null2_{i}:\n'
        fsbdl__vwoe += '        return False\n'
        fsbdl__vwoe += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        fsbdl__vwoe += f'        return False\n'
    fsbdl__vwoe += f'    return True\n'
    ufjb__gqbk = {}
    exec(fsbdl__vwoe, {}, ufjb__gqbk)
    impl = ufjb__gqbk['impl']
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
    fsbdl__vwoe = 'def impl(nullable_tup):\n'
    fsbdl__vwoe += '    data_tup = nullable_tup._data\n'
    fsbdl__vwoe += '    null_tup = nullable_tup._null_values\n'
    fsbdl__vwoe += (
        '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n')
    fsbdl__vwoe += '    acc = _PyHASH_XXPRIME_5\n'
    sblda__zcqx = nullable_tup._tuple_typ
    for i in range(len(sblda__zcqx)):
        fsbdl__vwoe += f'    null_val_{i} = null_tup[{i}]\n'
        fsbdl__vwoe += f'    null_lane_{i} = hash(null_val_{i})\n'
        fsbdl__vwoe += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        fsbdl__vwoe += '        return -1\n'
        fsbdl__vwoe += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        fsbdl__vwoe += (
            '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        fsbdl__vwoe += '    acc *= _PyHASH_XXPRIME_1\n'
        fsbdl__vwoe += f'    if not null_val_{i}:\n'
        fsbdl__vwoe += f'        lane_{i} = hash(data_tup[{i}])\n'
        fsbdl__vwoe += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        fsbdl__vwoe += f'            return -1\n'
        fsbdl__vwoe += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        fsbdl__vwoe += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        fsbdl__vwoe += '        acc *= _PyHASH_XXPRIME_1\n'
    fsbdl__vwoe += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    fsbdl__vwoe += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    fsbdl__vwoe += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    fsbdl__vwoe += '    return numba.cpython.hashing.process_return(acc)\n'
    ufjb__gqbk = {}
    exec(fsbdl__vwoe, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, ufjb__gqbk)
    impl = ufjb__gqbk['impl']
    return impl
