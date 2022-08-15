import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        ncc__ipzuu = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=ncc__ipzuu)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    ayuca__jad = tuple(val.categories.values)
    elem_type = None if len(ayuca__jad) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(ayuca__jad, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        usrx__ufqmn = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, usrx__ufqmn)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    timq__ujvzh = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    wycy__ena = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, jsh__nbk, jsh__nbk = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    lnb__kkflf = PDCategoricalDtype(wycy__ena, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, timq__ujvzh)
    return lnb__kkflf(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    waio__cjqcl = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, waio__cjqcl).value
    c.pyapi.decref(waio__cjqcl)
    xgn__ncwo = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, xgn__ncwo).value
    c.pyapi.decref(xgn__ncwo)
    qhj__iuh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=qhj__iuh)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    waio__cjqcl = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    ufnb__oemet = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    pdk__rlu = c.context.insert_const_string(c.builder.module, 'pandas')
    xzw__lcljs = c.pyapi.import_module_noblock(pdk__rlu)
    jtg__vwj = c.pyapi.call_method(xzw__lcljs, 'CategoricalDtype', (
        ufnb__oemet, waio__cjqcl))
    c.pyapi.decref(waio__cjqcl)
    c.pyapi.decref(ufnb__oemet)
    c.pyapi.decref(xzw__lcljs)
    c.context.nrt.decref(c.builder, typ, val)
    return jtg__vwj


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mgn__bbvi = get_categories_int_type(fe_type.dtype)
        usrx__ufqmn = [('dtype', fe_type.dtype), ('codes', types.Array(
            mgn__bbvi, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, usrx__ufqmn)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    rbvnv__bnst = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), rbvnv__bnst
        ).value
    c.pyapi.decref(rbvnv__bnst)
    jtg__vwj = c.pyapi.object_getattr_string(val, 'dtype')
    twkq__qjss = c.pyapi.to_native_value(typ.dtype, jtg__vwj).value
    c.pyapi.decref(jtg__vwj)
    pkc__eya = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pkc__eya.codes = codes
    pkc__eya.dtype = twkq__qjss
    return NativeValue(pkc__eya._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    ejmst__uwfh = get_categories_int_type(typ.dtype)
    vjf__bit = context.get_constant_generic(builder, types.Array(
        ejmst__uwfh, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, vjf__bit])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    efac__hrar = len(cat_dtype.categories)
    if efac__hrar < np.iinfo(np.int8).max:
        dtype = types.int8
    elif efac__hrar < np.iinfo(np.int16).max:
        dtype = types.int16
    elif efac__hrar < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    pdk__rlu = c.context.insert_const_string(c.builder.module, 'pandas')
    xzw__lcljs = c.pyapi.import_module_noblock(pdk__rlu)
    mgn__bbvi = get_categories_int_type(dtype)
    jdrpb__bvya = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    uzxn__xbmg = types.Array(mgn__bbvi, 1, 'C')
    c.context.nrt.incref(c.builder, uzxn__xbmg, jdrpb__bvya.codes)
    rbvnv__bnst = c.pyapi.from_native_value(uzxn__xbmg, jdrpb__bvya.codes,
        c.env_manager)
    c.context.nrt.incref(c.builder, dtype, jdrpb__bvya.dtype)
    jtg__vwj = c.pyapi.from_native_value(dtype, jdrpb__bvya.dtype, c.
        env_manager)
    nmpf__neq = c.pyapi.borrow_none()
    bbkev__yodbz = c.pyapi.object_getattr_string(xzw__lcljs, 'Categorical')
    axq__zvee = c.pyapi.call_method(bbkev__yodbz, 'from_codes', (
        rbvnv__bnst, nmpf__neq, nmpf__neq, jtg__vwj))
    c.pyapi.decref(bbkev__yodbz)
    c.pyapi.decref(rbvnv__bnst)
    c.pyapi.decref(jtg__vwj)
    c.pyapi.decref(xzw__lcljs)
    c.context.nrt.decref(c.builder, typ, val)
    return axq__zvee


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            ehyqw__nhd = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                bclv__lck = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), ehyqw__nhd)
                return bclv__lck
            return impl_lit

        def impl(A, other):
            ehyqw__nhd = get_code_for_value(A.dtype, other)
            bclv__lck = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), ehyqw__nhd)
            return bclv__lck
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        bqqmp__ciht = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(bqqmp__ciht)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    jdrpb__bvya = cat_dtype.categories
    n = len(jdrpb__bvya)
    for ycq__cvv in range(n):
        if jdrpb__bvya[ycq__cvv] == val:
            return ycq__cvv
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    ybar__hfvc = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype'
        )
    if ybar__hfvc != A.dtype.elem_type and ybar__hfvc != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if ybar__hfvc == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            bclv__lck = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for ycq__cvv in numba.parfors.parfor.internal_prange(n):
                ptzp__mto = codes[ycq__cvv]
                if ptzp__mto == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(bclv__lck,
                            ycq__cvv)
                    else:
                        bodo.libs.array_kernels.setna(bclv__lck, ycq__cvv)
                    continue
                bclv__lck[ycq__cvv] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[ptzp__mto]))
            return bclv__lck
        return impl
    uzxn__xbmg = dtype_to_array_type(ybar__hfvc)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        bclv__lck = bodo.utils.utils.alloc_type(n, uzxn__xbmg, (-1,))
        for ycq__cvv in numba.parfors.parfor.internal_prange(n):
            ptzp__mto = codes[ycq__cvv]
            if ptzp__mto == -1:
                bodo.libs.array_kernels.setna(bclv__lck, ycq__cvv)
                continue
            bclv__lck[ycq__cvv] = bodo.utils.conversion.unbox_if_timestamp(
                categories[ptzp__mto])
        return bclv__lck
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        vwtny__ictdy, twkq__qjss = args
        jdrpb__bvya = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        jdrpb__bvya.codes = vwtny__ictdy
        jdrpb__bvya.dtype = twkq__qjss
        context.nrt.incref(builder, signature.args[0], vwtny__ictdy)
        context.nrt.incref(builder, signature.args[1], twkq__qjss)
        return jdrpb__bvya._getvalue()
    zuk__vyvrq = CategoricalArrayType(cat_dtype)
    sig = zuk__vyvrq(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ryxbd__ouz = args[0]
    if equiv_set.has_shape(ryxbd__ouz):
        return ArrayAnalysis.AnalyzeResult(shape=ryxbd__ouz, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    mgn__bbvi = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, mgn__bbvi)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            tuxvr__fjag = {}
            vjf__bit = np.empty(n + 1, np.int64)
            rqtdl__faeqg = {}
            wafj__sndi = []
            dqpi__eieew = {}
            for ycq__cvv in range(n):
                dqpi__eieew[categories[ycq__cvv]] = ycq__cvv
            for brh__wmec in to_replace:
                if brh__wmec != value:
                    if brh__wmec in dqpi__eieew:
                        if value in dqpi__eieew:
                            tuxvr__fjag[brh__wmec] = brh__wmec
                            naoc__lnc = dqpi__eieew[brh__wmec]
                            rqtdl__faeqg[naoc__lnc] = dqpi__eieew[value]
                            wafj__sndi.append(naoc__lnc)
                        else:
                            tuxvr__fjag[brh__wmec] = value
                            dqpi__eieew[value] = dqpi__eieew[brh__wmec]
            wkwf__oke = np.sort(np.array(wafj__sndi))
            pbv__rjv = 0
            xvmav__gqod = []
            for irbg__ukid in range(-1, n):
                while pbv__rjv < len(wkwf__oke) and irbg__ukid > wkwf__oke[
                    pbv__rjv]:
                    pbv__rjv += 1
                xvmav__gqod.append(pbv__rjv)
            for zagxo__fybqj in range(-1, n):
                gfkq__xpsc = zagxo__fybqj
                if zagxo__fybqj in rqtdl__faeqg:
                    gfkq__xpsc = rqtdl__faeqg[zagxo__fybqj]
                vjf__bit[zagxo__fybqj + 1] = gfkq__xpsc - xvmav__gqod[
                    gfkq__xpsc + 1]
            return tuxvr__fjag, vjf__bit, len(wkwf__oke)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for ycq__cvv in range(len(new_codes_arr)):
        new_codes_arr[ycq__cvv] = codes_map_arr[old_codes_arr[ycq__cvv] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_replace,
        'CategoricalArray.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'CategoricalArray.replace()')
    kvke__btimd = arr.dtype.ordered
    ndyw__ngzw = arr.dtype.elem_type
    wcs__ualkq = get_overload_const(to_replace)
    zthr__mmqn = get_overload_const(value)
    if (arr.dtype.categories is not None and wcs__ualkq is not NOT_CONSTANT and
        zthr__mmqn is not NOT_CONSTANT):
        twnoh__agysp, codes_map_arr, jsh__nbk = python_build_replace_dicts(
            wcs__ualkq, zthr__mmqn, arr.dtype.categories)
        if len(twnoh__agysp) == 0:
            return lambda arr, to_replace, value: arr.copy()
        vssgh__ekijb = []
        for rbs__xvlmj in arr.dtype.categories:
            if rbs__xvlmj in twnoh__agysp:
                lgup__okfh = twnoh__agysp[rbs__xvlmj]
                if lgup__okfh != rbs__xvlmj:
                    vssgh__ekijb.append(lgup__okfh)
            else:
                vssgh__ekijb.append(rbs__xvlmj)
        pnj__cnmx = bodo.utils.utils.create_categorical_type(vssgh__ekijb,
            arr.dtype.data.data, kvke__btimd)
        gudlk__oveb = MetaType(tuple(pnj__cnmx))

        def impl_dtype(arr, to_replace, value):
            umris__lmlkj = init_cat_dtype(bodo.utils.conversion.
                index_from_array(pnj__cnmx), kvke__btimd, None, gudlk__oveb)
            jdrpb__bvya = alloc_categorical_array(len(arr.codes), umris__lmlkj)
            reassign_codes(jdrpb__bvya.codes, arr.codes, codes_map_arr)
            return jdrpb__bvya
        return impl_dtype
    ndyw__ngzw = arr.dtype.elem_type
    if ndyw__ngzw == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            tuxvr__fjag, codes_map_arr, dxdv__hujv = build_replace_dicts(
                to_replace, value, categories.values)
            if len(tuxvr__fjag) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), kvke__btimd,
                    None, None))
            n = len(categories)
            pnj__cnmx = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                dxdv__hujv, -1)
            upokx__proqc = 0
            for irbg__ukid in range(n):
                ugn__gfpx = categories[irbg__ukid]
                if ugn__gfpx in tuxvr__fjag:
                    osihe__fpw = tuxvr__fjag[ugn__gfpx]
                    if osihe__fpw != ugn__gfpx:
                        pnj__cnmx[upokx__proqc] = osihe__fpw
                        upokx__proqc += 1
                else:
                    pnj__cnmx[upokx__proqc] = ugn__gfpx
                    upokx__proqc += 1
            jdrpb__bvya = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                pnj__cnmx), kvke__btimd, None, None))
            reassign_codes(jdrpb__bvya.codes, arr.codes, codes_map_arr)
            return jdrpb__bvya
        return impl_str
    ahwer__udkre = dtype_to_array_type(ndyw__ngzw)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        tuxvr__fjag, codes_map_arr, dxdv__hujv = build_replace_dicts(to_replace
            , value, categories.values)
        if len(tuxvr__fjag) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), kvke__btimd, None, None))
        n = len(categories)
        pnj__cnmx = bodo.utils.utils.alloc_type(n - dxdv__hujv,
            ahwer__udkre, None)
        upokx__proqc = 0
        for ycq__cvv in range(n):
            ugn__gfpx = categories[ycq__cvv]
            if ugn__gfpx in tuxvr__fjag:
                osihe__fpw = tuxvr__fjag[ugn__gfpx]
                if osihe__fpw != ugn__gfpx:
                    pnj__cnmx[upokx__proqc] = osihe__fpw
                    upokx__proqc += 1
            else:
                pnj__cnmx[upokx__proqc] = ugn__gfpx
                upokx__proqc += 1
        jdrpb__bvya = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(pnj__cnmx
            ), kvke__btimd, None, None))
        reassign_codes(jdrpb__bvya.codes, arr.codes, codes_map_arr)
        return jdrpb__bvya
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    gumn__fxoki = dict()
    rztvz__gqzwt = 0
    for ycq__cvv in range(len(vals)):
        val = vals[ycq__cvv]
        if val in gumn__fxoki:
            continue
        gumn__fxoki[val] = rztvz__gqzwt
        rztvz__gqzwt += 1
    return gumn__fxoki


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    gumn__fxoki = dict()
    for ycq__cvv in range(len(vals)):
        val = vals[ycq__cvv]
        gumn__fxoki[val] = ycq__cvv
    return gumn__fxoki


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    sbgzn__gzigf = dict(fastpath=fastpath)
    bzcl__cjvq = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', sbgzn__gzigf, bzcl__cjvq)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        vkozn__ueush = get_overload_const(categories)
        if vkozn__ueush is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                gkj__llq = False
            else:
                gkj__llq = get_overload_const_bool(ordered)
            fze__vuctt = pd.CategoricalDtype(pd.array(vkozn__ueush), gkj__llq
                ).categories.array
            ptgfe__edhnz = MetaType(tuple(fze__vuctt))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                umris__lmlkj = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(fze__vuctt), gkj__llq, None, ptgfe__edhnz)
                return bodo.utils.conversion.fix_arr_dtype(data, umris__lmlkj)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            ayuca__jad = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                ayuca__jad, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            kpuvb__xgy = arr.codes[ind]
            return arr.dtype.categories[max(kpuvb__xgy, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for ycq__cvv in range(len(arr1)):
        if arr1[ycq__cvv] != arr2[ycq__cvv]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    cdssp__qjmxj = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    vdj__stzk = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    thwb__lfxod = categorical_arrs_match(arr, val)
    sqy__gkdz = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    klrqk__zsb = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not cdssp__qjmxj:
            raise BodoError(sqy__gkdz)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            kpuvb__xgy = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = kpuvb__xgy
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (cdssp__qjmxj or vdj__stzk or thwb__lfxod !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(sqy__gkdz)
        if thwb__lfxod == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(klrqk__zsb)
        if cdssp__qjmxj:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                nbrq__rymig = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for irbg__ukid in range(n):
                    arr.codes[ind[irbg__ukid]] = nbrq__rymig
            return impl_scalar
        if thwb__lfxod == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for ycq__cvv in range(n):
                    arr.codes[ind[ycq__cvv]] = val.codes[ycq__cvv]
            return impl_arr_ind_mask
        if thwb__lfxod == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(klrqk__zsb)
                n = len(val.codes)
                for ycq__cvv in range(n):
                    arr.codes[ind[ycq__cvv]] = val.codes[ycq__cvv]
            return impl_arr_ind_mask
        if vdj__stzk:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for irbg__ukid in range(n):
                    jqy__rpze = bodo.utils.conversion.unbox_if_timestamp(val
                        [irbg__ukid])
                    if jqy__rpze not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kpuvb__xgy = categories.get_loc(jqy__rpze)
                    arr.codes[ind[irbg__ukid]] = kpuvb__xgy
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (cdssp__qjmxj or vdj__stzk or thwb__lfxod !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(sqy__gkdz)
        if thwb__lfxod == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(klrqk__zsb)
        if cdssp__qjmxj:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                nbrq__rymig = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for irbg__ukid in range(n):
                    if ind[irbg__ukid]:
                        arr.codes[irbg__ukid] = nbrq__rymig
            return impl_scalar
        if thwb__lfxod == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                dsvy__apk = 0
                for ycq__cvv in range(n):
                    if ind[ycq__cvv]:
                        arr.codes[ycq__cvv] = val.codes[dsvy__apk]
                        dsvy__apk += 1
            return impl_bool_ind_mask
        if thwb__lfxod == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(klrqk__zsb)
                n = len(ind)
                dsvy__apk = 0
                for ycq__cvv in range(n):
                    if ind[ycq__cvv]:
                        arr.codes[ycq__cvv] = val.codes[dsvy__apk]
                        dsvy__apk += 1
            return impl_bool_ind_mask
        if vdj__stzk:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                dsvy__apk = 0
                categories = arr.dtype.categories
                for irbg__ukid in range(n):
                    if ind[irbg__ukid]:
                        jqy__rpze = bodo.utils.conversion.unbox_if_timestamp(
                            val[dsvy__apk])
                        if jqy__rpze not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        kpuvb__xgy = categories.get_loc(jqy__rpze)
                        arr.codes[irbg__ukid] = kpuvb__xgy
                        dsvy__apk += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (cdssp__qjmxj or vdj__stzk or thwb__lfxod !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(sqy__gkdz)
        if thwb__lfxod == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(klrqk__zsb)
        if cdssp__qjmxj:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                nbrq__rymig = arr.dtype.categories.get_loc(val)
                atg__gdb = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                for irbg__ukid in range(atg__gdb.start, atg__gdb.stop,
                    atg__gdb.step):
                    arr.codes[irbg__ukid] = nbrq__rymig
            return impl_scalar
        if thwb__lfxod == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if thwb__lfxod == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(klrqk__zsb)
                arr.codes[ind] = val.codes
            return impl_arr
        if vdj__stzk:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                atg__gdb = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                dsvy__apk = 0
                for irbg__ukid in range(atg__gdb.start, atg__gdb.stop,
                    atg__gdb.step):
                    jqy__rpze = bodo.utils.conversion.unbox_if_timestamp(val
                        [dsvy__apk])
                    if jqy__rpze not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kpuvb__xgy = categories.get_loc(jqy__rpze)
                    arr.codes[irbg__ukid] = kpuvb__xgy
                    dsvy__apk += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
