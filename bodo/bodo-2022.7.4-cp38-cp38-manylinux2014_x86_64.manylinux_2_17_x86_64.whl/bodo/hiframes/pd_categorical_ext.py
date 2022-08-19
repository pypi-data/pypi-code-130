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
        emvmt__oga = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=emvmt__oga)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    lhr__gwsv = tuple(val.categories.values)
    elem_type = None if len(lhr__gwsv) == 0 else bodo.typeof(val.categories
        .values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(lhr__gwsv, elem_type, val.ordered, bodo.
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
        thl__cdtn = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, thl__cdtn)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    tuz__xqe = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    gpi__zzv = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, dbam__rrun, dbam__rrun = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    fow__jst = PDCategoricalDtype(gpi__zzv, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, tuz__xqe)
    return fow__jst(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zws__iiqol = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, zws__iiqol).value
    c.pyapi.decref(zws__iiqol)
    ojv__anxg = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, ojv__anxg).value
    c.pyapi.decref(ojv__anxg)
    dnd__anwo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=dnd__anwo)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    zws__iiqol = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    veov__cspf = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    nnglf__wfhtz = c.context.insert_const_string(c.builder.module, 'pandas')
    fgme__vwcpe = c.pyapi.import_module_noblock(nnglf__wfhtz)
    zoprj__wjyk = c.pyapi.call_method(fgme__vwcpe, 'CategoricalDtype', (
        veov__cspf, zws__iiqol))
    c.pyapi.decref(zws__iiqol)
    c.pyapi.decref(veov__cspf)
    c.pyapi.decref(fgme__vwcpe)
    c.context.nrt.decref(c.builder, typ, val)
    return zoprj__wjyk


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
        pgta__eirhp = get_categories_int_type(fe_type.dtype)
        thl__cdtn = [('dtype', fe_type.dtype), ('codes', types.Array(
            pgta__eirhp, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, thl__cdtn)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    epr__nhyln = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), epr__nhyln
        ).value
    c.pyapi.decref(epr__nhyln)
    zoprj__wjyk = c.pyapi.object_getattr_string(val, 'dtype')
    voq__vbk = c.pyapi.to_native_value(typ.dtype, zoprj__wjyk).value
    c.pyapi.decref(zoprj__wjyk)
    cpzdi__vgk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cpzdi__vgk.codes = codes
    cpzdi__vgk.dtype = voq__vbk
    return NativeValue(cpzdi__vgk._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    fxn__ncsm = get_categories_int_type(typ.dtype)
    vnf__oapzk = context.get_constant_generic(builder, types.Array(
        fxn__ncsm, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, vnf__oapzk])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    asys__nvt = len(cat_dtype.categories)
    if asys__nvt < np.iinfo(np.int8).max:
        dtype = types.int8
    elif asys__nvt < np.iinfo(np.int16).max:
        dtype = types.int16
    elif asys__nvt < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    nnglf__wfhtz = c.context.insert_const_string(c.builder.module, 'pandas')
    fgme__vwcpe = c.pyapi.import_module_noblock(nnglf__wfhtz)
    pgta__eirhp = get_categories_int_type(dtype)
    jjhwj__batuk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    asto__uja = types.Array(pgta__eirhp, 1, 'C')
    c.context.nrt.incref(c.builder, asto__uja, jjhwj__batuk.codes)
    epr__nhyln = c.pyapi.from_native_value(asto__uja, jjhwj__batuk.codes, c
        .env_manager)
    c.context.nrt.incref(c.builder, dtype, jjhwj__batuk.dtype)
    zoprj__wjyk = c.pyapi.from_native_value(dtype, jjhwj__batuk.dtype, c.
        env_manager)
    vhaoo__mwoi = c.pyapi.borrow_none()
    xhdh__kohga = c.pyapi.object_getattr_string(fgme__vwcpe, 'Categorical')
    odno__ezja = c.pyapi.call_method(xhdh__kohga, 'from_codes', (epr__nhyln,
        vhaoo__mwoi, vhaoo__mwoi, zoprj__wjyk))
    c.pyapi.decref(xhdh__kohga)
    c.pyapi.decref(epr__nhyln)
    c.pyapi.decref(zoprj__wjyk)
    c.pyapi.decref(fgme__vwcpe)
    c.context.nrt.decref(c.builder, typ, val)
    return odno__ezja


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
            syyws__zanmj = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                iccs__abs = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), syyws__zanmj)
                return iccs__abs
            return impl_lit

        def impl(A, other):
            syyws__zanmj = get_code_for_value(A.dtype, other)
            iccs__abs = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), syyws__zanmj)
            return iccs__abs
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        nrna__ljrdr = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(nrna__ljrdr)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    jjhwj__batuk = cat_dtype.categories
    n = len(jjhwj__batuk)
    for zhm__mvxjc in range(n):
        if jjhwj__batuk[zhm__mvxjc] == val:
            return zhm__mvxjc
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    gjk__nsa = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if gjk__nsa != A.dtype.elem_type and gjk__nsa != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if gjk__nsa == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            iccs__abs = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for zhm__mvxjc in numba.parfors.parfor.internal_prange(n):
                tvekz__esff = codes[zhm__mvxjc]
                if tvekz__esff == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(iccs__abs,
                            zhm__mvxjc)
                    else:
                        bodo.libs.array_kernels.setna(iccs__abs, zhm__mvxjc)
                    continue
                iccs__abs[zhm__mvxjc] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[tvekz__esff]))
            return iccs__abs
        return impl
    asto__uja = dtype_to_array_type(gjk__nsa)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        iccs__abs = bodo.utils.utils.alloc_type(n, asto__uja, (-1,))
        for zhm__mvxjc in numba.parfors.parfor.internal_prange(n):
            tvekz__esff = codes[zhm__mvxjc]
            if tvekz__esff == -1:
                bodo.libs.array_kernels.setna(iccs__abs, zhm__mvxjc)
                continue
            iccs__abs[zhm__mvxjc] = bodo.utils.conversion.unbox_if_timestamp(
                categories[tvekz__esff])
        return iccs__abs
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        ddh__hwl, voq__vbk = args
        jjhwj__batuk = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        jjhwj__batuk.codes = ddh__hwl
        jjhwj__batuk.dtype = voq__vbk
        context.nrt.incref(builder, signature.args[0], ddh__hwl)
        context.nrt.incref(builder, signature.args[1], voq__vbk)
        return jjhwj__batuk._getvalue()
    lacgq__fpnej = CategoricalArrayType(cat_dtype)
    sig = lacgq__fpnej(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    avnaz__pjir = args[0]
    if equiv_set.has_shape(avnaz__pjir):
        return ArrayAnalysis.AnalyzeResult(shape=avnaz__pjir, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    pgta__eirhp = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, pgta__eirhp)
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
            wdmoz__wni = {}
            vnf__oapzk = np.empty(n + 1, np.int64)
            hkyr__msi = {}
            ipf__qsu = []
            aoq__wwlh = {}
            for zhm__mvxjc in range(n):
                aoq__wwlh[categories[zhm__mvxjc]] = zhm__mvxjc
            for foodj__elo in to_replace:
                if foodj__elo != value:
                    if foodj__elo in aoq__wwlh:
                        if value in aoq__wwlh:
                            wdmoz__wni[foodj__elo] = foodj__elo
                            ylyk__vvskd = aoq__wwlh[foodj__elo]
                            hkyr__msi[ylyk__vvskd] = aoq__wwlh[value]
                            ipf__qsu.append(ylyk__vvskd)
                        else:
                            wdmoz__wni[foodj__elo] = value
                            aoq__wwlh[value] = aoq__wwlh[foodj__elo]
            kcxcp__katb = np.sort(np.array(ipf__qsu))
            vsynx__xgua = 0
            iica__gkb = []
            for wgoth__wcq in range(-1, n):
                while vsynx__xgua < len(kcxcp__katb
                    ) and wgoth__wcq > kcxcp__katb[vsynx__xgua]:
                    vsynx__xgua += 1
                iica__gkb.append(vsynx__xgua)
            for ionc__ovi in range(-1, n):
                thb__idime = ionc__ovi
                if ionc__ovi in hkyr__msi:
                    thb__idime = hkyr__msi[ionc__ovi]
                vnf__oapzk[ionc__ovi + 1] = thb__idime - iica__gkb[
                    thb__idime + 1]
            return wdmoz__wni, vnf__oapzk, len(kcxcp__katb)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for zhm__mvxjc in range(len(new_codes_arr)):
        new_codes_arr[zhm__mvxjc] = codes_map_arr[old_codes_arr[zhm__mvxjc] + 1
            ]


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
    lxjjp__zbtu = arr.dtype.ordered
    kpdyt__two = arr.dtype.elem_type
    aajyx__zge = get_overload_const(to_replace)
    fdvh__fsh = get_overload_const(value)
    if (arr.dtype.categories is not None and aajyx__zge is not NOT_CONSTANT and
        fdvh__fsh is not NOT_CONSTANT):
        plg__zfcg, codes_map_arr, dbam__rrun = python_build_replace_dicts(
            aajyx__zge, fdvh__fsh, arr.dtype.categories)
        if len(plg__zfcg) == 0:
            return lambda arr, to_replace, value: arr.copy()
        mvy__riro = []
        for gre__lipj in arr.dtype.categories:
            if gre__lipj in plg__zfcg:
                speyb__tvbxv = plg__zfcg[gre__lipj]
                if speyb__tvbxv != gre__lipj:
                    mvy__riro.append(speyb__tvbxv)
            else:
                mvy__riro.append(gre__lipj)
        syhz__jujg = bodo.utils.utils.create_categorical_type(mvy__riro,
            arr.dtype.data.data, lxjjp__zbtu)
        hwyu__hxe = MetaType(tuple(syhz__jujg))

        def impl_dtype(arr, to_replace, value):
            bql__itgnz = init_cat_dtype(bodo.utils.conversion.
                index_from_array(syhz__jujg), lxjjp__zbtu, None, hwyu__hxe)
            jjhwj__batuk = alloc_categorical_array(len(arr.codes), bql__itgnz)
            reassign_codes(jjhwj__batuk.codes, arr.codes, codes_map_arr)
            return jjhwj__batuk
        return impl_dtype
    kpdyt__two = arr.dtype.elem_type
    if kpdyt__two == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            wdmoz__wni, codes_map_arr, vcwia__bida = build_replace_dicts(
                to_replace, value, categories.values)
            if len(wdmoz__wni) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), lxjjp__zbtu,
                    None, None))
            n = len(categories)
            syhz__jujg = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                vcwia__bida, -1)
            lpuo__kctjr = 0
            for wgoth__wcq in range(n):
                xktsv__mre = categories[wgoth__wcq]
                if xktsv__mre in wdmoz__wni:
                    koeup__jmjof = wdmoz__wni[xktsv__mre]
                    if koeup__jmjof != xktsv__mre:
                        syhz__jujg[lpuo__kctjr] = koeup__jmjof
                        lpuo__kctjr += 1
                else:
                    syhz__jujg[lpuo__kctjr] = xktsv__mre
                    lpuo__kctjr += 1
            jjhwj__batuk = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                syhz__jujg), lxjjp__zbtu, None, None))
            reassign_codes(jjhwj__batuk.codes, arr.codes, codes_map_arr)
            return jjhwj__batuk
        return impl_str
    lfv__zlkb = dtype_to_array_type(kpdyt__two)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        wdmoz__wni, codes_map_arr, vcwia__bida = build_replace_dicts(to_replace
            , value, categories.values)
        if len(wdmoz__wni) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), lxjjp__zbtu, None, None))
        n = len(categories)
        syhz__jujg = bodo.utils.utils.alloc_type(n - vcwia__bida, lfv__zlkb,
            None)
        lpuo__kctjr = 0
        for zhm__mvxjc in range(n):
            xktsv__mre = categories[zhm__mvxjc]
            if xktsv__mre in wdmoz__wni:
                koeup__jmjof = wdmoz__wni[xktsv__mre]
                if koeup__jmjof != xktsv__mre:
                    syhz__jujg[lpuo__kctjr] = koeup__jmjof
                    lpuo__kctjr += 1
            else:
                syhz__jujg[lpuo__kctjr] = xktsv__mre
                lpuo__kctjr += 1
        jjhwj__batuk = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            syhz__jujg), lxjjp__zbtu, None, None))
        reassign_codes(jjhwj__batuk.codes, arr.codes, codes_map_arr)
        return jjhwj__batuk
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
    okqf__wiljs = dict()
    iijf__dsz = 0
    for zhm__mvxjc in range(len(vals)):
        val = vals[zhm__mvxjc]
        if val in okqf__wiljs:
            continue
        okqf__wiljs[val] = iijf__dsz
        iijf__dsz += 1
    return okqf__wiljs


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    okqf__wiljs = dict()
    for zhm__mvxjc in range(len(vals)):
        val = vals[zhm__mvxjc]
        okqf__wiljs[val] = zhm__mvxjc
    return okqf__wiljs


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    xzp__hwfyc = dict(fastpath=fastpath)
    pzulk__wkugb = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', xzp__hwfyc, pzulk__wkugb)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        fqa__qtb = get_overload_const(categories)
        if fqa__qtb is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                zpoi__puc = False
            else:
                zpoi__puc = get_overload_const_bool(ordered)
            xdw__afkj = pd.CategoricalDtype(pd.array(fqa__qtb), zpoi__puc
                ).categories.array
            qfrr__yup = MetaType(tuple(xdw__afkj))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                bql__itgnz = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(xdw__afkj), zpoi__puc, None, qfrr__yup)
                return bodo.utils.conversion.fix_arr_dtype(data, bql__itgnz)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            lhr__gwsv = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                lhr__gwsv, ordered, None, None)
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
            jxd__zslwe = arr.codes[ind]
            return arr.dtype.categories[max(jxd__zslwe, 0)]
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
    for zhm__mvxjc in range(len(arr1)):
        if arr1[zhm__mvxjc] != arr2[zhm__mvxjc]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    nfk__wqp = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    gwbo__bre = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    tbyoo__fpcpx = categorical_arrs_match(arr, val)
    gxte__kjv = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    hwgi__qrt = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not nfk__wqp:
            raise BodoError(gxte__kjv)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            jxd__zslwe = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = jxd__zslwe
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (nfk__wqp or gwbo__bre or tbyoo__fpcpx !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gxte__kjv)
        if tbyoo__fpcpx == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hwgi__qrt)
        if nfk__wqp:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                wmaud__kcxa = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wgoth__wcq in range(n):
                    arr.codes[ind[wgoth__wcq]] = wmaud__kcxa
            return impl_scalar
        if tbyoo__fpcpx == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for zhm__mvxjc in range(n):
                    arr.codes[ind[zhm__mvxjc]] = val.codes[zhm__mvxjc]
            return impl_arr_ind_mask
        if tbyoo__fpcpx == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hwgi__qrt)
                n = len(val.codes)
                for zhm__mvxjc in range(n):
                    arr.codes[ind[zhm__mvxjc]] = val.codes[zhm__mvxjc]
            return impl_arr_ind_mask
        if gwbo__bre:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for wgoth__wcq in range(n):
                    upq__nyh = bodo.utils.conversion.unbox_if_timestamp(val
                        [wgoth__wcq])
                    if upq__nyh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    jxd__zslwe = categories.get_loc(upq__nyh)
                    arr.codes[ind[wgoth__wcq]] = jxd__zslwe
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (nfk__wqp or gwbo__bre or tbyoo__fpcpx !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gxte__kjv)
        if tbyoo__fpcpx == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hwgi__qrt)
        if nfk__wqp:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                wmaud__kcxa = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wgoth__wcq in range(n):
                    if ind[wgoth__wcq]:
                        arr.codes[wgoth__wcq] = wmaud__kcxa
            return impl_scalar
        if tbyoo__fpcpx == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                pax__ylyp = 0
                for zhm__mvxjc in range(n):
                    if ind[zhm__mvxjc]:
                        arr.codes[zhm__mvxjc] = val.codes[pax__ylyp]
                        pax__ylyp += 1
            return impl_bool_ind_mask
        if tbyoo__fpcpx == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hwgi__qrt)
                n = len(ind)
                pax__ylyp = 0
                for zhm__mvxjc in range(n):
                    if ind[zhm__mvxjc]:
                        arr.codes[zhm__mvxjc] = val.codes[pax__ylyp]
                        pax__ylyp += 1
            return impl_bool_ind_mask
        if gwbo__bre:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                pax__ylyp = 0
                categories = arr.dtype.categories
                for wgoth__wcq in range(n):
                    if ind[wgoth__wcq]:
                        upq__nyh = bodo.utils.conversion.unbox_if_timestamp(val
                            [pax__ylyp])
                        if upq__nyh not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        jxd__zslwe = categories.get_loc(upq__nyh)
                        arr.codes[wgoth__wcq] = jxd__zslwe
                        pax__ylyp += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (nfk__wqp or gwbo__bre or tbyoo__fpcpx !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gxte__kjv)
        if tbyoo__fpcpx == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hwgi__qrt)
        if nfk__wqp:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                wmaud__kcxa = arr.dtype.categories.get_loc(val)
                ftzn__als = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for wgoth__wcq in range(ftzn__als.start, ftzn__als.stop,
                    ftzn__als.step):
                    arr.codes[wgoth__wcq] = wmaud__kcxa
            return impl_scalar
        if tbyoo__fpcpx == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if tbyoo__fpcpx == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hwgi__qrt)
                arr.codes[ind] = val.codes
            return impl_arr
        if gwbo__bre:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                ftzn__als = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                pax__ylyp = 0
                for wgoth__wcq in range(ftzn__als.start, ftzn__als.stop,
                    ftzn__als.step):
                    upq__nyh = bodo.utils.conversion.unbox_if_timestamp(val
                        [pax__ylyp])
                    if upq__nyh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    jxd__zslwe = categories.get_loc(upq__nyh)
                    arr.codes[wgoth__wcq] = jxd__zslwe
                    pax__ylyp += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
