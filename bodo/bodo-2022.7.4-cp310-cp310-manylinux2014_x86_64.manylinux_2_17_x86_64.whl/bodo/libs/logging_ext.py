"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    orqvg__nqu = context.get_python_api(builder)
    return orqvg__nqu.unserialize(orqvg__nqu.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        jgrh__gtkrl = ', '.join('e{}'.format(vicua__kdsmr) for vicua__kdsmr in
            range(len(args)))
        if jgrh__gtkrl:
            jgrh__gtkrl += ', '
        xka__nqrir = ', '.join("{} = ''".format(bfz__vwh) for bfz__vwh in
            kws.keys())
        argqg__pqhay = (
            f'def format_stub(string, {jgrh__gtkrl} {xka__nqrir}):\n')
        argqg__pqhay += '    pass\n'
        xph__yjopx = {}
        exec(argqg__pqhay, {}, xph__yjopx)
        kscwi__pbu = xph__yjopx['format_stub']
        heyv__fnf = numba.core.utils.pysignature(kscwi__pbu)
        hntd__miptp = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, hntd__miptp).replace(pysig=heyv__fnf)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for yhyv__qsth in ('logging.Logger', 'logging.RootLogger'):
        for rrjw__rqhgn in func_names:
            btk__zbfe = f'@bound_function("{yhyv__qsth}.{rrjw__rqhgn}")\n'
            btk__zbfe += (
                f'def resolve_{rrjw__rqhgn}(self, logger_typ, args, kws):\n')
            btk__zbfe += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(btk__zbfe)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for dcktf__nxwzt in logging_logger_unsupported_attrs:
        qjs__rxu = 'logging.Logger.' + dcktf__nxwzt
        overload_attribute(LoggingLoggerType, dcktf__nxwzt)(
            create_unsupported_overload(qjs__rxu))
    for awtm__lnj in logging_logger_unsupported_methods:
        qjs__rxu = 'logging.Logger.' + awtm__lnj
        overload_method(LoggingLoggerType, awtm__lnj)(
            create_unsupported_overload(qjs__rxu))


_install_logging_logger_unsupported_objects()
