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
        ioja__dnk = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, ioja__dnk)


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
        xnfkw__wgq = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        xnfkw__wgq.data = data_tuple
        xnfkw__wgq.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return xnfkw__wgq._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    gnzo__rdz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, gnzo__rdz.data)
    c.context.nrt.incref(c.builder, typ.null_typ, gnzo__rdz.null_values)
    vurd__cdi = c.pyapi.from_native_value(typ.tuple_typ, gnzo__rdz.data, c.
        env_manager)
    rmvt__cgp = c.pyapi.from_native_value(typ.null_typ, gnzo__rdz.
        null_values, c.env_manager)
    vrtq__gskt = c.context.get_constant(types.int64, len(typ.tuple_typ))
    edu__vad = c.pyapi.list_new(vrtq__gskt)
    with cgutils.for_range(c.builder, vrtq__gskt) as mmdep__ayplg:
        i = mmdep__ayplg.index
        zjrs__revcx = c.pyapi.long_from_longlong(i)
        khf__bbm = c.pyapi.object_getitem(rmvt__cgp, zjrs__revcx)
        lick__cuzi = c.pyapi.to_native_value(types.bool_, khf__bbm).value
        with c.builder.if_else(lick__cuzi) as (hrqk__rtui, cfjn__exk):
            with hrqk__rtui:
                c.pyapi.list_setitem(edu__vad, i, c.pyapi.make_none())
            with cfjn__exk:
                vex__vlb = c.pyapi.object_getitem(vurd__cdi, zjrs__revcx)
                c.pyapi.list_setitem(edu__vad, i, vex__vlb)
        c.pyapi.decref(zjrs__revcx)
        c.pyapi.decref(khf__bbm)
    krwy__xcfa = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    ucsg__zey = c.pyapi.call_function_objargs(krwy__xcfa, (edu__vad,))
    c.pyapi.decref(vurd__cdi)
    c.pyapi.decref(rmvt__cgp)
    c.pyapi.decref(krwy__xcfa)
    c.pyapi.decref(edu__vad)
    c.context.nrt.decref(c.builder, typ, val)
    return ucsg__zey


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
    xnfkw__wgq = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (xnfkw__wgq.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    elf__xzzmo = 'def impl(val1, val2):\n'
    elf__xzzmo += '    data_tup1 = val1._data\n'
    elf__xzzmo += '    null_tup1 = val1._null_values\n'
    elf__xzzmo += '    data_tup2 = val2._data\n'
    elf__xzzmo += '    null_tup2 = val2._null_values\n'
    lpvm__jjhi = val1._tuple_typ
    for i in range(len(lpvm__jjhi)):
        elf__xzzmo += f'    null1_{i} = null_tup1[{i}]\n'
        elf__xzzmo += f'    null2_{i} = null_tup2[{i}]\n'
        elf__xzzmo += f'    data1_{i} = data_tup1[{i}]\n'
        elf__xzzmo += f'    data2_{i} = data_tup2[{i}]\n'
        elf__xzzmo += f'    if null1_{i} != null2_{i}:\n'
        elf__xzzmo += '        return False\n'
        elf__xzzmo += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        elf__xzzmo += f'        return False\n'
    elf__xzzmo += f'    return True\n'
    uyc__cwv = {}
    exec(elf__xzzmo, {}, uyc__cwv)
    impl = uyc__cwv['impl']
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
    elf__xzzmo = 'def impl(nullable_tup):\n'
    elf__xzzmo += '    data_tup = nullable_tup._data\n'
    elf__xzzmo += '    null_tup = nullable_tup._null_values\n'
    elf__xzzmo += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    elf__xzzmo += '    acc = _PyHASH_XXPRIME_5\n'
    lpvm__jjhi = nullable_tup._tuple_typ
    for i in range(len(lpvm__jjhi)):
        elf__xzzmo += f'    null_val_{i} = null_tup[{i}]\n'
        elf__xzzmo += f'    null_lane_{i} = hash(null_val_{i})\n'
        elf__xzzmo += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        elf__xzzmo += '        return -1\n'
        elf__xzzmo += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        elf__xzzmo += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        elf__xzzmo += '    acc *= _PyHASH_XXPRIME_1\n'
        elf__xzzmo += f'    if not null_val_{i}:\n'
        elf__xzzmo += f'        lane_{i} = hash(data_tup[{i}])\n'
        elf__xzzmo += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        elf__xzzmo += f'            return -1\n'
        elf__xzzmo += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        elf__xzzmo += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        elf__xzzmo += '        acc *= _PyHASH_XXPRIME_1\n'
    elf__xzzmo += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    elf__xzzmo += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    elf__xzzmo += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    elf__xzzmo += '    return numba.cpython.hashing.process_return(acc)\n'
    uyc__cwv = {}
    exec(elf__xzzmo, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, uyc__cwv)
    impl = uyc__cwv['impl']
    return impl
