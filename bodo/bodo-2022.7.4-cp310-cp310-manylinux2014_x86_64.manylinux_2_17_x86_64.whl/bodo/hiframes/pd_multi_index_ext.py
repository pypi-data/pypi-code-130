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
        ozg__hxkag = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, ozg__hxkag)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[kriw__azkvk].values) for
        kriw__azkvk in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (eqh__hkpb) for eqh__hkpb in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    jxso__kjlys = c.context.insert_const_string(c.builder.module, 'pandas')
    dojxc__gbrg = c.pyapi.import_module_noblock(jxso__kjlys)
    qjlva__utnfs = c.pyapi.object_getattr_string(dojxc__gbrg, 'MultiIndex')
    fcav__wkymm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        fcav__wkymm.data)
    vftg__fcst = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        fcav__wkymm.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), fcav__wkymm
        .names)
    qlm__smt = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        fcav__wkymm.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, fcav__wkymm.name)
    kfof__vdmz = c.pyapi.from_native_value(typ.name_typ, fcav__wkymm.name,
        c.env_manager)
    moc__kje = c.pyapi.borrow_none()
    uhttm__bhu = c.pyapi.call_method(qjlva__utnfs, 'from_arrays', (
        vftg__fcst, moc__kje, qlm__smt))
    c.pyapi.object_setattr_string(uhttm__bhu, 'name', kfof__vdmz)
    c.pyapi.decref(vftg__fcst)
    c.pyapi.decref(qlm__smt)
    c.pyapi.decref(kfof__vdmz)
    c.pyapi.decref(dojxc__gbrg)
    c.pyapi.decref(qjlva__utnfs)
    c.context.nrt.decref(c.builder, typ, val)
    return uhttm__bhu


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    qel__kzwsj = []
    dcwbt__uieee = []
    for kriw__azkvk in range(typ.nlevels):
        jvy__erjs = c.pyapi.unserialize(c.pyapi.serialize_object(kriw__azkvk))
        pvodp__nedmg = c.pyapi.call_method(val, 'get_level_values', (
            jvy__erjs,))
        vfnl__qay = c.pyapi.object_getattr_string(pvodp__nedmg, 'values')
        c.pyapi.decref(pvodp__nedmg)
        c.pyapi.decref(jvy__erjs)
        pfux__kdg = c.pyapi.to_native_value(typ.array_types[kriw__azkvk],
            vfnl__qay).value
        qel__kzwsj.append(pfux__kdg)
        dcwbt__uieee.append(vfnl__qay)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, qel__kzwsj)
    else:
        data = cgutils.pack_struct(c.builder, qel__kzwsj)
    qlm__smt = c.pyapi.object_getattr_string(val, 'names')
    jpxn__rzog = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    mjcmv__jhhz = c.pyapi.call_function_objargs(jpxn__rzog, (qlm__smt,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), mjcmv__jhhz
        ).value
    kfof__vdmz = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kfof__vdmz).value
    fcav__wkymm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fcav__wkymm.data = data
    fcav__wkymm.names = names
    fcav__wkymm.name = name
    for vfnl__qay in dcwbt__uieee:
        c.pyapi.decref(vfnl__qay)
    c.pyapi.decref(qlm__smt)
    c.pyapi.decref(jpxn__rzog)
    c.pyapi.decref(mjcmv__jhhz)
    c.pyapi.decref(kfof__vdmz)
    return NativeValue(fcav__wkymm._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    nxcp__bso = 'pandas.MultiIndex.from_product'
    bqat__dcozj = dict(sortorder=sortorder)
    spkbz__hwf = dict(sortorder=None)
    check_unsupported_args(nxcp__bso, bqat__dcozj, spkbz__hwf, package_name
        ='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{nxcp__bso}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{nxcp__bso}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{nxcp__bso}: iterables and names must be of the same length.')


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
    pqkn__tsop = MultiIndexType(array_types, names_typ)
    gqyf__qto = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, gqyf__qto, pqkn__tsop)
    nsc__hyrrh = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{gqyf__qto}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    xvckl__rdvu = {}
    exec(nsc__hyrrh, globals(), xvckl__rdvu)
    mmb__wxvas = xvckl__rdvu['impl']
    return mmb__wxvas


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        ltwl__duft, getv__ykm, zwoj__ajqa = args
        ojtwf__egk = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ojtwf__egk.data = ltwl__duft
        ojtwf__egk.names = getv__ykm
        ojtwf__egk.name = zwoj__ajqa
        context.nrt.incref(builder, signature.args[0], ltwl__duft)
        context.nrt.incref(builder, signature.args[1], getv__ykm)
        context.nrt.incref(builder, signature.args[2], zwoj__ajqa)
        return ojtwf__egk._getvalue()
    sjsxd__tdt = MultiIndexType(data.types, names.types, name)
    return sjsxd__tdt(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        zotjl__gtadn = len(I.array_types)
        nsc__hyrrh = 'def impl(I, ind):\n'
        nsc__hyrrh += '  data = I._data\n'
        nsc__hyrrh += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{kriw__azkvk}][ind])' for
            kriw__azkvk in range(zotjl__gtadn))))
        xvckl__rdvu = {}
        exec(nsc__hyrrh, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, xvckl__rdvu)
        mmb__wxvas = xvckl__rdvu['impl']
        return mmb__wxvas


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    nsqun__kgw, ylrkk__kevmm = sig.args
    if nsqun__kgw != ylrkk__kevmm:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
