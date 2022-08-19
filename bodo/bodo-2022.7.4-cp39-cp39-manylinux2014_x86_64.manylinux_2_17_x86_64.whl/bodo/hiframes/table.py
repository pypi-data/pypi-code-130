"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.ir_utils import guard
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_none, is_overload_true, raise_bodo_error, to_str_arr_if_dict_array, unwrap_typeref
from bodo.utils.utils import is_whole_slice


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            ctm__kne = 0
            zqno__vhca = []
            for i in range(usecols[-1] + 1):
                if i == usecols[ctm__kne]:
                    zqno__vhca.append(arrs[ctm__kne])
                    ctm__kne += 1
                else:
                    zqno__vhca.append(None)
            for mfnm__qew in range(usecols[-1] + 1, num_arrs):
                zqno__vhca.append(None)
            self.arrays = zqno__vhca
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((aau__qoos == uky__cnwlv).all() for aau__qoos,
            uky__cnwlv in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        vuv__mnbl = len(self.arrays)
        nwxs__byuv = dict(zip(range(vuv__mnbl), self.arrays))
        df = pd.DataFrame(nwxs__byuv, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        uhv__racc = []
        spgz__stwib = []
        ybaew__cmxkp = {}
        shv__jww = {}
        kaa__esjqw = defaultdict(int)
        pmvjm__uhwko = defaultdict(list)
        if not has_runtime_cols:
            for i, fnief__nlo in enumerate(arr_types):
                if fnief__nlo not in ybaew__cmxkp:
                    usw__ovh = len(ybaew__cmxkp)
                    ybaew__cmxkp[fnief__nlo] = usw__ovh
                    shv__jww[usw__ovh] = fnief__nlo
                exru__hjd = ybaew__cmxkp[fnief__nlo]
                uhv__racc.append(exru__hjd)
                spgz__stwib.append(kaa__esjqw[exru__hjd])
                kaa__esjqw[exru__hjd] += 1
                pmvjm__uhwko[exru__hjd].append(i)
        self.block_nums = uhv__racc
        self.block_offsets = spgz__stwib
        self.type_to_blk = ybaew__cmxkp
        self.blk_to_type = shv__jww
        self.block_to_arr_ind = pmvjm__uhwko
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(arr) for arr in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            tabcr__dld = [(f'block_{i}', types.List(fnief__nlo)) for i,
                fnief__nlo in enumerate(fe_type.arr_types)]
        else:
            tabcr__dld = [(f'block_{exru__hjd}', types.List(fnief__nlo)) for
                fnief__nlo, exru__hjd in fe_type.type_to_blk.items()]
        tabcr__dld.append(('parent', types.pyobject))
        tabcr__dld.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, tabcr__dld)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    hph__yynf = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    chirx__gzpr = c.pyapi.make_none()
    ivcw__ircrx = c.context.get_constant(types.int64, 0)
    rjr__mgvh = cgutils.alloca_once_value(c.builder, ivcw__ircrx)
    for fnief__nlo, exru__hjd in typ.type_to_blk.items():
        fylxy__ooxl = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[exru__hjd]))
        mfnm__qew, aumgq__ikrtm = ListInstance.allocate_ex(c.context, c.
            builder, types.List(fnief__nlo), fylxy__ooxl)
        aumgq__ikrtm.size = fylxy__ooxl
        bwt__hkv = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[exru__hjd],
            dtype=np.int64))
        nozkt__dzi = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, bwt__hkv)
        with cgutils.for_range(c.builder, fylxy__ooxl) as wadb__cxvvy:
            i = wadb__cxvvy.index
            ghxhx__vrbj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), nozkt__dzi, i)
            amazu__msz = c.pyapi.long_from_longlong(ghxhx__vrbj)
            emx__ynmob = c.pyapi.object_getitem(hph__yynf, amazu__msz)
            ytims__wip = c.builder.icmp_unsigned('==', emx__ynmob, chirx__gzpr)
            with c.builder.if_else(ytims__wip) as (eqd__rcg, kfci__nifuo):
                with eqd__rcg:
                    xyd__dqf = c.context.get_constant_null(fnief__nlo)
                    aumgq__ikrtm.inititem(i, xyd__dqf, incref=False)
                with kfci__nifuo:
                    rekg__ztgbt = c.pyapi.call_method(emx__ynmob, '__len__', ()
                        )
                    vcy__ukck = c.pyapi.long_as_longlong(rekg__ztgbt)
                    c.builder.store(vcy__ukck, rjr__mgvh)
                    c.pyapi.decref(rekg__ztgbt)
                    arr = c.pyapi.to_native_value(fnief__nlo, emx__ynmob).value
                    aumgq__ikrtm.inititem(i, arr, incref=False)
            c.pyapi.decref(emx__ynmob)
            c.pyapi.decref(amazu__msz)
        setattr(table, f'block_{exru__hjd}', aumgq__ikrtm.value)
    table.len = c.builder.load(rjr__mgvh)
    c.pyapi.decref(hph__yynf)
    c.pyapi.decref(chirx__gzpr)
    rsddu__ugycc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=rsddu__ugycc)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        rypd__akxo = c.context.get_constant(types.int64, 0)
        for i, fnief__nlo in enumerate(typ.arr_types):
            zqno__vhca = getattr(table, f'block_{i}')
            jjs__kfenq = ListInstance(c.context, c.builder, types.List(
                fnief__nlo), zqno__vhca)
            rypd__akxo = c.builder.add(rypd__akxo, jjs__kfenq.size)
        ukz__tigw = c.pyapi.list_new(rypd__akxo)
        lwsw__rgwq = c.context.get_constant(types.int64, 0)
        for i, fnief__nlo in enumerate(typ.arr_types):
            zqno__vhca = getattr(table, f'block_{i}')
            jjs__kfenq = ListInstance(c.context, c.builder, types.List(
                fnief__nlo), zqno__vhca)
            with cgutils.for_range(c.builder, jjs__kfenq.size) as wadb__cxvvy:
                i = wadb__cxvvy.index
                arr = jjs__kfenq.getitem(i)
                c.context.nrt.incref(c.builder, fnief__nlo, arr)
                idx = c.builder.add(lwsw__rgwq, i)
                c.pyapi.list_setitem(ukz__tigw, idx, c.pyapi.
                    from_native_value(fnief__nlo, arr, c.env_manager))
            lwsw__rgwq = c.builder.add(lwsw__rgwq, jjs__kfenq.size)
        goq__tgs = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        ppd__zxvns = c.pyapi.call_function_objargs(goq__tgs, (ukz__tigw,))
        c.pyapi.decref(goq__tgs)
        c.pyapi.decref(ukz__tigw)
        c.context.nrt.decref(c.builder, typ, val)
        return ppd__zxvns
    ukz__tigw = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    jyjv__ygwzh = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for fnief__nlo, exru__hjd in typ.type_to_blk.items():
        zqno__vhca = getattr(table, f'block_{exru__hjd}')
        jjs__kfenq = ListInstance(c.context, c.builder, types.List(
            fnief__nlo), zqno__vhca)
        bwt__hkv = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[exru__hjd],
            dtype=np.int64))
        nozkt__dzi = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, bwt__hkv)
        with cgutils.for_range(c.builder, jjs__kfenq.size) as wadb__cxvvy:
            i = wadb__cxvvy.index
            ghxhx__vrbj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), nozkt__dzi, i)
            arr = jjs__kfenq.getitem(i)
            hqv__oqrwp = cgutils.alloca_once_value(c.builder, arr)
            muxyg__tvctf = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(fnief__nlo))
            is_null = is_ll_eq(c.builder, hqv__oqrwp, muxyg__tvctf)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (eqd__rcg, kfci__nifuo):
                with eqd__rcg:
                    chirx__gzpr = c.pyapi.make_none()
                    c.pyapi.list_setitem(ukz__tigw, ghxhx__vrbj, chirx__gzpr)
                with kfci__nifuo:
                    emx__ynmob = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, jyjv__ygwzh)
                        ) as (lww__bbpy, tma__iwjbt):
                        with lww__bbpy:
                            rqgwa__pjkk = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                ghxhx__vrbj, fnief__nlo)
                            c.builder.store(rqgwa__pjkk, emx__ynmob)
                        with tma__iwjbt:
                            c.context.nrt.incref(c.builder, fnief__nlo, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                fnief__nlo, arr, c.env_manager), emx__ynmob)
                    c.pyapi.list_setitem(ukz__tigw, ghxhx__vrbj, c.builder.
                        load(emx__ynmob))
    goq__tgs = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    ppd__zxvns = c.pyapi.call_function_objargs(goq__tgs, (ukz__tigw,))
    c.pyapi.decref(goq__tgs)
    c.pyapi.decref(ukz__tigw)
    c.context.nrt.decref(c.builder, typ, val)
    return ppd__zxvns


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        uhkkt__sta = context.get_constant(types.int64, 0)
        for i, fnief__nlo in enumerate(table_type.arr_types):
            zqno__vhca = getattr(table, f'block_{i}')
            jjs__kfenq = ListInstance(context, builder, types.List(
                fnief__nlo), zqno__vhca)
            uhkkt__sta = builder.add(uhkkt__sta, jjs__kfenq.size)
        return uhkkt__sta
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    exru__hjd = table_type.block_nums[col_ind]
    tbx__wojr = table_type.block_offsets[col_ind]
    zqno__vhca = getattr(table, f'block_{exru__hjd}')
    snfce__vzjtr = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    idd__fofo = context.get_constant(types.int64, col_ind)
    cnls__hpkr = context.get_constant(types.int64, tbx__wojr)
    fxrh__zpfy = table_arg, zqno__vhca, cnls__hpkr, idd__fofo
    ensure_column_unboxed_codegen(context, builder, snfce__vzjtr, fxrh__zpfy)
    jjs__kfenq = ListInstance(context, builder, types.List(arr_type),
        zqno__vhca)
    arr = jjs__kfenq.getitem(tbx__wojr)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, mfnm__qew = args
        arr = get_table_data_codegen(context, builder, table_arg, col_ind,
            table_type)
        return impl_ret_borrowed(context, builder, arr_type, arr)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType
        ), 'Can only delete columns from a table'
    assert isinstance(ind_typ, types.TypeRef) and isinstance(ind_typ.
        instance_type, MetaType), 'ind_typ must be a typeref for a meta type'
    gzf__fjh = list(ind_typ.instance_type.meta)
    kyue__zho = defaultdict(list)
    for ind in gzf__fjh:
        kyue__zho[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, mfnm__qew = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for exru__hjd, tbidl__wrs in kyue__zho.items():
            arr_type = table_type.blk_to_type[exru__hjd]
            zqno__vhca = getattr(table, f'block_{exru__hjd}')
            jjs__kfenq = ListInstance(context, builder, types.List(arr_type
                ), zqno__vhca)
            xyd__dqf = context.get_constant_null(arr_type)
            if len(tbidl__wrs) == 1:
                tbx__wojr = tbidl__wrs[0]
                arr = jjs__kfenq.getitem(tbx__wojr)
                context.nrt.decref(builder, arr_type, arr)
                jjs__kfenq.inititem(tbx__wojr, xyd__dqf, incref=False)
            else:
                fylxy__ooxl = context.get_constant(types.int64, len(tbidl__wrs)
                    )
                asqml__uet = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(tbidl__wrs, dtype=
                    np.int64))
                pyf__foh = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, asqml__uet)
                with cgutils.for_range(builder, fylxy__ooxl) as wadb__cxvvy:
                    i = wadb__cxvvy.index
                    tbx__wojr = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        pyf__foh, i)
                    arr = jjs__kfenq.getitem(tbx__wojr)
                    context.nrt.decref(builder, arr_type, arr)
                    jjs__kfenq.inititem(tbx__wojr, xyd__dqf, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    ivcw__ircrx = context.get_constant(types.int64, 0)
    wmzb__udpo = context.get_constant(types.int64, 1)
    rdv__wgb = arr_type not in in_table_type.type_to_blk
    for fnief__nlo, exru__hjd in out_table_type.type_to_blk.items():
        if fnief__nlo in in_table_type.type_to_blk:
            fooig__yjx = in_table_type.type_to_blk[fnief__nlo]
            aumgq__ikrtm = ListInstance(context, builder, types.List(
                fnief__nlo), getattr(in_table, f'block_{fooig__yjx}'))
            context.nrt.incref(builder, types.List(fnief__nlo),
                aumgq__ikrtm.value)
            setattr(out_table, f'block_{exru__hjd}', aumgq__ikrtm.value)
    if rdv__wgb:
        mfnm__qew, aumgq__ikrtm = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), wmzb__udpo)
        aumgq__ikrtm.size = wmzb__udpo
        aumgq__ikrtm.inititem(ivcw__ircrx, arr_arg, incref=True)
        exru__hjd = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{exru__hjd}', aumgq__ikrtm.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        exru__hjd = out_table_type.type_to_blk[arr_type]
        aumgq__ikrtm = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{exru__hjd}'))
        if is_new_col:
            n = aumgq__ikrtm.size
            fnplc__hlurv = builder.add(n, wmzb__udpo)
            aumgq__ikrtm.resize(fnplc__hlurv)
            aumgq__ikrtm.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            jhpk__hwxw = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            aumgq__ikrtm.setitem(jhpk__hwxw, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            jhpk__hwxw = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = aumgq__ikrtm.size
            fnplc__hlurv = builder.add(n, wmzb__udpo)
            aumgq__ikrtm.resize(fnplc__hlurv)
            context.nrt.incref(builder, arr_type, aumgq__ikrtm.getitem(
                jhpk__hwxw))
            aumgq__ikrtm.move(builder.add(jhpk__hwxw, wmzb__udpo),
                jhpk__hwxw, builder.sub(n, jhpk__hwxw))
            aumgq__ikrtm.setitem(jhpk__hwxw, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    aih__rhv = in_table_type.arr_types[col_ind]
    if aih__rhv in out_table_type.type_to_blk:
        exru__hjd = out_table_type.type_to_blk[aih__rhv]
        dztyb__ldp = getattr(out_table, f'block_{exru__hjd}')
        rfxey__yiw = types.List(aih__rhv)
        jhpk__hwxw = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        oig__eov = rfxey__yiw.dtype(rfxey__yiw, types.intp)
        iic__wdpf = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), oig__eov, (dztyb__ldp, jhpk__hwxw))
        context.nrt.decref(builder, aih__rhv, iic__wdpf)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    bwt__qaknx = list(table.arr_types)
    if ind == len(bwt__qaknx):
        lgpyw__bvik = None
        bwt__qaknx.append(arr_type)
    else:
        lgpyw__bvik = table.arr_types[ind]
        bwt__qaknx[ind] = arr_type
    nsd__rwyd = TableType(tuple(bwt__qaknx))
    fptr__udau = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': nsd__rwyd}
    wvw__owd = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    wvw__owd += f'  T2 = init_table(out_table_typ, False)\n'
    wvw__owd += f'  T2 = set_table_len(T2, len(table))\n'
    wvw__owd += f'  T2 = set_table_parent(T2, table)\n'
    for typ, exru__hjd in nsd__rwyd.type_to_blk.items():
        if typ in table.type_to_blk:
            akuww__nzd = table.type_to_blk[typ]
            wvw__owd += (
                f'  arr_list_{exru__hjd} = get_table_block(table, {akuww__nzd})\n'
                )
            wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_{exru__hjd}, {len(nsd__rwyd.block_to_arr_ind[exru__hjd])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[akuww__nzd]
                ) & used_cols:
                wvw__owd += f'  for i in range(len(arr_list_{exru__hjd})):\n'
                if typ not in (lgpyw__bvik, arr_type):
                    wvw__owd += (
                        f'    out_arr_list_{exru__hjd}[i] = arr_list_{exru__hjd}[i]\n'
                        )
                else:
                    cvo__xco = table.block_to_arr_ind[akuww__nzd]
                    gkpxc__deat = np.empty(len(cvo__xco), np.int64)
                    gnz__mytfx = False
                    for eyg__szy, ghxhx__vrbj in enumerate(cvo__xco):
                        if ghxhx__vrbj != ind:
                            gquwu__vcma = nsd__rwyd.block_offsets[ghxhx__vrbj]
                        else:
                            gquwu__vcma = -1
                            gnz__mytfx = True
                        gkpxc__deat[eyg__szy] = gquwu__vcma
                    fptr__udau[f'out_idxs_{exru__hjd}'] = np.array(gkpxc__deat,
                        np.int64)
                    wvw__owd += f'    out_idx = out_idxs_{exru__hjd}[i]\n'
                    if gnz__mytfx:
                        wvw__owd += f'    if out_idx == -1:\n'
                        wvw__owd += f'      continue\n'
                    wvw__owd += (
                        f'    out_arr_list_{exru__hjd}[out_idx] = arr_list_{exru__hjd}[i]\n'
                        )
            if typ == arr_type and not is_null:
                wvw__owd += (
                    f'  out_arr_list_{exru__hjd}[{nsd__rwyd.block_offsets[ind]}] = arr\n'
                    )
        else:
            fptr__udau[f'arr_list_typ_{exru__hjd}'] = types.List(arr_type)
            wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_typ_{exru__hjd}, 1, False)
"""
            if not is_null:
                wvw__owd += f'  out_arr_list_{exru__hjd}[0] = arr\n'
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  return T2\n'
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        tah__kdot = None
    else:
        tah__kdot = set(used_cols.instance_type.meta)
    ogm__nupev = get_overload_const_int(ind)
    return generate_set_table_data_code(table, ogm__nupev, arr, tah__kdot)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    ogm__nupev = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        tah__kdot = None
    else:
        tah__kdot = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, ogm__nupev, arr_type,
        tah__kdot, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    sxgo__tya = args[0]
    if equiv_set.has_shape(sxgo__tya):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            sxgo__tya)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    mny__naw = []
    for fnief__nlo, exru__hjd in table_type.type_to_blk.items():
        olqh__fqhsn = len(table_type.block_to_arr_ind[exru__hjd])
        doglk__nsd = []
        for i in range(olqh__fqhsn):
            ghxhx__vrbj = table_type.block_to_arr_ind[exru__hjd][i]
            doglk__nsd.append(pyval.arrays[ghxhx__vrbj])
        mny__naw.append(context.get_constant_generic(builder, types.List(
            fnief__nlo), doglk__nsd))
    gtnsk__skfmf = context.get_constant_null(types.pyobject)
    brxl__ggdh = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(mny__naw + [gtnsk__skfmf, brxl__ggdh])


@intrinsic
def init_table(typingctx, table_type, to_str_if_dict_t):
    out_table_type = table_type.instance_type if isinstance(table_type,
        types.TypeRef) else table_type
    assert isinstance(out_table_type, TableType
        ), 'table type or typeref expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        out_table_type = to_str_arr_if_dict_array(out_table_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(out_table_type)(context, builder)
        for fnief__nlo, exru__hjd in out_table_type.type_to_blk.items():
            cunit__zprj = context.get_constant_null(types.List(fnief__nlo))
            setattr(table, f'block_{exru__hjd}', cunit__zprj)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    ndy__qjwjq = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        ndy__qjwjq[typ.dtype] = i
    lihi__ylts = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(lihi__ylts, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        exwlx__pzty, mfnm__qew = args
        table = cgutils.create_struct_proxy(lihi__ylts)(context, builder)
        for fnief__nlo, exru__hjd in lihi__ylts.type_to_blk.items():
            idx = ndy__qjwjq[fnief__nlo]
            lza__lnm = signature(types.List(fnief__nlo),
                tuple_of_lists_type, types.literal(idx))
            ulqhf__umj = exwlx__pzty, idx
            egeme__wlxt = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, lza__lnm, ulqhf__umj)
            setattr(table, f'block_{exru__hjd}', egeme__wlxt)
        return table._getvalue()
    sig = lihi__ylts(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    exru__hjd = get_overload_const_int(blk_type)
    arr_type = None
    for fnief__nlo, uky__cnwlv in table_type.type_to_blk.items():
        if uky__cnwlv == exru__hjd:
            arr_type = fnief__nlo
            break
    assert arr_type is not None, 'invalid table type block'
    qvokm__qtojp = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        zqno__vhca = getattr(table, f'block_{exru__hjd}')
        return impl_ret_borrowed(context, builder, qvokm__qtojp, zqno__vhca)
    sig = qvokm__qtojp(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, otmeg__xcr = args
        zyte__phl = context.get_python_api(builder)
        iut__xtkyn = used_cols_typ == types.none
        if not iut__xtkyn:
            frv__gds = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), otmeg__xcr)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for fnief__nlo, exru__hjd in table_type.type_to_blk.items():
            fylxy__ooxl = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[exru__hjd]))
            bwt__hkv = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                exru__hjd], dtype=np.int64))
            nozkt__dzi = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, bwt__hkv)
            zqno__vhca = getattr(table, f'block_{exru__hjd}')
            with cgutils.for_range(builder, fylxy__ooxl) as wadb__cxvvy:
                i = wadb__cxvvy.index
                ghxhx__vrbj = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    nozkt__dzi, i)
                snfce__vzjtr = types.none(table_type, types.List(fnief__nlo
                    ), types.int64, types.int64)
                fxrh__zpfy = table_arg, zqno__vhca, i, ghxhx__vrbj
                if iut__xtkyn:
                    ensure_column_unboxed_codegen(context, builder,
                        snfce__vzjtr, fxrh__zpfy)
                else:
                    veia__mips = frv__gds.contains(ghxhx__vrbj)
                    with builder.if_then(veia__mips):
                        ensure_column_unboxed_codegen(context, builder,
                            snfce__vzjtr, fxrh__zpfy)
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, used_cols_typ)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t, arr_ind_t):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, owyb__zapt, hnt__qxtm, qbv__ddhz = args
    zyte__phl = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    jyjv__ygwzh = cgutils.is_not_null(builder, table.parent)
    jjs__kfenq = ListInstance(context, builder, sig.args[1], owyb__zapt)
    hlnwp__wcmmj = jjs__kfenq.getitem(hnt__qxtm)
    hqv__oqrwp = cgutils.alloca_once_value(builder, hlnwp__wcmmj)
    muxyg__tvctf = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, hqv__oqrwp, muxyg__tvctf)
    with builder.if_then(is_null):
        with builder.if_else(jyjv__ygwzh) as (eqd__rcg, kfci__nifuo):
            with eqd__rcg:
                emx__ynmob = get_df_obj_column_codegen(context, builder,
                    zyte__phl, table.parent, qbv__ddhz, sig.args[1].dtype)
                arr = zyte__phl.to_native_value(sig.args[1].dtype, emx__ynmob
                    ).value
                jjs__kfenq.inititem(hnt__qxtm, arr, incref=False)
                zyte__phl.decref(emx__ynmob)
            with kfci__nifuo:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    exru__hjd = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, tfb__vhl, mfnm__qew = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{exru__hjd}', tfb__vhl)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, ves__efufr = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = ves__efufr
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        qwobv__mgso, zumdw__dptf = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, zumdw__dptf)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, qwobv__mgso)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    qvokm__qtojp = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(qvokm__qtojp, types.List
        ), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        qvokm__qtojp = types.List(to_str_arr_if_dict_array(qvokm__qtojp.dtype))

    def codegen(context, builder, sig, args):
        jhven__gjq = args[1]
        mfnm__qew, aumgq__ikrtm = ListInstance.allocate_ex(context, builder,
            qvokm__qtojp, jhven__gjq)
        aumgq__ikrtm.size = jhven__gjq
        return aumgq__ikrtm.value
    sig = qvokm__qtojp(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    aishj__rtnus = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(aishj__rtnus)

    def codegen(context, builder, sig, args):
        jhven__gjq, mfnm__qew = args
        mfnm__qew, aumgq__ikrtm = ListInstance.allocate_ex(context, builder,
            list_type, jhven__gjq)
        aumgq__ikrtm.size = jhven__gjq
        return aumgq__ikrtm.value
    sig = list_type(size_typ, data_typ)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        gembz__vwzj = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(gembz__vwzj)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    fptr__udau = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        trkvg__ajl = used_cols.instance_type
        gtv__jxh = np.array(trkvg__ajl.meta, dtype=np.int64)
        fptr__udau['used_cols_vals'] = gtv__jxh
        ixut__ixb = set([T.block_nums[i] for i in gtv__jxh])
    else:
        gtv__jxh = None
    wvw__owd = 'def table_filter_func(T, idx, used_cols=None):\n'
    wvw__owd += f'  T2 = init_table(T, False)\n'
    wvw__owd += f'  l = 0\n'
    if gtv__jxh is not None and len(gtv__jxh) == 0:
        wvw__owd += f'  l = _get_idx_length(idx, len(T))\n'
        wvw__owd += f'  T2 = set_table_len(T2, l)\n'
        wvw__owd += f'  return T2\n'
        mvxqb__zqsnt = {}
        exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
        return mvxqb__zqsnt['table_filter_func']
    if gtv__jxh is not None:
        wvw__owd += f'  used_set = set(used_cols_vals)\n'
    for exru__hjd in T.type_to_blk.values():
        wvw__owd += (
            f'  arr_list_{exru__hjd} = get_table_block(T, {exru__hjd})\n')
        wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_{exru__hjd}, len(arr_list_{exru__hjd}), False)
"""
        if gtv__jxh is None or exru__hjd in ixut__ixb:
            fptr__udau[f'arr_inds_{exru__hjd}'] = np.array(T.
                block_to_arr_ind[exru__hjd], dtype=np.int64)
            wvw__owd += f'  for i in range(len(arr_list_{exru__hjd})):\n'
            wvw__owd += f'    arr_ind_{exru__hjd} = arr_inds_{exru__hjd}[i]\n'
            if gtv__jxh is not None:
                wvw__owd += (
                    f'    if arr_ind_{exru__hjd} not in used_set: continue\n')
            wvw__owd += f"""    ensure_column_unboxed(T, arr_list_{exru__hjd}, i, arr_ind_{exru__hjd})
"""
            wvw__owd += f"""    out_arr_{exru__hjd} = ensure_contig_if_np(arr_list_{exru__hjd}[i][idx])
"""
            wvw__owd += f'    l = len(out_arr_{exru__hjd})\n'
            wvw__owd += (
                f'    out_arr_list_{exru__hjd}[i] = out_arr_{exru__hjd}\n')
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  T2 = set_table_len(T2, l)\n'
    wvw__owd += f'  return T2\n'
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    wptk__unt = list(idx.instance_type.meta)
    bwt__qaknx = tuple(np.array(T.arr_types, dtype=object)[wptk__unt])
    nsd__rwyd = TableType(bwt__qaknx)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    mzb__dcox = is_overload_true(copy_arrs)
    fptr__udau = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': nsd__rwyd}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        xgfq__lumn = set(kept_cols)
        fptr__udau['kept_cols'] = np.array(kept_cols, np.int64)
        txtps__yohxj = True
    else:
        txtps__yohxj = False
    pybe__veftr = {i: c for i, c in enumerate(wptk__unt)}
    wvw__owd = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    wvw__owd += f'  T2 = init_table(out_table_typ, False)\n'
    wvw__owd += f'  T2 = set_table_len(T2, len(T))\n'
    if txtps__yohxj and len(xgfq__lumn) == 0:
        wvw__owd += f'  return T2\n'
        mvxqb__zqsnt = {}
        exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
        return mvxqb__zqsnt['table_subset']
    if txtps__yohxj:
        wvw__owd += f'  kept_cols_set = set(kept_cols)\n'
    for typ, exru__hjd in nsd__rwyd.type_to_blk.items():
        akuww__nzd = T.type_to_blk[typ]
        wvw__owd += (
            f'  arr_list_{exru__hjd} = get_table_block(T, {akuww__nzd})\n')
        wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_{exru__hjd}, {len(nsd__rwyd.block_to_arr_ind[exru__hjd])}, False)
"""
        eifat__qfpg = True
        if txtps__yohxj:
            ucbsa__sgng = set(nsd__rwyd.block_to_arr_ind[exru__hjd])
            hvcp__tdl = ucbsa__sgng & xgfq__lumn
            eifat__qfpg = len(hvcp__tdl) > 0
        if eifat__qfpg:
            fptr__udau[f'out_arr_inds_{exru__hjd}'] = np.array(nsd__rwyd.
                block_to_arr_ind[exru__hjd], dtype=np.int64)
            wvw__owd += f'  for i in range(len(out_arr_list_{exru__hjd})):\n'
            wvw__owd += (
                f'    out_arr_ind_{exru__hjd} = out_arr_inds_{exru__hjd}[i]\n')
            if txtps__yohxj:
                wvw__owd += (
                    f'    if out_arr_ind_{exru__hjd} not in kept_cols_set: continue\n'
                    )
            tfja__ziocn = []
            fvo__mymc = []
            for hujp__fehps in nsd__rwyd.block_to_arr_ind[exru__hjd]:
                hwicz__oal = pybe__veftr[hujp__fehps]
                tfja__ziocn.append(hwicz__oal)
                uyzxe__exb = T.block_offsets[hwicz__oal]
                fvo__mymc.append(uyzxe__exb)
            fptr__udau[f'in_logical_idx_{exru__hjd}'] = np.array(tfja__ziocn,
                dtype=np.int64)
            fptr__udau[f'in_physical_idx_{exru__hjd}'] = np.array(fvo__mymc,
                dtype=np.int64)
            wvw__owd += (
                f'    logical_idx_{exru__hjd} = in_logical_idx_{exru__hjd}[i]\n'
                )
            wvw__owd += (
                f'    physical_idx_{exru__hjd} = in_physical_idx_{exru__hjd}[i]\n'
                )
            wvw__owd += f"""    ensure_column_unboxed(T, arr_list_{exru__hjd}, physical_idx_{exru__hjd}, logical_idx_{exru__hjd})
"""
            drob__jrxsr = '.copy()' if mzb__dcox else ''
            wvw__owd += f"""    out_arr_list_{exru__hjd}[i] = arr_list_{exru__hjd}[physical_idx_{exru__hjd}]{drob__jrxsr}
"""
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  return T2\n'
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    sxgo__tya = args[0]
    if equiv_set.has_shape(sxgo__tya):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=sxgo__tya, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (sxgo__tya)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    sxgo__tya = args[0]
    if equiv_set.has_shape(sxgo__tya):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            sxgo__tya)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    wvw__owd = 'def impl(T):\n'
    wvw__owd += f'  T2 = init_table(T, True)\n'
    wvw__owd += f'  l = len(T)\n'
    fptr__udau = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for exru__hjd in T.type_to_blk.values():
        fptr__udau[f'arr_inds_{exru__hjd}'] = np.array(T.block_to_arr_ind[
            exru__hjd], dtype=np.int64)
        wvw__owd += (
            f'  arr_list_{exru__hjd} = get_table_block(T, {exru__hjd})\n')
        wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_{exru__hjd}, len(arr_list_{exru__hjd}), True)
"""
        wvw__owd += f'  for i in range(len(arr_list_{exru__hjd})):\n'
        wvw__owd += f'    arr_ind_{exru__hjd} = arr_inds_{exru__hjd}[i]\n'
        wvw__owd += (
            f'    ensure_column_unboxed(T, arr_list_{exru__hjd}, i, arr_ind_{exru__hjd})\n'
            )
        wvw__owd += (
            f'    out_arr_{exru__hjd} = decode_if_dict_array(arr_list_{exru__hjd}[i])\n'
            )
        wvw__owd += f'    out_arr_list_{exru__hjd}[i] = out_arr_{exru__hjd}\n'
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  T2 = set_table_len(T2, l)\n'
    wvw__owd += f'  return T2\n'
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['impl']


@overload(operator.getitem, no_unliteral=True, inline='always')
def overload_table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return lambda T, idx: table_filter(T, idx)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        ebiug__err = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        ebiug__err = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            ebiug__err.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        iaoo__tdfyo, fsf__wjjz = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = fsf__wjjz
        mny__naw = cgutils.unpack_tuple(builder, iaoo__tdfyo)
        for i, zqno__vhca in enumerate(mny__naw):
            setattr(table, f'block_{i}', zqno__vhca)
            context.nrt.incref(builder, types.List(ebiug__err[i]), zqno__vhca)
        return table._getvalue()
    table_type = TableType(tuple(ebiug__err), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    fptr__udau = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        fptr__udau['kept_cols'] = np.array(list(kept_cols), np.int64)
        txtps__yohxj = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        txtps__yohxj = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    egaza__wev = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        egaza__wev else extra_arrs_t.types[i - egaza__wev] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    wvw__owd = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    wvw__owd += f'  T1 = in_table_t\n'
    wvw__owd += f'  T2 = init_table(out_table_type, False)\n'
    wvw__owd += f'  T2 = set_table_len(T2, len(T1))\n'
    if txtps__yohxj and len(kept_cols) == 0:
        wvw__owd += f'  return T2\n'
        mvxqb__zqsnt = {}
        exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
        return mvxqb__zqsnt['impl']
    if txtps__yohxj:
        wvw__owd += f'  kept_cols_set = set(kept_cols)\n'
    for typ, exru__hjd in out_table_type.type_to_blk.items():
        fptr__udau[f'arr_list_typ_{exru__hjd}'] = types.List(typ)
        fylxy__ooxl = len(out_table_type.block_to_arr_ind[exru__hjd])
        wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_typ_{exru__hjd}, {fylxy__ooxl}, False)
"""
        if typ in in_table_t.type_to_blk:
            dlfi__ebui = in_table_t.type_to_blk[typ]
            ofxk__pzm = []
            oia__bws = []
            for cwv__ktfwk in out_table_type.block_to_arr_ind[exru__hjd]:
                kvt__pvux = in_col_inds[cwv__ktfwk]
                if kvt__pvux < egaza__wev:
                    ofxk__pzm.append(in_table_t.block_offsets[kvt__pvux])
                    oia__bws.append(kvt__pvux)
                else:
                    ofxk__pzm.append(-1)
                    oia__bws.append(-1)
            fptr__udau[f'in_idxs_{exru__hjd}'] = np.array(ofxk__pzm, np.int64)
            fptr__udau[f'in_arr_inds_{exru__hjd}'] = np.array(oia__bws, np.
                int64)
            if txtps__yohxj:
                fptr__udau[f'out_arr_inds_{exru__hjd}'] = np.array(
                    out_table_type.block_to_arr_ind[exru__hjd], dtype=np.int64)
            wvw__owd += (
                f'  in_arr_list_{exru__hjd} = get_table_block(T1, {dlfi__ebui})\n'
                )
            wvw__owd += f'  for i in range(len(out_arr_list_{exru__hjd})):\n'
            wvw__owd += f'    in_offset_{exru__hjd} = in_idxs_{exru__hjd}[i]\n'
            wvw__owd += f'    if in_offset_{exru__hjd} == -1:\n'
            wvw__owd += f'      continue\n'
            wvw__owd += (
                f'    in_arr_ind_{exru__hjd} = in_arr_inds_{exru__hjd}[i]\n')
            if txtps__yohxj:
                wvw__owd += (
                    f'    if out_arr_inds_{exru__hjd}[i] not in kept_cols_set: continue\n'
                    )
            wvw__owd += f"""    ensure_column_unboxed(T1, in_arr_list_{exru__hjd}, in_offset_{exru__hjd}, in_arr_ind_{exru__hjd})
"""
            wvw__owd += f"""    out_arr_list_{exru__hjd}[i] = in_arr_list_{exru__hjd}[in_offset_{exru__hjd}]
"""
        for i, cwv__ktfwk in enumerate(out_table_type.block_to_arr_ind[
            exru__hjd]):
            if cwv__ktfwk not in kept_cols:
                continue
            kvt__pvux = in_col_inds[cwv__ktfwk]
            if kvt__pvux >= egaza__wev:
                wvw__owd += f"""  out_arr_list_{exru__hjd}[{i}] = extra_arrs_t[{kvt__pvux - egaza__wev}]
"""
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  return T2\n'
    fptr__udau.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    egaza__wev = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < egaza__wev else
        extra_arrs_t.types[i - egaza__wev] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    zki__nef = None
    if not is_overload_none(in_table_t):
        for i, fnief__nlo in enumerate(in_table_t.types):
            if fnief__nlo != types.none:
                zki__nef = f'in_table_t[{i}]'
                break
    if zki__nef is None:
        for i, fnief__nlo in enumerate(extra_arrs_t.types):
            if fnief__nlo != types.none:
                zki__nef = f'extra_arrs_t[{i}]'
                break
    assert zki__nef is not None, 'no array found in input data'
    wvw__owd = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    wvw__owd += f'  T1 = in_table_t\n'
    wvw__owd += f'  T2 = init_table(out_table_type, False)\n'
    wvw__owd += f'  T2 = set_table_len(T2, len({zki__nef}))\n'
    fptr__udau = {}
    for typ, exru__hjd in out_table_type.type_to_blk.items():
        fptr__udau[f'arr_list_typ_{exru__hjd}'] = types.List(typ)
        fylxy__ooxl = len(out_table_type.block_to_arr_ind[exru__hjd])
        wvw__owd += f"""  out_arr_list_{exru__hjd} = alloc_list_like(arr_list_typ_{exru__hjd}, {fylxy__ooxl}, False)
"""
        for i, cwv__ktfwk in enumerate(out_table_type.block_to_arr_ind[
            exru__hjd]):
            if cwv__ktfwk not in kept_cols:
                continue
            kvt__pvux = in_col_inds[cwv__ktfwk]
            if kvt__pvux < egaza__wev:
                wvw__owd += (
                    f'  out_arr_list_{exru__hjd}[{i}] = T1[{kvt__pvux}]\n')
            else:
                wvw__owd += f"""  out_arr_list_{exru__hjd}[{i}] = extra_arrs_t[{kvt__pvux - egaza__wev}]
"""
        wvw__owd += (
            f'  T2 = set_table_block(T2, out_arr_list_{exru__hjd}, {exru__hjd})\n'
            )
    wvw__owd += f'  return T2\n'
    fptr__udau.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    mvxqb__zqsnt = {}
    exec(wvw__owd, fptr__udau, mvxqb__zqsnt)
    return mvxqb__zqsnt['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    crgz__yei = args[0]
    ekb__iuo = args[1]
    if equiv_set.has_shape(crgz__yei):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            crgz__yei)[0], None), pre=[])
    if equiv_set.has_shape(ekb__iuo):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            ekb__iuo)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
