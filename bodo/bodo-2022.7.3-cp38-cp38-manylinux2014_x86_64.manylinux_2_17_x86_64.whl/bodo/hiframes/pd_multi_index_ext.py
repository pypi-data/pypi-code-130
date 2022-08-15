"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.ArrayCompatible):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        khrqa__auty = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, khrqa__auty)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[yjb__qfmhr].values) for
        yjb__qfmhr in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (wqla__hkqu) for wqla__hkqu in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    hsn__bzy = c.context.insert_const_string(c.builder.module, 'pandas')
    sic__zjtuj = c.pyapi.import_module_noblock(hsn__bzy)
    epmh__cxed = c.pyapi.object_getattr_string(sic__zjtuj, 'MultiIndex')
    has__emj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), has__emj.data
        )
    hlv__auky = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        has__emj.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), has__emj.names)
    gpu__ivw = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        has__emj.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, has__emj.name)
    tdyw__xqplu = c.pyapi.from_native_value(typ.name_typ, has__emj.name, c.
        env_manager)
    rac__kxvgp = c.pyapi.borrow_none()
    bjt__cls = c.pyapi.call_method(epmh__cxed, 'from_arrays', (hlv__auky,
        rac__kxvgp, gpu__ivw))
    c.pyapi.object_setattr_string(bjt__cls, 'name', tdyw__xqplu)
    c.pyapi.decref(hlv__auky)
    c.pyapi.decref(gpu__ivw)
    c.pyapi.decref(tdyw__xqplu)
    c.pyapi.decref(sic__zjtuj)
    c.pyapi.decref(epmh__cxed)
    c.context.nrt.decref(c.builder, typ, val)
    return bjt__cls


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    vng__sjm = []
    vbjm__tkuum = []
    for yjb__qfmhr in range(typ.nlevels):
        fhd__tpxb = c.pyapi.unserialize(c.pyapi.serialize_object(yjb__qfmhr))
        fpx__nznzk = c.pyapi.call_method(val, 'get_level_values', (fhd__tpxb,))
        zmc__emb = c.pyapi.object_getattr_string(fpx__nznzk, 'values')
        c.pyapi.decref(fpx__nznzk)
        c.pyapi.decref(fhd__tpxb)
        feo__hqu = c.pyapi.to_native_value(typ.array_types[yjb__qfmhr],
            zmc__emb).value
        vng__sjm.append(feo__hqu)
        vbjm__tkuum.append(zmc__emb)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, vng__sjm)
    else:
        data = cgutils.pack_struct(c.builder, vng__sjm)
    gpu__ivw = c.pyapi.object_getattr_string(val, 'names')
    pfgmj__zph = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    hsnya__uot = c.pyapi.call_function_objargs(pfgmj__zph, (gpu__ivw,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), hsnya__uot
        ).value
    tdyw__xqplu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, tdyw__xqplu).value
    has__emj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    has__emj.data = data
    has__emj.names = names
    has__emj.name = name
    for zmc__emb in vbjm__tkuum:
        c.pyapi.decref(zmc__emb)
    c.pyapi.decref(gpu__ivw)
    c.pyapi.decref(pfgmj__zph)
    c.pyapi.decref(hsnya__uot)
    c.pyapi.decref(tdyw__xqplu)
    return NativeValue(has__emj._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    pbxi__pfolu = 'pandas.MultiIndex.from_product'
    agopu__vmmhy = dict(sortorder=sortorder)
    fqijc__nfym = dict(sortorder=None)
    check_unsupported_args(pbxi__pfolu, agopu__vmmhy, fqijc__nfym,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{pbxi__pfolu}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{pbxi__pfolu}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{pbxi__pfolu}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    fikj__vhb = MultiIndexType(array_types, names_typ)
    diwei__cqkcl = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, diwei__cqkcl, fikj__vhb)
    kng__djkki = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{diwei__cqkcl}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    tykee__ljy = {}
    exec(kng__djkki, globals(), tykee__ljy)
    uts__kttf = tykee__ljy['impl']
    return uts__kttf


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        evk__sgd, yrc__hel, hmd__yfx = args
        kqvlo__hibnv = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        kqvlo__hibnv.data = evk__sgd
        kqvlo__hibnv.names = yrc__hel
        kqvlo__hibnv.name = hmd__yfx
        context.nrt.incref(builder, signature.args[0], evk__sgd)
        context.nrt.incref(builder, signature.args[1], yrc__hel)
        context.nrt.incref(builder, signature.args[2], hmd__yfx)
        return kqvlo__hibnv._getvalue()
    hbqjc__kdeyy = MultiIndexType(data.types, names.types, name)
    return hbqjc__kdeyy(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        srv__kfjg = len(I.array_types)
        kng__djkki = 'def impl(I, ind):\n'
        kng__djkki += '  data = I._data\n'
        kng__djkki += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{yjb__qfmhr}][ind])' for yjb__qfmhr in
            range(srv__kfjg))))
        tykee__ljy = {}
        exec(kng__djkki, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, tykee__ljy)
        uts__kttf = tykee__ljy['impl']
        return uts__kttf


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    sauj__ezv, sdx__jljh = sig.args
    if sauj__ezv != sdx__jljh:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
