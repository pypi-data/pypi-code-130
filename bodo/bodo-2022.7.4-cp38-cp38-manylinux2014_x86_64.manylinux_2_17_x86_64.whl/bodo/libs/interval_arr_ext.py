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
        kyi__psl = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, kyi__psl)


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
        uxlo__xgl, xjfkp__wihv = args
        mcn__nwk = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        mcn__nwk.left = uxlo__xgl
        mcn__nwk.right = xjfkp__wihv
        context.nrt.incref(builder, signature.args[0], uxlo__xgl)
        context.nrt.incref(builder, signature.args[1], xjfkp__wihv)
        return mcn__nwk._getvalue()
    ujpy__bdui = IntervalArrayType(left)
    nvala__izhtb = ujpy__bdui(left, right)
    return nvala__izhtb, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    xrkm__ouem = []
    for xpm__qgtv in args:
        kwtwv__wqcbp = equiv_set.get_shape(xpm__qgtv)
        if kwtwv__wqcbp is not None:
            xrkm__ouem.append(kwtwv__wqcbp[0])
    if len(xrkm__ouem) > 1:
        equiv_set.insert_equiv(*xrkm__ouem)
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
    mcn__nwk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, mcn__nwk.left)
    nigb__keyv = c.pyapi.from_native_value(typ.arr_type, mcn__nwk.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, mcn__nwk.right)
    asxe__koei = c.pyapi.from_native_value(typ.arr_type, mcn__nwk.right, c.
        env_manager)
    wbz__ljm = c.context.insert_const_string(c.builder.module, 'pandas')
    lpao__pqwsp = c.pyapi.import_module_noblock(wbz__ljm)
    yhja__eiow = c.pyapi.object_getattr_string(lpao__pqwsp, 'arrays')
    zxi__uhgu = c.pyapi.object_getattr_string(yhja__eiow, 'IntervalArray')
    tkzi__tyjm = c.pyapi.call_method(zxi__uhgu, 'from_arrays', (nigb__keyv,
        asxe__koei))
    c.pyapi.decref(nigb__keyv)
    c.pyapi.decref(asxe__koei)
    c.pyapi.decref(lpao__pqwsp)
    c.pyapi.decref(yhja__eiow)
    c.pyapi.decref(zxi__uhgu)
    c.context.nrt.decref(c.builder, typ, val)
    return tkzi__tyjm


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    nigb__keyv = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, nigb__keyv).value
    c.pyapi.decref(nigb__keyv)
    asxe__koei = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, asxe__koei).value
    c.pyapi.decref(asxe__koei)
    mcn__nwk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mcn__nwk.left = left
    mcn__nwk.right = right
    jofgt__opqrn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mcn__nwk._getvalue(), is_error=jofgt__opqrn)


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
