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
        trw__xsn = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=trw__xsn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    qmita__rjly = tuple(val.categories.values)
    elem_type = None if len(qmita__rjly) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(qmita__rjly, elem_type, val.ordered, bodo.
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
        zdqd__wkg = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, zdqd__wkg)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    kus__jbn = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    kgy__fyvik = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, dih__eui, dih__eui = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    tesr__twknc = PDCategoricalDtype(kgy__fyvik, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, kus__jbn)
    return tesr__twknc(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    orvw__alho = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, orvw__alho).value
    c.pyapi.decref(orvw__alho)
    icg__ugwhr = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, icg__ugwhr).value
    c.pyapi.decref(icg__ugwhr)
    ehf__juq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=ehf__juq)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    orvw__alho = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    grds__qfze = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    aon__mix = c.context.insert_const_string(c.builder.module, 'pandas')
    oih__cpl = c.pyapi.import_module_noblock(aon__mix)
    rcohx__viq = c.pyapi.call_method(oih__cpl, 'CategoricalDtype', (
        grds__qfze, orvw__alho))
    c.pyapi.decref(orvw__alho)
    c.pyapi.decref(grds__qfze)
    c.pyapi.decref(oih__cpl)
    c.context.nrt.decref(c.builder, typ, val)
    return rcohx__viq


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
        cfux__izhii = get_categories_int_type(fe_type.dtype)
        zdqd__wkg = [('dtype', fe_type.dtype), ('codes', types.Array(
            cfux__izhii, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, zdqd__wkg)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    hofk__zhkq = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), hofk__zhkq
        ).value
    c.pyapi.decref(hofk__zhkq)
    rcohx__viq = c.pyapi.object_getattr_string(val, 'dtype')
    zip__nsp = c.pyapi.to_native_value(typ.dtype, rcohx__viq).value
    c.pyapi.decref(rcohx__viq)
    ibo__tldij = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ibo__tldij.codes = codes
    ibo__tldij.dtype = zip__nsp
    return NativeValue(ibo__tldij._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    bzm__wuc = get_categories_int_type(typ.dtype)
    mztd__khwvt = context.get_constant_generic(builder, types.Array(
        bzm__wuc, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, mztd__khwvt])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    lstr__osyh = len(cat_dtype.categories)
    if lstr__osyh < np.iinfo(np.int8).max:
        dtype = types.int8
    elif lstr__osyh < np.iinfo(np.int16).max:
        dtype = types.int16
    elif lstr__osyh < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    aon__mix = c.context.insert_const_string(c.builder.module, 'pandas')
    oih__cpl = c.pyapi.import_module_noblock(aon__mix)
    cfux__izhii = get_categories_int_type(dtype)
    nkv__inhkm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    fimk__spzcs = types.Array(cfux__izhii, 1, 'C')
    c.context.nrt.incref(c.builder, fimk__spzcs, nkv__inhkm.codes)
    hofk__zhkq = c.pyapi.from_native_value(fimk__spzcs, nkv__inhkm.codes, c
        .env_manager)
    c.context.nrt.incref(c.builder, dtype, nkv__inhkm.dtype)
    rcohx__viq = c.pyapi.from_native_value(dtype, nkv__inhkm.dtype, c.
        env_manager)
    afqmk__khkcf = c.pyapi.borrow_none()
    pqic__gnn = c.pyapi.object_getattr_string(oih__cpl, 'Categorical')
    fzm__ecusx = c.pyapi.call_method(pqic__gnn, 'from_codes', (hofk__zhkq,
        afqmk__khkcf, afqmk__khkcf, rcohx__viq))
    c.pyapi.decref(pqic__gnn)
    c.pyapi.decref(hofk__zhkq)
    c.pyapi.decref(rcohx__viq)
    c.pyapi.decref(oih__cpl)
    c.context.nrt.decref(c.builder, typ, val)
    return fzm__ecusx


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
            iac__hhn = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                drvl__dicp = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), iac__hhn)
                return drvl__dicp
            return impl_lit

        def impl(A, other):
            iac__hhn = get_code_for_value(A.dtype, other)
            drvl__dicp = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), iac__hhn)
            return drvl__dicp
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        kmrzw__qxso = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(kmrzw__qxso)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    nkv__inhkm = cat_dtype.categories
    n = len(nkv__inhkm)
    for bsi__fjaj in range(n):
        if nkv__inhkm[bsi__fjaj] == val:
            return bsi__fjaj
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    gmeo__zgfef = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if gmeo__zgfef != A.dtype.elem_type and gmeo__zgfef != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if gmeo__zgfef == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            drvl__dicp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for bsi__fjaj in numba.parfors.parfor.internal_prange(n):
                hvhg__msni = codes[bsi__fjaj]
                if hvhg__msni == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(drvl__dicp
                            , bsi__fjaj)
                    else:
                        bodo.libs.array_kernels.setna(drvl__dicp, bsi__fjaj)
                    continue
                drvl__dicp[bsi__fjaj] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[hvhg__msni]))
            return drvl__dicp
        return impl
    fimk__spzcs = dtype_to_array_type(gmeo__zgfef)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        drvl__dicp = bodo.utils.utils.alloc_type(n, fimk__spzcs, (-1,))
        for bsi__fjaj in numba.parfors.parfor.internal_prange(n):
            hvhg__msni = codes[bsi__fjaj]
            if hvhg__msni == -1:
                bodo.libs.array_kernels.setna(drvl__dicp, bsi__fjaj)
                continue
            drvl__dicp[bsi__fjaj] = bodo.utils.conversion.unbox_if_timestamp(
                categories[hvhg__msni])
        return drvl__dicp
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        kdjo__ugnmo, zip__nsp = args
        nkv__inhkm = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        nkv__inhkm.codes = kdjo__ugnmo
        nkv__inhkm.dtype = zip__nsp
        context.nrt.incref(builder, signature.args[0], kdjo__ugnmo)
        context.nrt.incref(builder, signature.args[1], zip__nsp)
        return nkv__inhkm._getvalue()
    iboq__dloc = CategoricalArrayType(cat_dtype)
    sig = iboq__dloc(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    nkpwl__ylzam = args[0]
    if equiv_set.has_shape(nkpwl__ylzam):
        return ArrayAnalysis.AnalyzeResult(shape=nkpwl__ylzam, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    cfux__izhii = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, cfux__izhii)
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
            kfb__fwfpk = {}
            mztd__khwvt = np.empty(n + 1, np.int64)
            trc__xvfq = {}
            jfsj__vwcjf = []
            bry__wpcf = {}
            for bsi__fjaj in range(n):
                bry__wpcf[categories[bsi__fjaj]] = bsi__fjaj
            for pwkt__blha in to_replace:
                if pwkt__blha != value:
                    if pwkt__blha in bry__wpcf:
                        if value in bry__wpcf:
                            kfb__fwfpk[pwkt__blha] = pwkt__blha
                            uhxyz__eyl = bry__wpcf[pwkt__blha]
                            trc__xvfq[uhxyz__eyl] = bry__wpcf[value]
                            jfsj__vwcjf.append(uhxyz__eyl)
                        else:
                            kfb__fwfpk[pwkt__blha] = value
                            bry__wpcf[value] = bry__wpcf[pwkt__blha]
            wvh__keyme = np.sort(np.array(jfsj__vwcjf))
            znda__oxv = 0
            syn__cytd = []
            for dvye__sxqh in range(-1, n):
                while znda__oxv < len(wvh__keyme) and dvye__sxqh > wvh__keyme[
                    znda__oxv]:
                    znda__oxv += 1
                syn__cytd.append(znda__oxv)
            for yxsfz__ksqrt in range(-1, n):
                qpkz__ckoz = yxsfz__ksqrt
                if yxsfz__ksqrt in trc__xvfq:
                    qpkz__ckoz = trc__xvfq[yxsfz__ksqrt]
                mztd__khwvt[yxsfz__ksqrt + 1] = qpkz__ckoz - syn__cytd[
                    qpkz__ckoz + 1]
            return kfb__fwfpk, mztd__khwvt, len(wvh__keyme)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for bsi__fjaj in range(len(new_codes_arr)):
        new_codes_arr[bsi__fjaj] = codes_map_arr[old_codes_arr[bsi__fjaj] + 1]


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
    ymao__nbjep = arr.dtype.ordered
    ppjl__rkmba = arr.dtype.elem_type
    lozyv__mvm = get_overload_const(to_replace)
    iqcms__vzz = get_overload_const(value)
    if (arr.dtype.categories is not None and lozyv__mvm is not NOT_CONSTANT and
        iqcms__vzz is not NOT_CONSTANT):
        bxgt__hstr, codes_map_arr, dih__eui = python_build_replace_dicts(
            lozyv__mvm, iqcms__vzz, arr.dtype.categories)
        if len(bxgt__hstr) == 0:
            return lambda arr, to_replace, value: arr.copy()
        wgid__nskms = []
        for xxd__wbiu in arr.dtype.categories:
            if xxd__wbiu in bxgt__hstr:
                gspw__goo = bxgt__hstr[xxd__wbiu]
                if gspw__goo != xxd__wbiu:
                    wgid__nskms.append(gspw__goo)
            else:
                wgid__nskms.append(xxd__wbiu)
        zdm__jcegm = bodo.utils.utils.create_categorical_type(wgid__nskms,
            arr.dtype.data.data, ymao__nbjep)
        rxmqw__kcf = MetaType(tuple(zdm__jcegm))

        def impl_dtype(arr, to_replace, value):
            dkjxz__weo = init_cat_dtype(bodo.utils.conversion.
                index_from_array(zdm__jcegm), ymao__nbjep, None, rxmqw__kcf)
            nkv__inhkm = alloc_categorical_array(len(arr.codes), dkjxz__weo)
            reassign_codes(nkv__inhkm.codes, arr.codes, codes_map_arr)
            return nkv__inhkm
        return impl_dtype
    ppjl__rkmba = arr.dtype.elem_type
    if ppjl__rkmba == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            kfb__fwfpk, codes_map_arr, ppwn__clvum = build_replace_dicts(
                to_replace, value, categories.values)
            if len(kfb__fwfpk) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), ymao__nbjep,
                    None, None))
            n = len(categories)
            zdm__jcegm = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                ppwn__clvum, -1)
            dqgb__bhob = 0
            for dvye__sxqh in range(n):
                uel__bzwnw = categories[dvye__sxqh]
                if uel__bzwnw in kfb__fwfpk:
                    aev__ybnz = kfb__fwfpk[uel__bzwnw]
                    if aev__ybnz != uel__bzwnw:
                        zdm__jcegm[dqgb__bhob] = aev__ybnz
                        dqgb__bhob += 1
                else:
                    zdm__jcegm[dqgb__bhob] = uel__bzwnw
                    dqgb__bhob += 1
            nkv__inhkm = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                zdm__jcegm), ymao__nbjep, None, None))
            reassign_codes(nkv__inhkm.codes, arr.codes, codes_map_arr)
            return nkv__inhkm
        return impl_str
    mvkoq__sjcj = dtype_to_array_type(ppjl__rkmba)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        kfb__fwfpk, codes_map_arr, ppwn__clvum = build_replace_dicts(to_replace
            , value, categories.values)
        if len(kfb__fwfpk) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), ymao__nbjep, None, None))
        n = len(categories)
        zdm__jcegm = bodo.utils.utils.alloc_type(n - ppwn__clvum,
            mvkoq__sjcj, None)
        dqgb__bhob = 0
        for bsi__fjaj in range(n):
            uel__bzwnw = categories[bsi__fjaj]
            if uel__bzwnw in kfb__fwfpk:
                aev__ybnz = kfb__fwfpk[uel__bzwnw]
                if aev__ybnz != uel__bzwnw:
                    zdm__jcegm[dqgb__bhob] = aev__ybnz
                    dqgb__bhob += 1
            else:
                zdm__jcegm[dqgb__bhob] = uel__bzwnw
                dqgb__bhob += 1
        nkv__inhkm = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(zdm__jcegm),
            ymao__nbjep, None, None))
        reassign_codes(nkv__inhkm.codes, arr.codes, codes_map_arr)
        return nkv__inhkm
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
    kfo__givyb = dict()
    iyr__tyge = 0
    for bsi__fjaj in range(len(vals)):
        val = vals[bsi__fjaj]
        if val in kfo__givyb:
            continue
        kfo__givyb[val] = iyr__tyge
        iyr__tyge += 1
    return kfo__givyb


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    kfo__givyb = dict()
    for bsi__fjaj in range(len(vals)):
        val = vals[bsi__fjaj]
        kfo__givyb[val] = bsi__fjaj
    return kfo__givyb


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    dsx__eoeb = dict(fastpath=fastpath)
    oevv__wmnua = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', dsx__eoeb, oevv__wmnua)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        cjke__jaol = get_overload_const(categories)
        if cjke__jaol is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                pxt__oeo = False
            else:
                pxt__oeo = get_overload_const_bool(ordered)
            hnecr__efzsu = pd.CategoricalDtype(pd.array(cjke__jaol), pxt__oeo
                ).categories.array
            kdasa__fdrf = MetaType(tuple(hnecr__efzsu))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                dkjxz__weo = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(hnecr__efzsu), pxt__oeo, None, kdasa__fdrf
                    )
                return bodo.utils.conversion.fix_arr_dtype(data, dkjxz__weo)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            qmita__rjly = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                qmita__rjly, ordered, None, None)
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
            gew__zgfpi = arr.codes[ind]
            return arr.dtype.categories[max(gew__zgfpi, 0)]
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
    for bsi__fjaj in range(len(arr1)):
        if arr1[bsi__fjaj] != arr2[bsi__fjaj]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    vnz__yfogu = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    pnidj__rzk = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    hck__twmh = categorical_arrs_match(arr, val)
    gozr__stxbh = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    elk__ysc = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not vnz__yfogu:
            raise BodoError(gozr__stxbh)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            gew__zgfpi = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = gew__zgfpi
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (vnz__yfogu or pnidj__rzk or hck__twmh !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gozr__stxbh)
        if hck__twmh == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(elk__ysc)
        if vnz__yfogu:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qphi__znj = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for dvye__sxqh in range(n):
                    arr.codes[ind[dvye__sxqh]] = qphi__znj
            return impl_scalar
        if hck__twmh == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for bsi__fjaj in range(n):
                    arr.codes[ind[bsi__fjaj]] = val.codes[bsi__fjaj]
            return impl_arr_ind_mask
        if hck__twmh == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(elk__ysc)
                n = len(val.codes)
                for bsi__fjaj in range(n):
                    arr.codes[ind[bsi__fjaj]] = val.codes[bsi__fjaj]
            return impl_arr_ind_mask
        if pnidj__rzk:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for dvye__sxqh in range(n):
                    svai__ppq = bodo.utils.conversion.unbox_if_timestamp(val
                        [dvye__sxqh])
                    if svai__ppq not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    gew__zgfpi = categories.get_loc(svai__ppq)
                    arr.codes[ind[dvye__sxqh]] = gew__zgfpi
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (vnz__yfogu or pnidj__rzk or hck__twmh !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gozr__stxbh)
        if hck__twmh == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(elk__ysc)
        if vnz__yfogu:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qphi__znj = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for dvye__sxqh in range(n):
                    if ind[dvye__sxqh]:
                        arr.codes[dvye__sxqh] = qphi__znj
            return impl_scalar
        if hck__twmh == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                fsu__qyge = 0
                for bsi__fjaj in range(n):
                    if ind[bsi__fjaj]:
                        arr.codes[bsi__fjaj] = val.codes[fsu__qyge]
                        fsu__qyge += 1
            return impl_bool_ind_mask
        if hck__twmh == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(elk__ysc)
                n = len(ind)
                fsu__qyge = 0
                for bsi__fjaj in range(n):
                    if ind[bsi__fjaj]:
                        arr.codes[bsi__fjaj] = val.codes[fsu__qyge]
                        fsu__qyge += 1
            return impl_bool_ind_mask
        if pnidj__rzk:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                fsu__qyge = 0
                categories = arr.dtype.categories
                for dvye__sxqh in range(n):
                    if ind[dvye__sxqh]:
                        svai__ppq = bodo.utils.conversion.unbox_if_timestamp(
                            val[fsu__qyge])
                        if svai__ppq not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        gew__zgfpi = categories.get_loc(svai__ppq)
                        arr.codes[dvye__sxqh] = gew__zgfpi
                        fsu__qyge += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (vnz__yfogu or pnidj__rzk or hck__twmh !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gozr__stxbh)
        if hck__twmh == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(elk__ysc)
        if vnz__yfogu:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qphi__znj = arr.dtype.categories.get_loc(val)
                lgd__awh = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                for dvye__sxqh in range(lgd__awh.start, lgd__awh.stop,
                    lgd__awh.step):
                    arr.codes[dvye__sxqh] = qphi__znj
            return impl_scalar
        if hck__twmh == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if hck__twmh == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(elk__ysc)
                arr.codes[ind] = val.codes
            return impl_arr
        if pnidj__rzk:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                lgd__awh = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                fsu__qyge = 0
                for dvye__sxqh in range(lgd__awh.start, lgd__awh.stop,
                    lgd__awh.step):
                    svai__ppq = bodo.utils.conversion.unbox_if_timestamp(val
                        [fsu__qyge])
                    if svai__ppq not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    gew__zgfpi = categories.get_loc(svai__ppq)
                    arr.codes[dvye__sxqh] = gew__zgfpi
                    fsu__qyge += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
