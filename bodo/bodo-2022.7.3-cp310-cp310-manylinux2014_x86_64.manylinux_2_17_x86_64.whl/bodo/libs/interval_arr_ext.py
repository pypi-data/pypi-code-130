"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hwml__poo = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, hwml__poo)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        aylw__gco, qch__cezg = args
        aalp__lio = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        aalp__lio.left = aylw__gco
        aalp__lio.right = qch__cezg
        context.nrt.incref(builder, signature.args[0], aylw__gco)
        context.nrt.incref(builder, signature.args[1], qch__cezg)
        return aalp__lio._getvalue()
    snfmi__ivz = IntervalArrayType(left)
    tlis__vsieh = snfmi__ivz(left, right)
    return tlis__vsieh, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    rnw__cclt = []
    for xlmf__jcjl in args:
        usb__xzffz = equiv_set.get_shape(xlmf__jcjl)
        if usb__xzffz is not None:
            rnw__cclt.append(usb__xzffz[0])
    if len(rnw__cclt) > 1:
        equiv_set.insert_equiv(*rnw__cclt)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    aalp__lio = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, aalp__lio.left)
    iimz__zdu = c.pyapi.from_native_value(typ.arr_type, aalp__lio.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, aalp__lio.right)
    zyqg__find = c.pyapi.from_native_value(typ.arr_type, aalp__lio.right, c
        .env_manager)
    opovm__ajo = c.context.insert_const_string(c.builder.module, 'pandas')
    xfn__uohdp = c.pyapi.import_module_noblock(opovm__ajo)
    qffr__luuc = c.pyapi.object_getattr_string(xfn__uohdp, 'arrays')
    tgtyu__kxdt = c.pyapi.object_getattr_string(qffr__luuc, 'IntervalArray')
    hpr__sgn = c.pyapi.call_method(tgtyu__kxdt, 'from_arrays', (iimz__zdu,
        zyqg__find))
    c.pyapi.decref(iimz__zdu)
    c.pyapi.decref(zyqg__find)
    c.pyapi.decref(xfn__uohdp)
    c.pyapi.decref(qffr__luuc)
    c.pyapi.decref(tgtyu__kxdt)
    c.context.nrt.decref(c.builder, typ, val)
    return hpr__sgn


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    iimz__zdu = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, iimz__zdu).value
    c.pyapi.decref(iimz__zdu)
    zyqg__find = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, zyqg__find).value
    c.pyapi.decref(zyqg__find)
    aalp__lio = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aalp__lio.left = left
    aalp__lio.right = right
    lto__jmiz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(aalp__lio._getvalue(), is_error=lto__jmiz)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
