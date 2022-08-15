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
            dwkua__chsv = 0
            pxls__vyc = []
            for i in range(usecols[-1] + 1):
                if i == usecols[dwkua__chsv]:
                    pxls__vyc.append(arrs[dwkua__chsv])
                    dwkua__chsv += 1
                else:
                    pxls__vyc.append(None)
            for vvqq__fcw in range(usecols[-1] + 1, num_arrs):
                pxls__vyc.append(None)
            self.arrays = pxls__vyc
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((bwj__hevsp == bnpmd__fpwr).all() for 
            bwj__hevsp, bnpmd__fpwr in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        ewu__bmgmu = len(self.arrays)
        btyik__yqhtv = dict(zip(range(ewu__bmgmu), self.arrays))
        df = pd.DataFrame(btyik__yqhtv, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        auxsu__bmuhv = []
        bpzas__fypmm = []
        ctdgn__una = {}
        wnn__fvim = {}
        ytjy__cgkbh = defaultdict(int)
        khisc__ioaq = defaultdict(list)
        if not has_runtime_cols:
            for i, yttb__wzm in enumerate(arr_types):
                if yttb__wzm not in ctdgn__una:
                    lqkfc__vta = len(ctdgn__una)
                    ctdgn__una[yttb__wzm] = lqkfc__vta
                    wnn__fvim[lqkfc__vta] = yttb__wzm
                wdd__mzgfg = ctdgn__una[yttb__wzm]
                auxsu__bmuhv.append(wdd__mzgfg)
                bpzas__fypmm.append(ytjy__cgkbh[wdd__mzgfg])
                ytjy__cgkbh[wdd__mzgfg] += 1
                khisc__ioaq[wdd__mzgfg].append(i)
        self.block_nums = auxsu__bmuhv
        self.block_offsets = bpzas__fypmm
        self.type_to_blk = ctdgn__una
        self.blk_to_type = wnn__fvim
        self.block_to_arr_ind = khisc__ioaq
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
            zia__uxqh = [(f'block_{i}', types.List(yttb__wzm)) for i,
                yttb__wzm in enumerate(fe_type.arr_types)]
        else:
            zia__uxqh = [(f'block_{wdd__mzgfg}', types.List(yttb__wzm)) for
                yttb__wzm, wdd__mzgfg in fe_type.type_to_blk.items()]
        zia__uxqh.append(('parent', types.pyobject))
        zia__uxqh.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, zia__uxqh)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    azx__ltq = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    pacpt__liduy = c.pyapi.make_none()
    iazpi__hsreo = c.context.get_constant(types.int64, 0)
    kbmnb__wcono = cgutils.alloca_once_value(c.builder, iazpi__hsreo)
    for yttb__wzm, wdd__mzgfg in typ.type_to_blk.items():
        tbg__jaktk = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[wdd__mzgfg]))
        vvqq__fcw, swwe__nns = ListInstance.allocate_ex(c.context, c.
            builder, types.List(yttb__wzm), tbg__jaktk)
        swwe__nns.size = tbg__jaktk
        vwl__xbahe = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[wdd__mzgfg],
            dtype=np.int64))
        uun__kcjlj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vwl__xbahe)
        with cgutils.for_range(c.builder, tbg__jaktk) as ndkuw__amzq:
            i = ndkuw__amzq.index
            vwgzp__gbdwi = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), uun__kcjlj, i)
            mgv__fie = c.pyapi.long_from_longlong(vwgzp__gbdwi)
            dfx__mtl = c.pyapi.object_getitem(azx__ltq, mgv__fie)
            yuyaw__mqa = c.builder.icmp_unsigned('==', dfx__mtl, pacpt__liduy)
            with c.builder.if_else(yuyaw__mqa) as (dtmd__mfs, badrt__onn):
                with dtmd__mfs:
                    mepmu__dcx = c.context.get_constant_null(yttb__wzm)
                    swwe__nns.inititem(i, mepmu__dcx, incref=False)
                with badrt__onn:
                    ycd__zanvu = c.pyapi.call_method(dfx__mtl, '__len__', ())
                    jca__zcsm = c.pyapi.long_as_longlong(ycd__zanvu)
                    c.builder.store(jca__zcsm, kbmnb__wcono)
                    c.pyapi.decref(ycd__zanvu)
                    arr = c.pyapi.to_native_value(yttb__wzm, dfx__mtl).value
                    swwe__nns.inititem(i, arr, incref=False)
            c.pyapi.decref(dfx__mtl)
            c.pyapi.decref(mgv__fie)
        setattr(table, f'block_{wdd__mzgfg}', swwe__nns.value)
    table.len = c.builder.load(kbmnb__wcono)
    c.pyapi.decref(azx__ltq)
    c.pyapi.decref(pacpt__liduy)
    gbef__june = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=gbef__june)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        sdrto__tsgt = c.context.get_constant(types.int64, 0)
        for i, yttb__wzm in enumerate(typ.arr_types):
            pxls__vyc = getattr(table, f'block_{i}')
            oaij__zaqsy = ListInstance(c.context, c.builder, types.List(
                yttb__wzm), pxls__vyc)
            sdrto__tsgt = c.builder.add(sdrto__tsgt, oaij__zaqsy.size)
        fpl__ilrq = c.pyapi.list_new(sdrto__tsgt)
        ibgqg__dyd = c.context.get_constant(types.int64, 0)
        for i, yttb__wzm in enumerate(typ.arr_types):
            pxls__vyc = getattr(table, f'block_{i}')
            oaij__zaqsy = ListInstance(c.context, c.builder, types.List(
                yttb__wzm), pxls__vyc)
            with cgutils.for_range(c.builder, oaij__zaqsy.size) as ndkuw__amzq:
                i = ndkuw__amzq.index
                arr = oaij__zaqsy.getitem(i)
                c.context.nrt.incref(c.builder, yttb__wzm, arr)
                idx = c.builder.add(ibgqg__dyd, i)
                c.pyapi.list_setitem(fpl__ilrq, idx, c.pyapi.
                    from_native_value(yttb__wzm, arr, c.env_manager))
            ibgqg__dyd = c.builder.add(ibgqg__dyd, oaij__zaqsy.size)
        iyx__nwml = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        pykl__cvzd = c.pyapi.call_function_objargs(iyx__nwml, (fpl__ilrq,))
        c.pyapi.decref(iyx__nwml)
        c.pyapi.decref(fpl__ilrq)
        c.context.nrt.decref(c.builder, typ, val)
        return pykl__cvzd
    fpl__ilrq = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    vduhx__nfz = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for yttb__wzm, wdd__mzgfg in typ.type_to_blk.items():
        pxls__vyc = getattr(table, f'block_{wdd__mzgfg}')
        oaij__zaqsy = ListInstance(c.context, c.builder, types.List(
            yttb__wzm), pxls__vyc)
        vwl__xbahe = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[wdd__mzgfg],
            dtype=np.int64))
        uun__kcjlj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vwl__xbahe)
        with cgutils.for_range(c.builder, oaij__zaqsy.size) as ndkuw__amzq:
            i = ndkuw__amzq.index
            vwgzp__gbdwi = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), uun__kcjlj, i)
            arr = oaij__zaqsy.getitem(i)
            flrro__uss = cgutils.alloca_once_value(c.builder, arr)
            rep__jrebo = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(yttb__wzm))
            is_null = is_ll_eq(c.builder, flrro__uss, rep__jrebo)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (dtmd__mfs, badrt__onn):
                with dtmd__mfs:
                    pacpt__liduy = c.pyapi.make_none()
                    c.pyapi.list_setitem(fpl__ilrq, vwgzp__gbdwi, pacpt__liduy)
                with badrt__onn:
                    dfx__mtl = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, vduhx__nfz)
                        ) as (lsqj__gnr, hzyh__wexg):
                        with lsqj__gnr:
                            aaw__xafch = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                vwgzp__gbdwi, yttb__wzm)
                            c.builder.store(aaw__xafch, dfx__mtl)
                        with hzyh__wexg:
                            c.context.nrt.incref(c.builder, yttb__wzm, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                yttb__wzm, arr, c.env_manager), dfx__mtl)
                    c.pyapi.list_setitem(fpl__ilrq, vwgzp__gbdwi, c.builder
                        .load(dfx__mtl))
    iyx__nwml = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    pykl__cvzd = c.pyapi.call_function_objargs(iyx__nwml, (fpl__ilrq,))
    c.pyapi.decref(iyx__nwml)
    c.pyapi.decref(fpl__ilrq)
    c.context.nrt.decref(c.builder, typ, val)
    return pykl__cvzd


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
        arstb__cezwf = context.get_constant(types.int64, 0)
        for i, yttb__wzm in enumerate(table_type.arr_types):
            pxls__vyc = getattr(table, f'block_{i}')
            oaij__zaqsy = ListInstance(context, builder, types.List(
                yttb__wzm), pxls__vyc)
            arstb__cezwf = builder.add(arstb__cezwf, oaij__zaqsy.size)
        return arstb__cezwf
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    wdd__mzgfg = table_type.block_nums[col_ind]
    gika__lnl = table_type.block_offsets[col_ind]
    pxls__vyc = getattr(table, f'block_{wdd__mzgfg}')
    dvqr__exuu = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    vbs__wsvhy = context.get_constant(types.int64, col_ind)
    swp__hvk = context.get_constant(types.int64, gika__lnl)
    sre__uwukm = table_arg, pxls__vyc, swp__hvk, vbs__wsvhy
    ensure_column_unboxed_codegen(context, builder, dvqr__exuu, sre__uwukm)
    oaij__zaqsy = ListInstance(context, builder, types.List(arr_type),
        pxls__vyc)
    arr = oaij__zaqsy.getitem(gika__lnl)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, vvqq__fcw = args
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
    rjgch__jgt = list(ind_typ.instance_type.meta)
    wso__zjs = defaultdict(list)
    for ind in rjgch__jgt:
        wso__zjs[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, vvqq__fcw = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for wdd__mzgfg, sglur__soak in wso__zjs.items():
            arr_type = table_type.blk_to_type[wdd__mzgfg]
            pxls__vyc = getattr(table, f'block_{wdd__mzgfg}')
            oaij__zaqsy = ListInstance(context, builder, types.List(
                arr_type), pxls__vyc)
            mepmu__dcx = context.get_constant_null(arr_type)
            if len(sglur__soak) == 1:
                gika__lnl = sglur__soak[0]
                arr = oaij__zaqsy.getitem(gika__lnl)
                context.nrt.decref(builder, arr_type, arr)
                oaij__zaqsy.inititem(gika__lnl, mepmu__dcx, incref=False)
            else:
                tbg__jaktk = context.get_constant(types.int64, len(sglur__soak)
                    )
                szgm__vps = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(sglur__soak, dtype
                    =np.int64))
                nqmvc__xouh = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, szgm__vps)
                with cgutils.for_range(builder, tbg__jaktk) as ndkuw__amzq:
                    i = ndkuw__amzq.index
                    gika__lnl = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        nqmvc__xouh, i)
                    arr = oaij__zaqsy.getitem(gika__lnl)
                    context.nrt.decref(builder, arr_type, arr)
                    oaij__zaqsy.inititem(gika__lnl, mepmu__dcx, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    iazpi__hsreo = context.get_constant(types.int64, 0)
    urne__tpjlv = context.get_constant(types.int64, 1)
    huko__vyke = arr_type not in in_table_type.type_to_blk
    for yttb__wzm, wdd__mzgfg in out_table_type.type_to_blk.items():
        if yttb__wzm in in_table_type.type_to_blk:
            xytu__bqrq = in_table_type.type_to_blk[yttb__wzm]
            swwe__nns = ListInstance(context, builder, types.List(yttb__wzm
                ), getattr(in_table, f'block_{xytu__bqrq}'))
            context.nrt.incref(builder, types.List(yttb__wzm), swwe__nns.value)
            setattr(out_table, f'block_{wdd__mzgfg}', swwe__nns.value)
    if huko__vyke:
        vvqq__fcw, swwe__nns = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), urne__tpjlv)
        swwe__nns.size = urne__tpjlv
        swwe__nns.inititem(iazpi__hsreo, arr_arg, incref=True)
        wdd__mzgfg = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{wdd__mzgfg}', swwe__nns.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        wdd__mzgfg = out_table_type.type_to_blk[arr_type]
        swwe__nns = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{wdd__mzgfg}'))
        if is_new_col:
            n = swwe__nns.size
            qxiin__trx = builder.add(n, urne__tpjlv)
            swwe__nns.resize(qxiin__trx)
            swwe__nns.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            cnnw__ksj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            swwe__nns.setitem(cnnw__ksj, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            cnnw__ksj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = swwe__nns.size
            qxiin__trx = builder.add(n, urne__tpjlv)
            swwe__nns.resize(qxiin__trx)
            context.nrt.incref(builder, arr_type, swwe__nns.getitem(cnnw__ksj))
            swwe__nns.move(builder.add(cnnw__ksj, urne__tpjlv), cnnw__ksj,
                builder.sub(n, cnnw__ksj))
            swwe__nns.setitem(cnnw__ksj, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    rmqft__plbe = in_table_type.arr_types[col_ind]
    if rmqft__plbe in out_table_type.type_to_blk:
        wdd__mzgfg = out_table_type.type_to_blk[rmqft__plbe]
        lus__zwj = getattr(out_table, f'block_{wdd__mzgfg}')
        bokp__axwh = types.List(rmqft__plbe)
        cnnw__ksj = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        vigo__eqi = bokp__axwh.dtype(bokp__axwh, types.intp)
        kelg__fcr = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), vigo__eqi, (lus__zwj, cnnw__ksj))
        context.nrt.decref(builder, rmqft__plbe, kelg__fcr)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    ddiva__sfy = list(table.arr_types)
    if ind == len(ddiva__sfy):
        fzrga__mcqe = None
        ddiva__sfy.append(arr_type)
    else:
        fzrga__mcqe = table.arr_types[ind]
        ddiva__sfy[ind] = arr_type
    blf__rseyb = TableType(tuple(ddiva__sfy))
    cptc__yao = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': blf__rseyb}
    lgu__ewt = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    lgu__ewt += f'  T2 = init_table(out_table_typ, False)\n'
    lgu__ewt += f'  T2 = set_table_len(T2, len(table))\n'
    lgu__ewt += f'  T2 = set_table_parent(T2, table)\n'
    for typ, wdd__mzgfg in blf__rseyb.type_to_blk.items():
        if typ in table.type_to_blk:
            jdxed__emkee = table.type_to_blk[typ]
            lgu__ewt += (
                f'  arr_list_{wdd__mzgfg} = get_table_block(table, {jdxed__emkee})\n'
                )
            lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_{wdd__mzgfg}, {len(blf__rseyb.block_to_arr_ind[wdd__mzgfg])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[jdxed__emkee]
                ) & used_cols:
                lgu__ewt += f'  for i in range(len(arr_list_{wdd__mzgfg})):\n'
                if typ not in (fzrga__mcqe, arr_type):
                    lgu__ewt += (
                        f'    out_arr_list_{wdd__mzgfg}[i] = arr_list_{wdd__mzgfg}[i]\n'
                        )
                else:
                    inzqt__mlmab = table.block_to_arr_ind[jdxed__emkee]
                    dafy__wkjvh = np.empty(len(inzqt__mlmab), np.int64)
                    ejqb__vmxxm = False
                    for hfv__hxg, vwgzp__gbdwi in enumerate(inzqt__mlmab):
                        if vwgzp__gbdwi != ind:
                            gyi__lhur = blf__rseyb.block_offsets[vwgzp__gbdwi]
                        else:
                            gyi__lhur = -1
                            ejqb__vmxxm = True
                        dafy__wkjvh[hfv__hxg] = gyi__lhur
                    cptc__yao[f'out_idxs_{wdd__mzgfg}'] = np.array(dafy__wkjvh,
                        np.int64)
                    lgu__ewt += f'    out_idx = out_idxs_{wdd__mzgfg}[i]\n'
                    if ejqb__vmxxm:
                        lgu__ewt += f'    if out_idx == -1:\n'
                        lgu__ewt += f'      continue\n'
                    lgu__ewt += f"""    out_arr_list_{wdd__mzgfg}[out_idx] = arr_list_{wdd__mzgfg}[i]
"""
            if typ == arr_type and not is_null:
                lgu__ewt += (
                    f'  out_arr_list_{wdd__mzgfg}[{blf__rseyb.block_offsets[ind]}] = arr\n'
                    )
        else:
            cptc__yao[f'arr_list_typ_{wdd__mzgfg}'] = types.List(arr_type)
            lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_typ_{wdd__mzgfg}, 1, False)
"""
            if not is_null:
                lgu__ewt += f'  out_arr_list_{wdd__mzgfg}[0] = arr\n'
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  return T2\n'
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        krp__kxkp = None
    else:
        krp__kxkp = set(used_cols.instance_type.meta)
    pwg__uyeu = get_overload_const_int(ind)
    return generate_set_table_data_code(table, pwg__uyeu, arr, krp__kxkp)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    pwg__uyeu = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        krp__kxkp = None
    else:
        krp__kxkp = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, pwg__uyeu, arr_type,
        krp__kxkp, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wxwc__yngop = args[0]
    if equiv_set.has_shape(wxwc__yngop):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wxwc__yngop)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    ucvt__kykdc = []
    for yttb__wzm, wdd__mzgfg in table_type.type_to_blk.items():
        bff__tlri = len(table_type.block_to_arr_ind[wdd__mzgfg])
        joc__pqwq = []
        for i in range(bff__tlri):
            vwgzp__gbdwi = table_type.block_to_arr_ind[wdd__mzgfg][i]
            joc__pqwq.append(pyval.arrays[vwgzp__gbdwi])
        ucvt__kykdc.append(context.get_constant_generic(builder, types.List
            (yttb__wzm), joc__pqwq))
    kvkvn__dghjv = context.get_constant_null(types.pyobject)
    lydo__frigt = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(ucvt__kykdc + [kvkvn__dghjv,
        lydo__frigt])


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
        for yttb__wzm, wdd__mzgfg in out_table_type.type_to_blk.items():
            oeonb__kmwr = context.get_constant_null(types.List(yttb__wzm))
            setattr(table, f'block_{wdd__mzgfg}', oeonb__kmwr)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    iqyxa__aargx = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        iqyxa__aargx[typ.dtype] = i
    xeqy__qcaum = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(xeqy__qcaum, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ffo__dotqs, vvqq__fcw = args
        table = cgutils.create_struct_proxy(xeqy__qcaum)(context, builder)
        for yttb__wzm, wdd__mzgfg in xeqy__qcaum.type_to_blk.items():
            idx = iqyxa__aargx[yttb__wzm]
            cqndj__lpy = signature(types.List(yttb__wzm),
                tuple_of_lists_type, types.literal(idx))
            dayr__eha = ffo__dotqs, idx
            mkq__djbw = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, cqndj__lpy, dayr__eha)
            setattr(table, f'block_{wdd__mzgfg}', mkq__djbw)
        return table._getvalue()
    sig = xeqy__qcaum(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    wdd__mzgfg = get_overload_const_int(blk_type)
    arr_type = None
    for yttb__wzm, bnpmd__fpwr in table_type.type_to_blk.items():
        if bnpmd__fpwr == wdd__mzgfg:
            arr_type = yttb__wzm
            break
    assert arr_type is not None, 'invalid table type block'
    apxc__gdbd = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        pxls__vyc = getattr(table, f'block_{wdd__mzgfg}')
        return impl_ret_borrowed(context, builder, apxc__gdbd, pxls__vyc)
    sig = apxc__gdbd(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, bcw__ccxd = args
        mmerg__pdkx = context.get_python_api(builder)
        vvdf__ihdwj = used_cols_typ == types.none
        if not vvdf__ihdwj:
            yuco__cpjh = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), bcw__ccxd)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for yttb__wzm, wdd__mzgfg in table_type.type_to_blk.items():
            tbg__jaktk = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[wdd__mzgfg]))
            vwl__xbahe = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                wdd__mzgfg], dtype=np.int64))
            uun__kcjlj = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, vwl__xbahe)
            pxls__vyc = getattr(table, f'block_{wdd__mzgfg}')
            with cgutils.for_range(builder, tbg__jaktk) as ndkuw__amzq:
                i = ndkuw__amzq.index
                vwgzp__gbdwi = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    uun__kcjlj, i)
                dvqr__exuu = types.none(table_type, types.List(yttb__wzm),
                    types.int64, types.int64)
                sre__uwukm = table_arg, pxls__vyc, i, vwgzp__gbdwi
                if vvdf__ihdwj:
                    ensure_column_unboxed_codegen(context, builder,
                        dvqr__exuu, sre__uwukm)
                else:
                    pghdm__akyp = yuco__cpjh.contains(vwgzp__gbdwi)
                    with builder.if_then(pghdm__akyp):
                        ensure_column_unboxed_codegen(context, builder,
                            dvqr__exuu, sre__uwukm)
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
    table_arg, nhuxx__onm, fofh__vbkl, qfuve__cvasd = args
    mmerg__pdkx = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    vduhx__nfz = cgutils.is_not_null(builder, table.parent)
    oaij__zaqsy = ListInstance(context, builder, sig.args[1], nhuxx__onm)
    jauxi__jqvyl = oaij__zaqsy.getitem(fofh__vbkl)
    flrro__uss = cgutils.alloca_once_value(builder, jauxi__jqvyl)
    rep__jrebo = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, flrro__uss, rep__jrebo)
    with builder.if_then(is_null):
        with builder.if_else(vduhx__nfz) as (dtmd__mfs, badrt__onn):
            with dtmd__mfs:
                dfx__mtl = get_df_obj_column_codegen(context, builder,
                    mmerg__pdkx, table.parent, qfuve__cvasd, sig.args[1].dtype)
                arr = mmerg__pdkx.to_native_value(sig.args[1].dtype, dfx__mtl
                    ).value
                oaij__zaqsy.inititem(fofh__vbkl, arr, incref=False)
                mmerg__pdkx.decref(dfx__mtl)
            with badrt__onn:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    wdd__mzgfg = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, suyy__tub, vvqq__fcw = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{wdd__mzgfg}', suyy__tub)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, mtl__vglma = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = mtl__vglma
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        bhnat__lqn, qvpfr__kfanl = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, qvpfr__kfanl)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, bhnat__lqn)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    apxc__gdbd = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(apxc__gdbd, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        apxc__gdbd = types.List(to_str_arr_if_dict_array(apxc__gdbd.dtype))

    def codegen(context, builder, sig, args):
        cjl__mjdld = args[1]
        vvqq__fcw, swwe__nns = ListInstance.allocate_ex(context, builder,
            apxc__gdbd, cjl__mjdld)
        swwe__nns.size = cjl__mjdld
        return swwe__nns.value
    sig = apxc__gdbd(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    hikh__tiqu = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(hikh__tiqu)

    def codegen(context, builder, sig, args):
        cjl__mjdld, vvqq__fcw = args
        vvqq__fcw, swwe__nns = ListInstance.allocate_ex(context, builder,
            list_type, cjl__mjdld)
        swwe__nns.size = cjl__mjdld
        return swwe__nns.value
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
        xavpf__rmn = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(xavpf__rmn)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    cptc__yao = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        mirk__ghhv = used_cols.instance_type
        zgsc__uolg = np.array(mirk__ghhv.meta, dtype=np.int64)
        cptc__yao['used_cols_vals'] = zgsc__uolg
        ptdmq__rih = set([T.block_nums[i] for i in zgsc__uolg])
    else:
        zgsc__uolg = None
    lgu__ewt = 'def table_filter_func(T, idx, used_cols=None):\n'
    lgu__ewt += f'  T2 = init_table(T, False)\n'
    lgu__ewt += f'  l = 0\n'
    if zgsc__uolg is not None and len(zgsc__uolg) == 0:
        lgu__ewt += f'  l = _get_idx_length(idx, len(T))\n'
        lgu__ewt += f'  T2 = set_table_len(T2, l)\n'
        lgu__ewt += f'  return T2\n'
        klzzt__tsomv = {}
        exec(lgu__ewt, cptc__yao, klzzt__tsomv)
        return klzzt__tsomv['table_filter_func']
    if zgsc__uolg is not None:
        lgu__ewt += f'  used_set = set(used_cols_vals)\n'
    for wdd__mzgfg in T.type_to_blk.values():
        lgu__ewt += (
            f'  arr_list_{wdd__mzgfg} = get_table_block(T, {wdd__mzgfg})\n')
        lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_{wdd__mzgfg}, len(arr_list_{wdd__mzgfg}), False)
"""
        if zgsc__uolg is None or wdd__mzgfg in ptdmq__rih:
            cptc__yao[f'arr_inds_{wdd__mzgfg}'] = np.array(T.
                block_to_arr_ind[wdd__mzgfg], dtype=np.int64)
            lgu__ewt += f'  for i in range(len(arr_list_{wdd__mzgfg})):\n'
            lgu__ewt += (
                f'    arr_ind_{wdd__mzgfg} = arr_inds_{wdd__mzgfg}[i]\n')
            if zgsc__uolg is not None:
                lgu__ewt += (
                    f'    if arr_ind_{wdd__mzgfg} not in used_set: continue\n')
            lgu__ewt += f"""    ensure_column_unboxed(T, arr_list_{wdd__mzgfg}, i, arr_ind_{wdd__mzgfg})
"""
            lgu__ewt += f"""    out_arr_{wdd__mzgfg} = ensure_contig_if_np(arr_list_{wdd__mzgfg}[i][idx])
"""
            lgu__ewt += f'    l = len(out_arr_{wdd__mzgfg})\n'
            lgu__ewt += (
                f'    out_arr_list_{wdd__mzgfg}[i] = out_arr_{wdd__mzgfg}\n')
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  T2 = set_table_len(T2, l)\n'
    lgu__ewt += f'  return T2\n'
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    obon__jterd = list(idx.instance_type.meta)
    ddiva__sfy = tuple(np.array(T.arr_types, dtype=object)[obon__jterd])
    blf__rseyb = TableType(ddiva__sfy)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    cjdbc__iufo = is_overload_true(copy_arrs)
    cptc__yao = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': blf__rseyb}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        lpgx__vdmie = set(kept_cols)
        cptc__yao['kept_cols'] = np.array(kept_cols, np.int64)
        vhdvi__skyh = True
    else:
        vhdvi__skyh = False
    dqmp__qwsti = {i: c for i, c in enumerate(obon__jterd)}
    lgu__ewt = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    lgu__ewt += f'  T2 = init_table(out_table_typ, False)\n'
    lgu__ewt += f'  T2 = set_table_len(T2, len(T))\n'
    if vhdvi__skyh and len(lpgx__vdmie) == 0:
        lgu__ewt += f'  return T2\n'
        klzzt__tsomv = {}
        exec(lgu__ewt, cptc__yao, klzzt__tsomv)
        return klzzt__tsomv['table_subset']
    if vhdvi__skyh:
        lgu__ewt += f'  kept_cols_set = set(kept_cols)\n'
    for typ, wdd__mzgfg in blf__rseyb.type_to_blk.items():
        jdxed__emkee = T.type_to_blk[typ]
        lgu__ewt += (
            f'  arr_list_{wdd__mzgfg} = get_table_block(T, {jdxed__emkee})\n')
        lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_{wdd__mzgfg}, {len(blf__rseyb.block_to_arr_ind[wdd__mzgfg])}, False)
"""
        ssft__ftrj = True
        if vhdvi__skyh:
            sxhbt__itaz = set(blf__rseyb.block_to_arr_ind[wdd__mzgfg])
            jdff__uuy = sxhbt__itaz & lpgx__vdmie
            ssft__ftrj = len(jdff__uuy) > 0
        if ssft__ftrj:
            cptc__yao[f'out_arr_inds_{wdd__mzgfg}'] = np.array(blf__rseyb.
                block_to_arr_ind[wdd__mzgfg], dtype=np.int64)
            lgu__ewt += f'  for i in range(len(out_arr_list_{wdd__mzgfg})):\n'
            lgu__ewt += (
                f'    out_arr_ind_{wdd__mzgfg} = out_arr_inds_{wdd__mzgfg}[i]\n'
                )
            if vhdvi__skyh:
                lgu__ewt += (
                    f'    if out_arr_ind_{wdd__mzgfg} not in kept_cols_set: continue\n'
                    )
            zvi__nfwy = []
            tlljf__ljq = []
            for wgqtc__yrrq in blf__rseyb.block_to_arr_ind[wdd__mzgfg]:
                abqf__ycxd = dqmp__qwsti[wgqtc__yrrq]
                zvi__nfwy.append(abqf__ycxd)
                qqxr__xzk = T.block_offsets[abqf__ycxd]
                tlljf__ljq.append(qqxr__xzk)
            cptc__yao[f'in_logical_idx_{wdd__mzgfg}'] = np.array(zvi__nfwy,
                dtype=np.int64)
            cptc__yao[f'in_physical_idx_{wdd__mzgfg}'] = np.array(tlljf__ljq,
                dtype=np.int64)
            lgu__ewt += (
                f'    logical_idx_{wdd__mzgfg} = in_logical_idx_{wdd__mzgfg}[i]\n'
                )
            lgu__ewt += (
                f'    physical_idx_{wdd__mzgfg} = in_physical_idx_{wdd__mzgfg}[i]\n'
                )
            lgu__ewt += f"""    ensure_column_unboxed(T, arr_list_{wdd__mzgfg}, physical_idx_{wdd__mzgfg}, logical_idx_{wdd__mzgfg})
"""
            jpwpb__anndu = '.copy()' if cjdbc__iufo else ''
            lgu__ewt += f"""    out_arr_list_{wdd__mzgfg}[i] = arr_list_{wdd__mzgfg}[physical_idx_{wdd__mzgfg}]{jpwpb__anndu}
"""
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  return T2\n'
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    wxwc__yngop = args[0]
    if equiv_set.has_shape(wxwc__yngop):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=wxwc__yngop, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (wxwc__yngop)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    wxwc__yngop = args[0]
    if equiv_set.has_shape(wxwc__yngop):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            wxwc__yngop)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    lgu__ewt = 'def impl(T):\n'
    lgu__ewt += f'  T2 = init_table(T, True)\n'
    lgu__ewt += f'  l = len(T)\n'
    cptc__yao = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for wdd__mzgfg in T.type_to_blk.values():
        cptc__yao[f'arr_inds_{wdd__mzgfg}'] = np.array(T.block_to_arr_ind[
            wdd__mzgfg], dtype=np.int64)
        lgu__ewt += (
            f'  arr_list_{wdd__mzgfg} = get_table_block(T, {wdd__mzgfg})\n')
        lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_{wdd__mzgfg}, len(arr_list_{wdd__mzgfg}), True)
"""
        lgu__ewt += f'  for i in range(len(arr_list_{wdd__mzgfg})):\n'
        lgu__ewt += f'    arr_ind_{wdd__mzgfg} = arr_inds_{wdd__mzgfg}[i]\n'
        lgu__ewt += f"""    ensure_column_unboxed(T, arr_list_{wdd__mzgfg}, i, arr_ind_{wdd__mzgfg})
"""
        lgu__ewt += (
            f'    out_arr_{wdd__mzgfg} = decode_if_dict_array(arr_list_{wdd__mzgfg}[i])\n'
            )
        lgu__ewt += (
            f'    out_arr_list_{wdd__mzgfg}[i] = out_arr_{wdd__mzgfg}\n')
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  T2 = set_table_len(T2, l)\n'
    lgu__ewt += f'  return T2\n'
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['impl']


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
        uwbd__ktwrk = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        uwbd__ktwrk = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            uwbd__ktwrk.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        xuh__csajw, owtm__oiijk = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = owtm__oiijk
        ucvt__kykdc = cgutils.unpack_tuple(builder, xuh__csajw)
        for i, pxls__vyc in enumerate(ucvt__kykdc):
            setattr(table, f'block_{i}', pxls__vyc)
            context.nrt.incref(builder, types.List(uwbd__ktwrk[i]), pxls__vyc)
        return table._getvalue()
    table_type = TableType(tuple(uwbd__ktwrk), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    cptc__yao = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        cptc__yao['kept_cols'] = np.array(list(kept_cols), np.int64)
        vhdvi__skyh = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        vhdvi__skyh = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    iaje__hja = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        iaje__hja else extra_arrs_t.types[i - iaje__hja] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    lgu__ewt = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    lgu__ewt += f'  T1 = in_table_t\n'
    lgu__ewt += f'  T2 = init_table(out_table_type, False)\n'
    lgu__ewt += f'  T2 = set_table_len(T2, len(T1))\n'
    if vhdvi__skyh and len(kept_cols) == 0:
        lgu__ewt += f'  return T2\n'
        klzzt__tsomv = {}
        exec(lgu__ewt, cptc__yao, klzzt__tsomv)
        return klzzt__tsomv['impl']
    if vhdvi__skyh:
        lgu__ewt += f'  kept_cols_set = set(kept_cols)\n'
    for typ, wdd__mzgfg in out_table_type.type_to_blk.items():
        cptc__yao[f'arr_list_typ_{wdd__mzgfg}'] = types.List(typ)
        tbg__jaktk = len(out_table_type.block_to_arr_ind[wdd__mzgfg])
        lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_typ_{wdd__mzgfg}, {tbg__jaktk}, False)
"""
        if typ in in_table_t.type_to_blk:
            raa__bcwx = in_table_t.type_to_blk[typ]
            bgqaz__etqml = []
            ath__lsi = []
            for zlgx__isukd in out_table_type.block_to_arr_ind[wdd__mzgfg]:
                mjki__fkj = in_col_inds[zlgx__isukd]
                if mjki__fkj < iaje__hja:
                    bgqaz__etqml.append(in_table_t.block_offsets[mjki__fkj])
                    ath__lsi.append(mjki__fkj)
                else:
                    bgqaz__etqml.append(-1)
                    ath__lsi.append(-1)
            cptc__yao[f'in_idxs_{wdd__mzgfg}'] = np.array(bgqaz__etqml, np.
                int64)
            cptc__yao[f'in_arr_inds_{wdd__mzgfg}'] = np.array(ath__lsi, np.
                int64)
            if vhdvi__skyh:
                cptc__yao[f'out_arr_inds_{wdd__mzgfg}'] = np.array(
                    out_table_type.block_to_arr_ind[wdd__mzgfg], dtype=np.int64
                    )
            lgu__ewt += (
                f'  in_arr_list_{wdd__mzgfg} = get_table_block(T1, {raa__bcwx})\n'
                )
            lgu__ewt += f'  for i in range(len(out_arr_list_{wdd__mzgfg})):\n'
            lgu__ewt += (
                f'    in_offset_{wdd__mzgfg} = in_idxs_{wdd__mzgfg}[i]\n')
            lgu__ewt += f'    if in_offset_{wdd__mzgfg} == -1:\n'
            lgu__ewt += f'      continue\n'
            lgu__ewt += (
                f'    in_arr_ind_{wdd__mzgfg} = in_arr_inds_{wdd__mzgfg}[i]\n')
            if vhdvi__skyh:
                lgu__ewt += (
                    f'    if out_arr_inds_{wdd__mzgfg}[i] not in kept_cols_set: continue\n'
                    )
            lgu__ewt += f"""    ensure_column_unboxed(T1, in_arr_list_{wdd__mzgfg}, in_offset_{wdd__mzgfg}, in_arr_ind_{wdd__mzgfg})
"""
            lgu__ewt += f"""    out_arr_list_{wdd__mzgfg}[i] = in_arr_list_{wdd__mzgfg}[in_offset_{wdd__mzgfg}]
"""
        for i, zlgx__isukd in enumerate(out_table_type.block_to_arr_ind[
            wdd__mzgfg]):
            if zlgx__isukd not in kept_cols:
                continue
            mjki__fkj = in_col_inds[zlgx__isukd]
            if mjki__fkj >= iaje__hja:
                lgu__ewt += f"""  out_arr_list_{wdd__mzgfg}[{i}] = extra_arrs_t[{mjki__fkj - iaje__hja}]
"""
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  return T2\n'
    cptc__yao.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    iaje__hja = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < iaje__hja else
        extra_arrs_t.types[i - iaje__hja] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    vddvc__aephv = None
    if not is_overload_none(in_table_t):
        for i, yttb__wzm in enumerate(in_table_t.types):
            if yttb__wzm != types.none:
                vddvc__aephv = f'in_table_t[{i}]'
                break
    if vddvc__aephv is None:
        for i, yttb__wzm in enumerate(extra_arrs_t.types):
            if yttb__wzm != types.none:
                vddvc__aephv = f'extra_arrs_t[{i}]'
                break
    assert vddvc__aephv is not None, 'no array found in input data'
    lgu__ewt = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    lgu__ewt += f'  T1 = in_table_t\n'
    lgu__ewt += f'  T2 = init_table(out_table_type, False)\n'
    lgu__ewt += f'  T2 = set_table_len(T2, len({vddvc__aephv}))\n'
    cptc__yao = {}
    for typ, wdd__mzgfg in out_table_type.type_to_blk.items():
        cptc__yao[f'arr_list_typ_{wdd__mzgfg}'] = types.List(typ)
        tbg__jaktk = len(out_table_type.block_to_arr_ind[wdd__mzgfg])
        lgu__ewt += f"""  out_arr_list_{wdd__mzgfg} = alloc_list_like(arr_list_typ_{wdd__mzgfg}, {tbg__jaktk}, False)
"""
        for i, zlgx__isukd in enumerate(out_table_type.block_to_arr_ind[
            wdd__mzgfg]):
            if zlgx__isukd not in kept_cols:
                continue
            mjki__fkj = in_col_inds[zlgx__isukd]
            if mjki__fkj < iaje__hja:
                lgu__ewt += (
                    f'  out_arr_list_{wdd__mzgfg}[{i}] = T1[{mjki__fkj}]\n')
            else:
                lgu__ewt += f"""  out_arr_list_{wdd__mzgfg}[{i}] = extra_arrs_t[{mjki__fkj - iaje__hja}]
"""
        lgu__ewt += (
            f'  T2 = set_table_block(T2, out_arr_list_{wdd__mzgfg}, {wdd__mzgfg})\n'
            )
    lgu__ewt += f'  return T2\n'
    cptc__yao.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    klzzt__tsomv = {}
    exec(lgu__ewt, cptc__yao, klzzt__tsomv)
    return klzzt__tsomv['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    lck__duvzn = args[0]
    qnm__vlw = args[1]
    if equiv_set.has_shape(lck__duvzn):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            lck__duvzn)[0], None), pre=[])
    if equiv_set.has_shape(qnm__vlw):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            qnm__vlw)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
