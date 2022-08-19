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
        ccika__pesv = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, ccika__pesv)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[zapw__vdo].values) for
        zapw__vdo in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (xgzok__azzr) for xgzok__azzr in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    oiom__whwp = c.context.insert_const_string(c.builder.module, 'pandas')
    oqa__rwxof = c.pyapi.import_module_noblock(oiom__whwp)
    llz__odb = c.pyapi.object_getattr_string(oqa__rwxof, 'MultiIndex')
    nwopp__vcxqm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        nwopp__vcxqm.data)
    wphk__buwi = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        nwopp__vcxqm.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ),
        nwopp__vcxqm.names)
    czlz__mcxf = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        nwopp__vcxqm.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, nwopp__vcxqm.name)
    bbb__ixo = c.pyapi.from_native_value(typ.name_typ, nwopp__vcxqm.name, c
        .env_manager)
    fcvbl__lzl = c.pyapi.borrow_none()
    gptj__udjej = c.pyapi.call_method(llz__odb, 'from_arrays', (wphk__buwi,
        fcvbl__lzl, czlz__mcxf))
    c.pyapi.object_setattr_string(gptj__udjej, 'name', bbb__ixo)
    c.pyapi.decref(wphk__buwi)
    c.pyapi.decref(czlz__mcxf)
    c.pyapi.decref(bbb__ixo)
    c.pyapi.decref(oqa__rwxof)
    c.pyapi.decref(llz__odb)
    c.context.nrt.decref(c.builder, typ, val)
    return gptj__udjej


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    jrqrj__zrx = []
    crm__odjmw = []
    for zapw__vdo in range(typ.nlevels):
        ndobz__hiijb = c.pyapi.unserialize(c.pyapi.serialize_object(zapw__vdo))
        nkchx__egc = c.pyapi.call_method(val, 'get_level_values', (
            ndobz__hiijb,))
        yqcib__zvy = c.pyapi.object_getattr_string(nkchx__egc, 'values')
        c.pyapi.decref(nkchx__egc)
        c.pyapi.decref(ndobz__hiijb)
        dlvtx__znx = c.pyapi.to_native_value(typ.array_types[zapw__vdo],
            yqcib__zvy).value
        jrqrj__zrx.append(dlvtx__znx)
        crm__odjmw.append(yqcib__zvy)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, jrqrj__zrx)
    else:
        data = cgutils.pack_struct(c.builder, jrqrj__zrx)
    czlz__mcxf = c.pyapi.object_getattr_string(val, 'names')
    eqn__gdkei = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    ims__rpx = c.pyapi.call_function_objargs(eqn__gdkei, (czlz__mcxf,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), ims__rpx).value
    bbb__ixo = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, bbb__ixo).value
    nwopp__vcxqm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nwopp__vcxqm.data = data
    nwopp__vcxqm.names = names
    nwopp__vcxqm.name = name
    for yqcib__zvy in crm__odjmw:
        c.pyapi.decref(yqcib__zvy)
    c.pyapi.decref(czlz__mcxf)
    c.pyapi.decref(eqn__gdkei)
    c.pyapi.decref(ims__rpx)
    c.pyapi.decref(bbb__ixo)
    return NativeValue(nwopp__vcxqm._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    ioo__ergbu = 'pandas.MultiIndex.from_product'
    ixw__jfp = dict(sortorder=sortorder)
    hwq__yxz = dict(sortorder=None)
    check_unsupported_args(ioo__ergbu, ixw__jfp, hwq__yxz, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{ioo__ergbu}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{ioo__ergbu}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{ioo__ergbu}: iterables and names must be of the same length.')


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
    lwpeu__dxfyu = MultiIndexType(array_types, names_typ)
    ixvax__ehpb = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, ixvax__ehpb, lwpeu__dxfyu)
    rugc__ery = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{ixvax__ehpb}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    llv__nml = {}
    exec(rugc__ery, globals(), llv__nml)
    xvx__xazum = llv__nml['impl']
    return xvx__xazum


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        luzc__ygi, wzbto__xcwgs, akl__wpsnr = args
        ffwwg__bzs = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ffwwg__bzs.data = luzc__ygi
        ffwwg__bzs.names = wzbto__xcwgs
        ffwwg__bzs.name = akl__wpsnr
        context.nrt.incref(builder, signature.args[0], luzc__ygi)
        context.nrt.incref(builder, signature.args[1], wzbto__xcwgs)
        context.nrt.incref(builder, signature.args[2], akl__wpsnr)
        return ffwwg__bzs._getvalue()
    sru__xvf = MultiIndexType(data.types, names.types, name)
    return sru__xvf(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        hjm__rldya = len(I.array_types)
        rugc__ery = 'def impl(I, ind):\n'
        rugc__ery += '  data = I._data\n'
        rugc__ery += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{zapw__vdo}][ind])' for zapw__vdo in
            range(hjm__rldya))))
        llv__nml = {}
        exec(rugc__ery, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, llv__nml)
        xvx__xazum = llv__nml['impl']
        return xvx__xazum


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    wfh__pfu, duiqi__snza = sig.args
    if wfh__pfu != duiqi__snza:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
