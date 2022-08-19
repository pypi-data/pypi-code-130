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
            pta__lljbk = 0
            bbs__wxi = []
            for i in range(usecols[-1] + 1):
                if i == usecols[pta__lljbk]:
                    bbs__wxi.append(arrs[pta__lljbk])
                    pta__lljbk += 1
                else:
                    bbs__wxi.append(None)
            for fpf__uexdy in range(usecols[-1] + 1, num_arrs):
                bbs__wxi.append(None)
            self.arrays = bbs__wxi
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((wzvsp__snh == fyy__tcwfl).all() for wzvsp__snh,
            fyy__tcwfl in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        pxmc__xqs = len(self.arrays)
        ktpbx__fhtmo = dict(zip(range(pxmc__xqs), self.arrays))
        df = pd.DataFrame(ktpbx__fhtmo, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        vkb__gme = []
        kmb__ubzr = []
        dfe__rgamc = {}
        cosgb__gwikc = {}
        fdaaq__tghm = defaultdict(int)
        lwk__bdkky = defaultdict(list)
        if not has_runtime_cols:
            for i, lmymg__jrs in enumerate(arr_types):
                if lmymg__jrs not in dfe__rgamc:
                    fxewx__mcjgk = len(dfe__rgamc)
                    dfe__rgamc[lmymg__jrs] = fxewx__mcjgk
                    cosgb__gwikc[fxewx__mcjgk] = lmymg__jrs
                bira__dcdt = dfe__rgamc[lmymg__jrs]
                vkb__gme.append(bira__dcdt)
                kmb__ubzr.append(fdaaq__tghm[bira__dcdt])
                fdaaq__tghm[bira__dcdt] += 1
                lwk__bdkky[bira__dcdt].append(i)
        self.block_nums = vkb__gme
        self.block_offsets = kmb__ubzr
        self.type_to_blk = dfe__rgamc
        self.blk_to_type = cosgb__gwikc
        self.block_to_arr_ind = lwk__bdkky
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
            ptur__xahm = [(f'block_{i}', types.List(lmymg__jrs)) for i,
                lmymg__jrs in enumerate(fe_type.arr_types)]
        else:
            ptur__xahm = [(f'block_{bira__dcdt}', types.List(lmymg__jrs)) for
                lmymg__jrs, bira__dcdt in fe_type.type_to_blk.items()]
        ptur__xahm.append(('parent', types.pyobject))
        ptur__xahm.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, ptur__xahm)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    uzqe__gbd = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    iec__hvjgt = c.pyapi.make_none()
    knzak__dzgc = c.context.get_constant(types.int64, 0)
    lhv__kysh = cgutils.alloca_once_value(c.builder, knzak__dzgc)
    for lmymg__jrs, bira__dcdt in typ.type_to_blk.items():
        scqhx__tqkhb = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[bira__dcdt]))
        fpf__uexdy, egjjs__hqb = ListInstance.allocate_ex(c.context, c.
            builder, types.List(lmymg__jrs), scqhx__tqkhb)
        egjjs__hqb.size = scqhx__tqkhb
        mix__xzbz = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[bira__dcdt],
            dtype=np.int64))
        zkjh__wrnoh = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, mix__xzbz)
        with cgutils.for_range(c.builder, scqhx__tqkhb) as sgg__cujnl:
            i = sgg__cujnl.index
            icmje__bdmmf = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), zkjh__wrnoh, i)
            bat__dkq = c.pyapi.long_from_longlong(icmje__bdmmf)
            lrq__dxb = c.pyapi.object_getitem(uzqe__gbd, bat__dkq)
            zhdl__nuebr = c.builder.icmp_unsigned('==', lrq__dxb, iec__hvjgt)
            with c.builder.if_else(zhdl__nuebr) as (sgij__oavpf, gsp__nea):
                with sgij__oavpf:
                    xbbo__silm = c.context.get_constant_null(lmymg__jrs)
                    egjjs__hqb.inititem(i, xbbo__silm, incref=False)
                with gsp__nea:
                    oar__wwm = c.pyapi.call_method(lrq__dxb, '__len__', ())
                    wiw__cdeg = c.pyapi.long_as_longlong(oar__wwm)
                    c.builder.store(wiw__cdeg, lhv__kysh)
                    c.pyapi.decref(oar__wwm)
                    arr = c.pyapi.to_native_value(lmymg__jrs, lrq__dxb).value
                    egjjs__hqb.inititem(i, arr, incref=False)
            c.pyapi.decref(lrq__dxb)
            c.pyapi.decref(bat__dkq)
        setattr(table, f'block_{bira__dcdt}', egjjs__hqb.value)
    table.len = c.builder.load(lhv__kysh)
    c.pyapi.decref(uzqe__gbd)
    c.pyapi.decref(iec__hvjgt)
    fflaq__wdj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=fflaq__wdj)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        nsfp__jqsfe = c.context.get_constant(types.int64, 0)
        for i, lmymg__jrs in enumerate(typ.arr_types):
            bbs__wxi = getattr(table, f'block_{i}')
            lyi__hczr = ListInstance(c.context, c.builder, types.List(
                lmymg__jrs), bbs__wxi)
            nsfp__jqsfe = c.builder.add(nsfp__jqsfe, lyi__hczr.size)
        pwfg__zno = c.pyapi.list_new(nsfp__jqsfe)
        nwqij__ekc = c.context.get_constant(types.int64, 0)
        for i, lmymg__jrs in enumerate(typ.arr_types):
            bbs__wxi = getattr(table, f'block_{i}')
            lyi__hczr = ListInstance(c.context, c.builder, types.List(
                lmymg__jrs), bbs__wxi)
            with cgutils.for_range(c.builder, lyi__hczr.size) as sgg__cujnl:
                i = sgg__cujnl.index
                arr = lyi__hczr.getitem(i)
                c.context.nrt.incref(c.builder, lmymg__jrs, arr)
                idx = c.builder.add(nwqij__ekc, i)
                c.pyapi.list_setitem(pwfg__zno, idx, c.pyapi.
                    from_native_value(lmymg__jrs, arr, c.env_manager))
            nwqij__ekc = c.builder.add(nwqij__ekc, lyi__hczr.size)
        qah__fai = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        ltw__usxc = c.pyapi.call_function_objargs(qah__fai, (pwfg__zno,))
        c.pyapi.decref(qah__fai)
        c.pyapi.decref(pwfg__zno)
        c.context.nrt.decref(c.builder, typ, val)
        return ltw__usxc
    pwfg__zno = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    xmfd__yoiht = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for lmymg__jrs, bira__dcdt in typ.type_to_blk.items():
        bbs__wxi = getattr(table, f'block_{bira__dcdt}')
        lyi__hczr = ListInstance(c.context, c.builder, types.List(
            lmymg__jrs), bbs__wxi)
        mix__xzbz = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[bira__dcdt],
            dtype=np.int64))
        zkjh__wrnoh = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, mix__xzbz)
        with cgutils.for_range(c.builder, lyi__hczr.size) as sgg__cujnl:
            i = sgg__cujnl.index
            icmje__bdmmf = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), zkjh__wrnoh, i)
            arr = lyi__hczr.getitem(i)
            fyxmt__efeu = cgutils.alloca_once_value(c.builder, arr)
            and__xddhv = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(lmymg__jrs))
            is_null = is_ll_eq(c.builder, fyxmt__efeu, and__xddhv)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (sgij__oavpf, gsp__nea):
                with sgij__oavpf:
                    iec__hvjgt = c.pyapi.make_none()
                    c.pyapi.list_setitem(pwfg__zno, icmje__bdmmf, iec__hvjgt)
                with gsp__nea:
                    lrq__dxb = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, xmfd__yoiht)
                        ) as (dnda__emisv, iid__lhz):
                        with dnda__emisv:
                            zkaww__ggih = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                icmje__bdmmf, lmymg__jrs)
                            c.builder.store(zkaww__ggih, lrq__dxb)
                        with iid__lhz:
                            c.context.nrt.incref(c.builder, lmymg__jrs, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                lmymg__jrs, arr, c.env_manager), lrq__dxb)
                    c.pyapi.list_setitem(pwfg__zno, icmje__bdmmf, c.builder
                        .load(lrq__dxb))
    qah__fai = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    ltw__usxc = c.pyapi.call_function_objargs(qah__fai, (pwfg__zno,))
    c.pyapi.decref(qah__fai)
    c.pyapi.decref(pwfg__zno)
    c.context.nrt.decref(c.builder, typ, val)
    return ltw__usxc


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
        oqb__knat = context.get_constant(types.int64, 0)
        for i, lmymg__jrs in enumerate(table_type.arr_types):
            bbs__wxi = getattr(table, f'block_{i}')
            lyi__hczr = ListInstance(context, builder, types.List(
                lmymg__jrs), bbs__wxi)
            oqb__knat = builder.add(oqb__knat, lyi__hczr.size)
        return oqb__knat
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    bira__dcdt = table_type.block_nums[col_ind]
    vfjyu__moua = table_type.block_offsets[col_ind]
    bbs__wxi = getattr(table, f'block_{bira__dcdt}')
    qwot__wdh = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    zdfix__vlstd = context.get_constant(types.int64, col_ind)
    enh__fgx = context.get_constant(types.int64, vfjyu__moua)
    xrg__rviqv = table_arg, bbs__wxi, enh__fgx, zdfix__vlstd
    ensure_column_unboxed_codegen(context, builder, qwot__wdh, xrg__rviqv)
    lyi__hczr = ListInstance(context, builder, types.List(arr_type), bbs__wxi)
    arr = lyi__hczr.getitem(vfjyu__moua)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, fpf__uexdy = args
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
    bhkv__gvls = list(ind_typ.instance_type.meta)
    aetq__xyvpf = defaultdict(list)
    for ind in bhkv__gvls:
        aetq__xyvpf[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, fpf__uexdy = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for bira__dcdt, ysjpg__ncou in aetq__xyvpf.items():
            arr_type = table_type.blk_to_type[bira__dcdt]
            bbs__wxi = getattr(table, f'block_{bira__dcdt}')
            lyi__hczr = ListInstance(context, builder, types.List(arr_type),
                bbs__wxi)
            xbbo__silm = context.get_constant_null(arr_type)
            if len(ysjpg__ncou) == 1:
                vfjyu__moua = ysjpg__ncou[0]
                arr = lyi__hczr.getitem(vfjyu__moua)
                context.nrt.decref(builder, arr_type, arr)
                lyi__hczr.inititem(vfjyu__moua, xbbo__silm, incref=False)
            else:
                scqhx__tqkhb = context.get_constant(types.int64, len(
                    ysjpg__ncou))
                iqw__eempp = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(ysjpg__ncou, dtype
                    =np.int64))
                mlma__jqz = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, iqw__eempp)
                with cgutils.for_range(builder, scqhx__tqkhb) as sgg__cujnl:
                    i = sgg__cujnl.index
                    vfjyu__moua = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), mlma__jqz, i)
                    arr = lyi__hczr.getitem(vfjyu__moua)
                    context.nrt.decref(builder, arr_type, arr)
                    lyi__hczr.inititem(vfjyu__moua, xbbo__silm, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    knzak__dzgc = context.get_constant(types.int64, 0)
    wvd__alz = context.get_constant(types.int64, 1)
    vhouh__isg = arr_type not in in_table_type.type_to_blk
    for lmymg__jrs, bira__dcdt in out_table_type.type_to_blk.items():
        if lmymg__jrs in in_table_type.type_to_blk:
            dkk__kkc = in_table_type.type_to_blk[lmymg__jrs]
            egjjs__hqb = ListInstance(context, builder, types.List(
                lmymg__jrs), getattr(in_table, f'block_{dkk__kkc}'))
            context.nrt.incref(builder, types.List(lmymg__jrs), egjjs__hqb.
                value)
            setattr(out_table, f'block_{bira__dcdt}', egjjs__hqb.value)
    if vhouh__isg:
        fpf__uexdy, egjjs__hqb = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), wvd__alz)
        egjjs__hqb.size = wvd__alz
        egjjs__hqb.inititem(knzak__dzgc, arr_arg, incref=True)
        bira__dcdt = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{bira__dcdt}', egjjs__hqb.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        bira__dcdt = out_table_type.type_to_blk[arr_type]
        egjjs__hqb = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{bira__dcdt}'))
        if is_new_col:
            n = egjjs__hqb.size
            ypz__rep = builder.add(n, wvd__alz)
            egjjs__hqb.resize(ypz__rep)
            egjjs__hqb.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            kcuoo__mhlj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            egjjs__hqb.setitem(kcuoo__mhlj, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            kcuoo__mhlj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = egjjs__hqb.size
            ypz__rep = builder.add(n, wvd__alz)
            egjjs__hqb.resize(ypz__rep)
            context.nrt.incref(builder, arr_type, egjjs__hqb.getitem(
                kcuoo__mhlj))
            egjjs__hqb.move(builder.add(kcuoo__mhlj, wvd__alz), kcuoo__mhlj,
                builder.sub(n, kcuoo__mhlj))
            egjjs__hqb.setitem(kcuoo__mhlj, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    nzrqz__kmzq = in_table_type.arr_types[col_ind]
    if nzrqz__kmzq in out_table_type.type_to_blk:
        bira__dcdt = out_table_type.type_to_blk[nzrqz__kmzq]
        tylz__obfp = getattr(out_table, f'block_{bira__dcdt}')
        ktqj__quipz = types.List(nzrqz__kmzq)
        kcuoo__mhlj = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        jvm__ywgw = ktqj__quipz.dtype(ktqj__quipz, types.intp)
        vlo__lwvnm = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), jvm__ywgw, (tylz__obfp, kcuoo__mhlj))
        context.nrt.decref(builder, nzrqz__kmzq, vlo__lwvnm)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    ydukt__dop = list(table.arr_types)
    if ind == len(ydukt__dop):
        qoe__abvkl = None
        ydukt__dop.append(arr_type)
    else:
        qoe__abvkl = table.arr_types[ind]
        ydukt__dop[ind] = arr_type
    doro__gda = TableType(tuple(ydukt__dop))
    ysvm__mgzl = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': doro__gda}
    lzh__vsypi = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    lzh__vsypi += f'  T2 = init_table(out_table_typ, False)\n'
    lzh__vsypi += f'  T2 = set_table_len(T2, len(table))\n'
    lzh__vsypi += f'  T2 = set_table_parent(T2, table)\n'
    for typ, bira__dcdt in doro__gda.type_to_blk.items():
        if typ in table.type_to_blk:
            uypcw__vlf = table.type_to_blk[typ]
            lzh__vsypi += (
                f'  arr_list_{bira__dcdt} = get_table_block(table, {uypcw__vlf})\n'
                )
            lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_{bira__dcdt}, {len(doro__gda.block_to_arr_ind[bira__dcdt])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[uypcw__vlf]
                ) & used_cols:
                lzh__vsypi += (
                    f'  for i in range(len(arr_list_{bira__dcdt})):\n')
                if typ not in (qoe__abvkl, arr_type):
                    lzh__vsypi += (
                        f'    out_arr_list_{bira__dcdt}[i] = arr_list_{bira__dcdt}[i]\n'
                        )
                else:
                    dvlc__oyj = table.block_to_arr_ind[uypcw__vlf]
                    hmbk__pbv = np.empty(len(dvlc__oyj), np.int64)
                    upfrp__dkd = False
                    for bfd__nepv, icmje__bdmmf in enumerate(dvlc__oyj):
                        if icmje__bdmmf != ind:
                            bzk__nqhxu = doro__gda.block_offsets[icmje__bdmmf]
                        else:
                            bzk__nqhxu = -1
                            upfrp__dkd = True
                        hmbk__pbv[bfd__nepv] = bzk__nqhxu
                    ysvm__mgzl[f'out_idxs_{bira__dcdt}'] = np.array(hmbk__pbv,
                        np.int64)
                    lzh__vsypi += f'    out_idx = out_idxs_{bira__dcdt}[i]\n'
                    if upfrp__dkd:
                        lzh__vsypi += f'    if out_idx == -1:\n'
                        lzh__vsypi += f'      continue\n'
                    lzh__vsypi += f"""    out_arr_list_{bira__dcdt}[out_idx] = arr_list_{bira__dcdt}[i]
"""
            if typ == arr_type and not is_null:
                lzh__vsypi += (
                    f'  out_arr_list_{bira__dcdt}[{doro__gda.block_offsets[ind]}] = arr\n'
                    )
        else:
            ysvm__mgzl[f'arr_list_typ_{bira__dcdt}'] = types.List(arr_type)
            lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_typ_{bira__dcdt}, 1, False)
"""
            if not is_null:
                lzh__vsypi += f'  out_arr_list_{bira__dcdt}[0] = arr\n'
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  return T2\n'
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        fbkc__qsysw = None
    else:
        fbkc__qsysw = set(used_cols.instance_type.meta)
    eybv__boq = get_overload_const_int(ind)
    return generate_set_table_data_code(table, eybv__boq, arr, fbkc__qsysw)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    eybv__boq = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        fbkc__qsysw = None
    else:
        fbkc__qsysw = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, eybv__boq, arr_type,
        fbkc__qsysw, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    akdkz__klgry = args[0]
    if equiv_set.has_shape(akdkz__klgry):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            akdkz__klgry)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    ibfy__cyh = []
    for lmymg__jrs, bira__dcdt in table_type.type_to_blk.items():
        bnzbl__afo = len(table_type.block_to_arr_ind[bira__dcdt])
        ehom__kdsa = []
        for i in range(bnzbl__afo):
            icmje__bdmmf = table_type.block_to_arr_ind[bira__dcdt][i]
            ehom__kdsa.append(pyval.arrays[icmje__bdmmf])
        ibfy__cyh.append(context.get_constant_generic(builder, types.List(
            lmymg__jrs), ehom__kdsa))
    orw__dosp = context.get_constant_null(types.pyobject)
    foue__cjxyv = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(ibfy__cyh + [orw__dosp, foue__cjxyv])


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
        for lmymg__jrs, bira__dcdt in out_table_type.type_to_blk.items():
            mdwx__snlw = context.get_constant_null(types.List(lmymg__jrs))
            setattr(table, f'block_{bira__dcdt}', mdwx__snlw)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    fyleg__rfc = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        fyleg__rfc[typ.dtype] = i
    babo__bzh = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(babo__bzh, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        zmk__kqyyx, fpf__uexdy = args
        table = cgutils.create_struct_proxy(babo__bzh)(context, builder)
        for lmymg__jrs, bira__dcdt in babo__bzh.type_to_blk.items():
            idx = fyleg__rfc[lmymg__jrs]
            jpfan__wupwq = signature(types.List(lmymg__jrs),
                tuple_of_lists_type, types.literal(idx))
            fee__hskx = zmk__kqyyx, idx
            hdz__evpm = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, jpfan__wupwq, fee__hskx)
            setattr(table, f'block_{bira__dcdt}', hdz__evpm)
        return table._getvalue()
    sig = babo__bzh(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    bira__dcdt = get_overload_const_int(blk_type)
    arr_type = None
    for lmymg__jrs, fyy__tcwfl in table_type.type_to_blk.items():
        if fyy__tcwfl == bira__dcdt:
            arr_type = lmymg__jrs
            break
    assert arr_type is not None, 'invalid table type block'
    eqgul__buum = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        bbs__wxi = getattr(table, f'block_{bira__dcdt}')
        return impl_ret_borrowed(context, builder, eqgul__buum, bbs__wxi)
    sig = eqgul__buum(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, qjlgp__rizq = args
        yhcr__pakb = context.get_python_api(builder)
        ukk__qslgj = used_cols_typ == types.none
        if not ukk__qslgj:
            gdgi__mqs = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), qjlgp__rizq)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for lmymg__jrs, bira__dcdt in table_type.type_to_blk.items():
            scqhx__tqkhb = context.get_constant(types.int64, len(table_type
                .block_to_arr_ind[bira__dcdt]))
            mix__xzbz = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                bira__dcdt], dtype=np.int64))
            zkjh__wrnoh = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, mix__xzbz)
            bbs__wxi = getattr(table, f'block_{bira__dcdt}')
            with cgutils.for_range(builder, scqhx__tqkhb) as sgg__cujnl:
                i = sgg__cujnl.index
                icmje__bdmmf = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    zkjh__wrnoh, i)
                qwot__wdh = types.none(table_type, types.List(lmymg__jrs),
                    types.int64, types.int64)
                xrg__rviqv = table_arg, bbs__wxi, i, icmje__bdmmf
                if ukk__qslgj:
                    ensure_column_unboxed_codegen(context, builder,
                        qwot__wdh, xrg__rviqv)
                else:
                    qqjo__rnwm = gdgi__mqs.contains(icmje__bdmmf)
                    with builder.if_then(qqjo__rnwm):
                        ensure_column_unboxed_codegen(context, builder,
                            qwot__wdh, xrg__rviqv)
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
    table_arg, vxu__kwb, hfft__vhjo, jdi__mtemw = args
    yhcr__pakb = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    xmfd__yoiht = cgutils.is_not_null(builder, table.parent)
    lyi__hczr = ListInstance(context, builder, sig.args[1], vxu__kwb)
    kiv__njtah = lyi__hczr.getitem(hfft__vhjo)
    fyxmt__efeu = cgutils.alloca_once_value(builder, kiv__njtah)
    and__xddhv = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, fyxmt__efeu, and__xddhv)
    with builder.if_then(is_null):
        with builder.if_else(xmfd__yoiht) as (sgij__oavpf, gsp__nea):
            with sgij__oavpf:
                lrq__dxb = get_df_obj_column_codegen(context, builder,
                    yhcr__pakb, table.parent, jdi__mtemw, sig.args[1].dtype)
                arr = yhcr__pakb.to_native_value(sig.args[1].dtype, lrq__dxb
                    ).value
                lyi__hczr.inititem(hfft__vhjo, arr, incref=False)
                yhcr__pakb.decref(lrq__dxb)
            with gsp__nea:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    bira__dcdt = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, umq__oenv, fpf__uexdy = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{bira__dcdt}', umq__oenv)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, mdifb__biz = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = mdifb__biz
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        exqxn__udh, jcx__qmp = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, jcx__qmp)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, exqxn__udh)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    eqgul__buum = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(eqgul__buum, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        eqgul__buum = types.List(to_str_arr_if_dict_array(eqgul__buum.dtype))

    def codegen(context, builder, sig, args):
        zefqr__zdac = args[1]
        fpf__uexdy, egjjs__hqb = ListInstance.allocate_ex(context, builder,
            eqgul__buum, zefqr__zdac)
        egjjs__hqb.size = zefqr__zdac
        return egjjs__hqb.value
    sig = eqgul__buum(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    edro__yad = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(edro__yad)

    def codegen(context, builder, sig, args):
        zefqr__zdac, fpf__uexdy = args
        fpf__uexdy, egjjs__hqb = ListInstance.allocate_ex(context, builder,
            list_type, zefqr__zdac)
        egjjs__hqb.size = zefqr__zdac
        return egjjs__hqb.value
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
        cezgy__mts = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(cezgy__mts)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    ysvm__mgzl = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        rht__ukm = used_cols.instance_type
        bime__cmmew = np.array(rht__ukm.meta, dtype=np.int64)
        ysvm__mgzl['used_cols_vals'] = bime__cmmew
        woszg__mie = set([T.block_nums[i] for i in bime__cmmew])
    else:
        bime__cmmew = None
    lzh__vsypi = 'def table_filter_func(T, idx, used_cols=None):\n'
    lzh__vsypi += f'  T2 = init_table(T, False)\n'
    lzh__vsypi += f'  l = 0\n'
    if bime__cmmew is not None and len(bime__cmmew) == 0:
        lzh__vsypi += f'  l = _get_idx_length(idx, len(T))\n'
        lzh__vsypi += f'  T2 = set_table_len(T2, l)\n'
        lzh__vsypi += f'  return T2\n'
        idldz__xnkt = {}
        exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
        return idldz__xnkt['table_filter_func']
    if bime__cmmew is not None:
        lzh__vsypi += f'  used_set = set(used_cols_vals)\n'
    for bira__dcdt in T.type_to_blk.values():
        lzh__vsypi += (
            f'  arr_list_{bira__dcdt} = get_table_block(T, {bira__dcdt})\n')
        lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_{bira__dcdt}, len(arr_list_{bira__dcdt}), False)
"""
        if bime__cmmew is None or bira__dcdt in woszg__mie:
            ysvm__mgzl[f'arr_inds_{bira__dcdt}'] = np.array(T.
                block_to_arr_ind[bira__dcdt], dtype=np.int64)
            lzh__vsypi += f'  for i in range(len(arr_list_{bira__dcdt})):\n'
            lzh__vsypi += (
                f'    arr_ind_{bira__dcdt} = arr_inds_{bira__dcdt}[i]\n')
            if bime__cmmew is not None:
                lzh__vsypi += (
                    f'    if arr_ind_{bira__dcdt} not in used_set: continue\n')
            lzh__vsypi += f"""    ensure_column_unboxed(T, arr_list_{bira__dcdt}, i, arr_ind_{bira__dcdt})
"""
            lzh__vsypi += f"""    out_arr_{bira__dcdt} = ensure_contig_if_np(arr_list_{bira__dcdt}[i][idx])
"""
            lzh__vsypi += f'    l = len(out_arr_{bira__dcdt})\n'
            lzh__vsypi += (
                f'    out_arr_list_{bira__dcdt}[i] = out_arr_{bira__dcdt}\n')
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  T2 = set_table_len(T2, l)\n'
    lzh__vsypi += f'  return T2\n'
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    xed__zjwy = list(idx.instance_type.meta)
    ydukt__dop = tuple(np.array(T.arr_types, dtype=object)[xed__zjwy])
    doro__gda = TableType(ydukt__dop)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    dzu__lynw = is_overload_true(copy_arrs)
    ysvm__mgzl = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': doro__gda}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        agkb__rbm = set(kept_cols)
        ysvm__mgzl['kept_cols'] = np.array(kept_cols, np.int64)
        ekgwy__uugre = True
    else:
        ekgwy__uugre = False
    oeth__jqed = {i: c for i, c in enumerate(xed__zjwy)}
    lzh__vsypi = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    lzh__vsypi += f'  T2 = init_table(out_table_typ, False)\n'
    lzh__vsypi += f'  T2 = set_table_len(T2, len(T))\n'
    if ekgwy__uugre and len(agkb__rbm) == 0:
        lzh__vsypi += f'  return T2\n'
        idldz__xnkt = {}
        exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
        return idldz__xnkt['table_subset']
    if ekgwy__uugre:
        lzh__vsypi += f'  kept_cols_set = set(kept_cols)\n'
    for typ, bira__dcdt in doro__gda.type_to_blk.items():
        uypcw__vlf = T.type_to_blk[typ]
        lzh__vsypi += (
            f'  arr_list_{bira__dcdt} = get_table_block(T, {uypcw__vlf})\n')
        lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_{bira__dcdt}, {len(doro__gda.block_to_arr_ind[bira__dcdt])}, False)
"""
        vqhip__uvm = True
        if ekgwy__uugre:
            wfe__gqgy = set(doro__gda.block_to_arr_ind[bira__dcdt])
            dooq__lpxcz = wfe__gqgy & agkb__rbm
            vqhip__uvm = len(dooq__lpxcz) > 0
        if vqhip__uvm:
            ysvm__mgzl[f'out_arr_inds_{bira__dcdt}'] = np.array(doro__gda.
                block_to_arr_ind[bira__dcdt], dtype=np.int64)
            lzh__vsypi += (
                f'  for i in range(len(out_arr_list_{bira__dcdt})):\n')
            lzh__vsypi += (
                f'    out_arr_ind_{bira__dcdt} = out_arr_inds_{bira__dcdt}[i]\n'
                )
            if ekgwy__uugre:
                lzh__vsypi += (
                    f'    if out_arr_ind_{bira__dcdt} not in kept_cols_set: continue\n'
                    )
            kygg__ghh = []
            fxf__plibx = []
            for crts__cqtuw in doro__gda.block_to_arr_ind[bira__dcdt]:
                bvfia__tdpl = oeth__jqed[crts__cqtuw]
                kygg__ghh.append(bvfia__tdpl)
                oorqk__woy = T.block_offsets[bvfia__tdpl]
                fxf__plibx.append(oorqk__woy)
            ysvm__mgzl[f'in_logical_idx_{bira__dcdt}'] = np.array(kygg__ghh,
                dtype=np.int64)
            ysvm__mgzl[f'in_physical_idx_{bira__dcdt}'] = np.array(fxf__plibx,
                dtype=np.int64)
            lzh__vsypi += (
                f'    logical_idx_{bira__dcdt} = in_logical_idx_{bira__dcdt}[i]\n'
                )
            lzh__vsypi += (
                f'    physical_idx_{bira__dcdt} = in_physical_idx_{bira__dcdt}[i]\n'
                )
            lzh__vsypi += f"""    ensure_column_unboxed(T, arr_list_{bira__dcdt}, physical_idx_{bira__dcdt}, logical_idx_{bira__dcdt})
"""
            zzih__oefia = '.copy()' if dzu__lynw else ''
            lzh__vsypi += f"""    out_arr_list_{bira__dcdt}[i] = arr_list_{bira__dcdt}[physical_idx_{bira__dcdt}]{zzih__oefia}
"""
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  return T2\n'
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    akdkz__klgry = args[0]
    if equiv_set.has_shape(akdkz__klgry):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=akdkz__klgry, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (akdkz__klgry)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    akdkz__klgry = args[0]
    if equiv_set.has_shape(akdkz__klgry):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            akdkz__klgry)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    lzh__vsypi = 'def impl(T):\n'
    lzh__vsypi += f'  T2 = init_table(T, True)\n'
    lzh__vsypi += f'  l = len(T)\n'
    ysvm__mgzl = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for bira__dcdt in T.type_to_blk.values():
        ysvm__mgzl[f'arr_inds_{bira__dcdt}'] = np.array(T.block_to_arr_ind[
            bira__dcdt], dtype=np.int64)
        lzh__vsypi += (
            f'  arr_list_{bira__dcdt} = get_table_block(T, {bira__dcdt})\n')
        lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_{bira__dcdt}, len(arr_list_{bira__dcdt}), True)
"""
        lzh__vsypi += f'  for i in range(len(arr_list_{bira__dcdt})):\n'
        lzh__vsypi += f'    arr_ind_{bira__dcdt} = arr_inds_{bira__dcdt}[i]\n'
        lzh__vsypi += f"""    ensure_column_unboxed(T, arr_list_{bira__dcdt}, i, arr_ind_{bira__dcdt})
"""
        lzh__vsypi += (
            f'    out_arr_{bira__dcdt} = decode_if_dict_array(arr_list_{bira__dcdt}[i])\n'
            )
        lzh__vsypi += (
            f'    out_arr_list_{bira__dcdt}[i] = out_arr_{bira__dcdt}\n')
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  T2 = set_table_len(T2, l)\n'
    lzh__vsypi += f'  return T2\n'
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['impl']


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
        mlk__mee = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        mlk__mee = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            mlk__mee.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        rhrty__ldxkj, mlix__xmc = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = mlix__xmc
        ibfy__cyh = cgutils.unpack_tuple(builder, rhrty__ldxkj)
        for i, bbs__wxi in enumerate(ibfy__cyh):
            setattr(table, f'block_{i}', bbs__wxi)
            context.nrt.incref(builder, types.List(mlk__mee[i]), bbs__wxi)
        return table._getvalue()
    table_type = TableType(tuple(mlk__mee), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    ysvm__mgzl = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        ysvm__mgzl['kept_cols'] = np.array(list(kept_cols), np.int64)
        ekgwy__uugre = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        ekgwy__uugre = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    ixsj__lzq = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        ixsj__lzq else extra_arrs_t.types[i - ixsj__lzq] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    lzh__vsypi = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    lzh__vsypi += f'  T1 = in_table_t\n'
    lzh__vsypi += f'  T2 = init_table(out_table_type, False)\n'
    lzh__vsypi += f'  T2 = set_table_len(T2, len(T1))\n'
    if ekgwy__uugre and len(kept_cols) == 0:
        lzh__vsypi += f'  return T2\n'
        idldz__xnkt = {}
        exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
        return idldz__xnkt['impl']
    if ekgwy__uugre:
        lzh__vsypi += f'  kept_cols_set = set(kept_cols)\n'
    for typ, bira__dcdt in out_table_type.type_to_blk.items():
        ysvm__mgzl[f'arr_list_typ_{bira__dcdt}'] = types.List(typ)
        scqhx__tqkhb = len(out_table_type.block_to_arr_ind[bira__dcdt])
        lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_typ_{bira__dcdt}, {scqhx__tqkhb}, False)
"""
        if typ in in_table_t.type_to_blk:
            pnnce__xgy = in_table_t.type_to_blk[typ]
            olcnh__amo = []
            fqlbc__kcgtp = []
            for khwiz__hsv in out_table_type.block_to_arr_ind[bira__dcdt]:
                rzn__bnro = in_col_inds[khwiz__hsv]
                if rzn__bnro < ixsj__lzq:
                    olcnh__amo.append(in_table_t.block_offsets[rzn__bnro])
                    fqlbc__kcgtp.append(rzn__bnro)
                else:
                    olcnh__amo.append(-1)
                    fqlbc__kcgtp.append(-1)
            ysvm__mgzl[f'in_idxs_{bira__dcdt}'] = np.array(olcnh__amo, np.int64
                )
            ysvm__mgzl[f'in_arr_inds_{bira__dcdt}'] = np.array(fqlbc__kcgtp,
                np.int64)
            if ekgwy__uugre:
                ysvm__mgzl[f'out_arr_inds_{bira__dcdt}'] = np.array(
                    out_table_type.block_to_arr_ind[bira__dcdt], dtype=np.int64
                    )
            lzh__vsypi += (
                f'  in_arr_list_{bira__dcdt} = get_table_block(T1, {pnnce__xgy})\n'
                )
            lzh__vsypi += (
                f'  for i in range(len(out_arr_list_{bira__dcdt})):\n')
            lzh__vsypi += (
                f'    in_offset_{bira__dcdt} = in_idxs_{bira__dcdt}[i]\n')
            lzh__vsypi += f'    if in_offset_{bira__dcdt} == -1:\n'
            lzh__vsypi += f'      continue\n'
            lzh__vsypi += (
                f'    in_arr_ind_{bira__dcdt} = in_arr_inds_{bira__dcdt}[i]\n')
            if ekgwy__uugre:
                lzh__vsypi += f"""    if out_arr_inds_{bira__dcdt}[i] not in kept_cols_set: continue
"""
            lzh__vsypi += f"""    ensure_column_unboxed(T1, in_arr_list_{bira__dcdt}, in_offset_{bira__dcdt}, in_arr_ind_{bira__dcdt})
"""
            lzh__vsypi += f"""    out_arr_list_{bira__dcdt}[i] = in_arr_list_{bira__dcdt}[in_offset_{bira__dcdt}]
"""
        for i, khwiz__hsv in enumerate(out_table_type.block_to_arr_ind[
            bira__dcdt]):
            if khwiz__hsv not in kept_cols:
                continue
            rzn__bnro = in_col_inds[khwiz__hsv]
            if rzn__bnro >= ixsj__lzq:
                lzh__vsypi += f"""  out_arr_list_{bira__dcdt}[{i}] = extra_arrs_t[{rzn__bnro - ixsj__lzq}]
"""
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  return T2\n'
    ysvm__mgzl.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    ixsj__lzq = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < ixsj__lzq else
        extra_arrs_t.types[i - ixsj__lzq] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    ovqot__gflzd = None
    if not is_overload_none(in_table_t):
        for i, lmymg__jrs in enumerate(in_table_t.types):
            if lmymg__jrs != types.none:
                ovqot__gflzd = f'in_table_t[{i}]'
                break
    if ovqot__gflzd is None:
        for i, lmymg__jrs in enumerate(extra_arrs_t.types):
            if lmymg__jrs != types.none:
                ovqot__gflzd = f'extra_arrs_t[{i}]'
                break
    assert ovqot__gflzd is not None, 'no array found in input data'
    lzh__vsypi = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    lzh__vsypi += f'  T1 = in_table_t\n'
    lzh__vsypi += f'  T2 = init_table(out_table_type, False)\n'
    lzh__vsypi += f'  T2 = set_table_len(T2, len({ovqot__gflzd}))\n'
    ysvm__mgzl = {}
    for typ, bira__dcdt in out_table_type.type_to_blk.items():
        ysvm__mgzl[f'arr_list_typ_{bira__dcdt}'] = types.List(typ)
        scqhx__tqkhb = len(out_table_type.block_to_arr_ind[bira__dcdt])
        lzh__vsypi += f"""  out_arr_list_{bira__dcdt} = alloc_list_like(arr_list_typ_{bira__dcdt}, {scqhx__tqkhb}, False)
"""
        for i, khwiz__hsv in enumerate(out_table_type.block_to_arr_ind[
            bira__dcdt]):
            if khwiz__hsv not in kept_cols:
                continue
            rzn__bnro = in_col_inds[khwiz__hsv]
            if rzn__bnro < ixsj__lzq:
                lzh__vsypi += (
                    f'  out_arr_list_{bira__dcdt}[{i}] = T1[{rzn__bnro}]\n')
            else:
                lzh__vsypi += f"""  out_arr_list_{bira__dcdt}[{i}] = extra_arrs_t[{rzn__bnro - ixsj__lzq}]
"""
        lzh__vsypi += (
            f'  T2 = set_table_block(T2, out_arr_list_{bira__dcdt}, {bira__dcdt})\n'
            )
    lzh__vsypi += f'  return T2\n'
    ysvm__mgzl.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    idldz__xnkt = {}
    exec(lzh__vsypi, ysvm__mgzl, idldz__xnkt)
    return idldz__xnkt['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    xtik__oqbg = args[0]
    zxgun__jhb = args[1]
    if equiv_set.has_shape(xtik__oqbg):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xtik__oqbg)[0], None), pre=[])
    if equiv_set.has_shape(zxgun__jhb):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            zxgun__jhb)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
