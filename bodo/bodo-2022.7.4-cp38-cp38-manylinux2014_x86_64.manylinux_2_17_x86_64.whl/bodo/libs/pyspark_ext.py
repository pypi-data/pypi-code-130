"""
Support for PySpark APIs in Bodo JIT functions
"""
from collections import namedtuple
import numba
import numba.cpython.tupleobj
import numpy as np
import pyspark
import pyspark.sql.functions as F
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, infer_global, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_overload_constant_list, is_overload_constant_str, is_overload_true
ANON_SENTINEL = 'bodo_field_'


class SparkSessionType(types.Opaque):

    def __init__(self):
        super(SparkSessionType, self).__init__(name='SparkSessionType')


spark_session_type = SparkSessionType()
register_model(SparkSessionType)(models.OpaqueModel)


class SparkSessionBuilderType(types.Opaque):

    def __init__(self):
        super(SparkSessionBuilderType, self).__init__(name=
            'SparkSessionBuilderType')


spark_session_builder_type = SparkSessionBuilderType()
register_model(SparkSessionBuilderType)(models.OpaqueModel)


@intrinsic
def init_session(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_type)
    return spark_session_type(), codegen


@intrinsic
def init_session_builder(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_builder_type)
    return spark_session_builder_type(), codegen


@overload_method(SparkSessionBuilderType, 'appName', no_unliteral=True)
def overload_appName(A, s):
    return lambda A, s: A


@overload_method(SparkSessionBuilderType, 'getOrCreate', inline='always',
    no_unliteral=True)
def overload_getOrCreate(A):
    return lambda A: bodo.libs.pyspark_ext.init_session()


@typeof_impl.register(pyspark.sql.session.SparkSession)
def typeof_session(val, c):
    return spark_session_type


@box(SparkSessionType)
def box_spark_session(typ, val, c):
    yanr__sgmeq = c.context.insert_const_string(c.builder.module, 'pyspark')
    wlx__pnsi = c.pyapi.import_module_noblock(yanr__sgmeq)
    ijjq__wyzkh = c.pyapi.object_getattr_string(wlx__pnsi, 'sql')
    prk__gby = c.pyapi.object_getattr_string(ijjq__wyzkh, 'SparkSession')
    syn__nlelq = c.pyapi.object_getattr_string(prk__gby, 'builder')
    bmmk__mmd = c.pyapi.call_method(syn__nlelq, 'getOrCreate', ())
    c.pyapi.decref(wlx__pnsi)
    c.pyapi.decref(ijjq__wyzkh)
    c.pyapi.decref(prk__gby)
    c.pyapi.decref(syn__nlelq)
    return bmmk__mmd


@unbox(SparkSessionType)
def unbox_spark_session(typ, obj, c):
    return NativeValue(c.context.get_constant_null(spark_session_type))


@lower_constant(SparkSessionType)
def lower_constant_spark_session(context, builder, ty, pyval):
    return context.get_constant_null(spark_session_type)


class RowType(types.BaseNamedTuple):

    def __init__(self, types, fields):
        self.types = tuple(types)
        self.count = len(self.types)
        self.fields = tuple(fields)
        self.instance_class = namedtuple('Row', fields)
        fzb__tcb = 'Row({})'.format(', '.join(f'{ehndl__ver}:{uufl__jpu}' for
            ehndl__ver, uufl__jpu in zip(self.fields, self.types)))
        super(RowType, self).__init__(fzb__tcb)

    @property
    def key(self):
        return self.fields, self.types

    def __getitem__(self, i):
        return self.types[i]

    def __len__(self):
        return len(self.types)

    def __iter__(self):
        return iter(self.types)


@register_model(RowType)
class RowModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdqfv__fxy = [(ehndl__ver, uufl__jpu) for ehndl__ver, uufl__jpu in
            zip(fe_type.fields, fe_type.types)]
        super(RowModel, self).__init__(dmm, fe_type, qdqfv__fxy)


@typeof_impl.register(pyspark.sql.types.Row)
def typeof_row(val, c):
    fields = val.__fields__ if hasattr(val, '__fields__') else tuple(
        f'{ANON_SENTINEL}{i}' for i in range(len(val)))
    return RowType(tuple(numba.typeof(gnh__zbym) for gnh__zbym in val), fields)


@box(RowType)
def box_row(typ, val, c):
    vvqr__vnqdh = c.pyapi.unserialize(c.pyapi.serialize_object(pyspark.sql.
        types.Row))
    if all(ehndl__ver.startswith(ANON_SENTINEL) for ehndl__ver in typ.fields):
        akn__cweum = [c.box(uufl__jpu, c.builder.extract_value(val, i)) for
            i, uufl__jpu in enumerate(typ.types)]
        obbhc__bosfd = c.pyapi.call_function_objargs(vvqr__vnqdh, akn__cweum)
        for obj in akn__cweum:
            c.pyapi.decref(obj)
        c.pyapi.decref(vvqr__vnqdh)
        return obbhc__bosfd
    args = c.pyapi.tuple_pack([])
    akn__cweum = []
    ikf__wcxw = []
    for i, uufl__jpu in enumerate(typ.types):
        ktbw__mznqs = c.builder.extract_value(val, i)
        obj = c.box(uufl__jpu, ktbw__mznqs)
        ikf__wcxw.append((typ.fields[i], obj))
        akn__cweum.append(obj)
    kws = c.pyapi.dict_pack(ikf__wcxw)
    obbhc__bosfd = c.pyapi.call(vvqr__vnqdh, args, kws)
    for obj in akn__cweum:
        c.pyapi.decref(obj)
    c.pyapi.decref(vvqr__vnqdh)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    return obbhc__bosfd


@infer_global(pyspark.sql.types.Row)
class RowConstructor(AbstractTemplate):

    def generic(self, args, kws):
        if args and kws:
            raise BodoError(
                'pyspark.sql.types.Row: Cannot use both args and kwargs to create Row'
                )
        qxmp__ovm = ', '.join(f'arg{i}' for i in range(len(args)))
        hlq__krr = ', '.join(f"{mly__nlvzp} = ''" for mly__nlvzp in kws)
        func_text = f'def row_stub({qxmp__ovm}{hlq__krr}):\n'
        func_text += '    pass\n'
        ubx__sgfsf = {}
        exec(func_text, {}, ubx__sgfsf)
        gifbs__fibrt = ubx__sgfsf['row_stub']
        hcka__ugnpn = numba.core.utils.pysignature(gifbs__fibrt)
        if args:
            trfdi__atpr = RowType(args, tuple(f'{ANON_SENTINEL}{i}' for i in
                range(len(args))))
            return signature(trfdi__atpr, *args).replace(pysig=hcka__ugnpn)
        kws = dict(kws)
        trfdi__atpr = RowType(tuple(kws.values()), tuple(kws.keys()))
        return signature(trfdi__atpr, *kws.values()).replace(pysig=hcka__ugnpn)


lower_builtin(pyspark.sql.types.Row, types.VarArg(types.Any))(numba.cpython
    .tupleobj.namedtuple_constructor)


class SparkDataFrameType(types.Type):

    def __init__(self, df):
        self.df = df
        super(SparkDataFrameType, self).__init__(f'SparkDataFrame({df})')

    @property
    def key(self):
        return self.df

    def copy(self):
        return SparkDataFrameType(self.df)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SparkDataFrameType)
class SparkDataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdqfv__fxy = [('df', fe_type.df)]
        super(SparkDataFrameModel, self).__init__(dmm, fe_type, qdqfv__fxy)


make_attribute_wrapper(SparkDataFrameType, 'df', '_df')


@intrinsic
def init_spark_df(typingctx, df_typ=None):

    def codegen(context, builder, sig, args):
        df, = args
        spark_df = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        spark_df.df = df
        context.nrt.incref(builder, sig.args[0], df)
        return spark_df._getvalue()
    return SparkDataFrameType(df_typ)(df_typ), codegen


@overload_method(SparkSessionType, 'createDataFrame', inline='always',
    no_unliteral=True)
def overload_create_df(sp_session, data, schema=None, samplingRatio=None,
    verifySchema=True):
    check_runtime_cols_unsupported(data, 'spark.createDataFrame()')
    if isinstance(data, DataFrameType):

        def impl_df(sp_session, data, schema=None, samplingRatio=None,
            verifySchema=True):
            data = bodo.scatterv(data, warn_if_dist=False)
            return bodo.libs.pyspark_ext.init_spark_df(data)
        return impl_df
    if not (isinstance(data, types.List) and isinstance(data.dtype, RowType)):
        raise BodoError(
            f"SparkSession.createDataFrame(): 'data' should be a Pandas dataframe or list of Rows, not {data}"
            )
    nzqvv__qadz = data.dtype.fields
    ggxx__fqm = len(data.dtype.types)
    func_text = (
        'def impl(sp_session, data, schema=None, samplingRatio=None, verifySchema=True):\n'
        )
    func_text += f'  n = len(data)\n'
    icsl__nbd = []
    for i, uufl__jpu in enumerate(data.dtype.types):
        vyogv__vtk = dtype_to_array_type(uufl__jpu)
        func_text += (
            f'  A{i} = bodo.utils.utils.alloc_type(n, arr_typ{i}, (-1,))\n')
        icsl__nbd.append(vyogv__vtk)
    func_text += f'  for i in range(n):\n'
    func_text += f'    r = data[i]\n'
    for i in range(ggxx__fqm):
        func_text += (
            f'    A{i}[i] = bodo.utils.conversion.unbox_if_timestamp(r[{i}])\n'
            )
    kbrmm__lxeyf = '({}{})'.format(', '.join(f'A{i}' for i in range(
        ggxx__fqm)), ',' if len(nzqvv__qadz) == 1 else '')
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({kbrmm__lxeyf}, index, __col_name_meta_value_create_df)
"""
    func_text += f'  pdf = bodo.scatterv(pdf)\n'
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    ubx__sgfsf = {}
    hgfh__zphbl = {'bodo': bodo, '__col_name_meta_value_create_df':
        ColNamesMetaType(tuple(nzqvv__qadz))}
    for i in range(ggxx__fqm):
        hgfh__zphbl[f'arr_typ{i}'] = icsl__nbd[i]
    exec(func_text, hgfh__zphbl, ubx__sgfsf)
    impl = ubx__sgfsf['impl']
    return impl


@overload_method(SparkDataFrameType, 'toPandas', inline='always',
    no_unliteral=True)
def overload_to_pandas(spark_df, _is_bodo_dist=False):
    if is_overload_true(_is_bodo_dist):
        return lambda spark_df, _is_bodo_dist=False: spark_df._df

    def impl(spark_df, _is_bodo_dist=False):
        return bodo.gatherv(spark_df._df, warn_if_rep=False)
    return impl


@overload_method(SparkDataFrameType, 'limit', inline='always', no_unliteral
    =True)
def overload_limit(spark_df, num):

    def impl(spark_df, num):
        return bodo.libs.pyspark_ext.init_spark_df(spark_df._df.iloc[:num])
    return impl


def _df_to_rows(df):
    pass


@overload(_df_to_rows)
def overload_df_to_rows(df):
    func_text = 'def impl(df):\n'
    for i in range(len(df.columns)):
        func_text += (
            f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    func_text += '  n = len(df)\n'
    func_text += '  out = []\n'
    func_text += '  for i in range(n):\n'
    toi__siqce = ', '.join(f'{c}=A{i}[i]' for i, c in enumerate(df.columns))
    func_text += f'    out.append(Row({toi__siqce}))\n'
    func_text += '  return out\n'
    ubx__sgfsf = {}
    hgfh__zphbl = {'bodo': bodo, 'Row': pyspark.sql.types.Row}
    exec(func_text, hgfh__zphbl, ubx__sgfsf)
    impl = ubx__sgfsf['impl']
    return impl


@overload_method(SparkDataFrameType, 'collect', inline='always',
    no_unliteral=True)
def overload_collect(spark_df):

    def impl(spark_df):
        data = bodo.gatherv(spark_df._df, warn_if_rep=False)
        return _df_to_rows(data)
    return impl


@overload_method(SparkDataFrameType, 'take', inline='always', no_unliteral=True
    )
def overload_take(spark_df, num):

    def impl(spark_df, num):
        return spark_df.limit(num).collect()
    return impl


@infer_getattr
class SparkDataFrameAttribute(AttributeTemplate):
    key = SparkDataFrameType

    def generic_resolve(self, sdf, attr):
        if attr in sdf.df.columns:
            return ColumnType(ExprType('col', (attr,)))


SparkDataFrameAttribute._no_unliteral = True


@overload_method(SparkDataFrameType, 'select', no_unliteral=True)
def overload_df_select(spark_df, *cols):
    return _gen_df_select(spark_df, cols)


def _gen_df_select(spark_df, cols, avoid_stararg=False):
    df_type = spark_df.df
    if isinstance(cols, tuple) and len(cols) == 1 and isinstance(cols[0], (
        types.StarArgTuple, types.StarArgUniTuple)):
        cols = cols[0]
    if len(cols) == 1 and is_overload_constant_list(cols[0]):
        cols = get_overload_const_list(cols[0])
    func_text = f"def impl(spark_df, {'' if avoid_stararg else '*cols'}):\n"
    func_text += '  df = spark_df._df\n'
    out_col_names = []
    out_data = []
    for col in cols:
        col = get_overload_const_str(col) if is_overload_constant_str(col
            ) else col
        out_col_names.append(_get_col_name(col))
        data, hjnd__fvvj = _gen_col_code(col, df_type)
        func_text += hjnd__fvvj
        out_data.append(data)
    return _gen_init_spark_df(func_text, out_data, out_col_names)


def _gen_init_spark_df(func_text, out_data, out_col_names):
    kbrmm__lxeyf = '({}{})'.format(', '.join(out_data), ',' if len(out_data
        ) == 1 else '')
    qlzbx__cbzbj = '0' if not out_data else f'len({out_data[0]})'
    func_text += f'  n = {qlzbx__cbzbj}\n'
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({kbrmm__lxeyf}, index, __col_name_meta_value_init_spark_df)
"""
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    ubx__sgfsf = {}
    hgfh__zphbl = {'bodo': bodo, 'np': np,
        '__col_name_meta_value_init_spark_df': ColNamesMetaType(tuple(
        out_col_names))}
    exec(func_text, hgfh__zphbl, ubx__sgfsf)
    impl = ubx__sgfsf['impl']
    return impl


@overload_method(SparkDataFrameType, 'show', inline='always', no_unliteral=True
    )
def overload_show(spark_df, n=20, truncate=True, vertical=False):
    twtle__lkh = dict(truncate=truncate, vertical=vertical)
    ionmz__hej = dict(truncate=True, vertical=False)
    check_unsupported_args('SparkDataFrameType.show', twtle__lkh, ionmz__hej)

    def impl(spark_df, n=20, truncate=True, vertical=False):
        print(spark_df._df.head(n))
    return impl


@overload_method(SparkDataFrameType, 'printSchema', inline='always',
    no_unliteral=True)
def overload_print_schema(spark_df):

    def impl(spark_df):
        print(spark_df._df.dtypes)
    return impl


@overload_method(SparkDataFrameType, 'withColumn', inline='always',
    no_unliteral=True)
def overload_with_column(spark_df, colName, col):
    _check_column(col)
    if not is_overload_constant_str(colName):
        raise BodoError(
            f"SparkDataFrame.withColumn(): 'colName' should be a constant string, not {colName}"
            )
    col_name = get_overload_const_str(colName)
    csys__tonf = spark_df.df.columns
    munq__mwft = csys__tonf if col_name in csys__tonf else csys__tonf + (
        col_name,)
    eraz__pyjer, yhdw__ovhd = _gen_col_code(col, spark_df.df)
    out_data = [(eraz__pyjer if c == col_name else
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {csys__tonf.index(c)})'
        ) for c in munq__mwft]
    func_text = 'def impl(spark_df, colName, col):\n'
    func_text += '  df = spark_df._df\n'
    func_text += yhdw__ovhd
    return _gen_init_spark_df(func_text, out_data, munq__mwft)


@overload_method(SparkDataFrameType, 'withColumnRenamed', inline='always',
    no_unliteral=True)
def overload_with_column_renamed(spark_df, existing, new):
    if not (is_overload_constant_str(existing) and is_overload_constant_str
        (new)):
        raise BodoError(
            f"SparkDataFrame.withColumnRenamed(): 'existing' and 'new' should be a constant strings, not ({existing}, {new})"
            )
    csdam__difji = get_overload_const_str(existing)
    xycwv__rlc = get_overload_const_str(new)
    csys__tonf = spark_df.df.columns
    munq__mwft = tuple(xycwv__rlc if c == csdam__difji else c for c in
        csys__tonf)
    out_data = [f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
         for i in range(len(csys__tonf))]
    func_text = 'def impl(spark_df, existing, new):\n'
    func_text += '  df = spark_df._df\n'
    return _gen_init_spark_df(func_text, out_data, munq__mwft)


@overload_attribute(SparkDataFrameType, 'columns', inline='always')
def overload_dataframe_columns(spark_df):
    eaxj__tdqbw = list(str(mly__nlvzp) for mly__nlvzp in spark_df.df.columns)
    func_text = 'def impl(spark_df):\n'
    func_text += f'  return {eaxj__tdqbw}\n'
    ubx__sgfsf = {}
    exec(func_text, {}, ubx__sgfsf)
    impl = ubx__sgfsf['impl']
    return impl


class ColumnType(types.Type):

    def __init__(self, expr):
        self.expr = expr
        super(ColumnType, self).__init__(f'Column({expr})')

    @property
    def key(self):
        return self.expr

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ColumnType)(models.OpaqueModel)


class ExprType(types.Type):

    def __init__(self, op, children):
        self.op = op
        self.children = children
        super(ExprType, self).__init__(f'{op}({children})')

    @property
    def key(self):
        return self.op, self.children

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ExprType)(models.OpaqueModel)


@intrinsic
def init_col_from_name(typingctx, col=None):
    assert is_overload_constant_str(col)
    jgb__qigek = get_overload_const_str(col)
    qth__mmwaf = ColumnType(ExprType('col', (jgb__qigek,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(qth__mmwaf)
    return qth__mmwaf(col), codegen


@overload(F.col, no_unliteral=True)
@overload(F.column, no_unliteral=True)
def overload_f_col(col):
    if not is_overload_constant_str(col):
        raise BodoError(
            f'pyspark.sql.functions.col(): column name should be a constant string, not {col}'
            )
    return lambda col: init_col_from_name(col)


@intrinsic
def init_f_sum(typingctx, col=None):
    qth__mmwaf = ColumnType(ExprType('sum', (col.expr,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(qth__mmwaf)
    return qth__mmwaf(col), codegen


@overload(F.sum, no_unliteral=True)
def overload_f_sum(col):
    if is_overload_constant_str(col):
        return lambda col: init_f_sum(init_col_from_name(col))
    if not isinstance(col, ColumnType):
        raise BodoError(
            f'pyspark.sql.functions.sum(): input should be a Column object or a constant string, not {col}'
            )
    return lambda col: init_f_sum(col)


def _get_col_name(col):
    if isinstance(col, str):
        return col
    _check_column(col)
    return _get_col_name_exr(col.expr)


def _get_col_name_exr(expr):
    if expr.op == 'sum':
        return f'sum({_get_col_name_exr(expr.children[0])})'
    assert expr.op == 'col'
    return expr.children[0]


def _gen_col_code(col, df_type):
    if isinstance(col, str):
        return _gen_col_code_colname(col, df_type)
    _check_column(col)
    return _gen_col_code_expr(col.expr, df_type)


def _gen_col_code_expr(expr, df_type):
    if expr.op == 'col':
        return _gen_col_code_colname(expr.children[0], df_type)
    if expr.op == 'sum':
        ctdh__cmy, avi__tio = _gen_col_code_expr(expr.children[0], df_type)
        i = ir_utils.next_label()
        func_text = f"""  A{i} = np.asarray([bodo.libs.array_ops.array_op_sum({ctdh__cmy}, True, 0)])
"""
        return f'A{i}', avi__tio + func_text


def _gen_col_code_colname(col_name, df_type):
    kuui__qhy = df_type.columns.index(col_name)
    i = ir_utils.next_label()
    func_text = (
        f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {kuui__qhy})\n'
        )
    return f'A{i}', func_text


def _check_column(col):
    if not isinstance(col, ColumnType):
        raise BodoError('Column object expected')
