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
    fsax__ubh = context.get_python_api(builder)
    return fsax__ubh.unserialize(fsax__ubh.serialize_object(pyval))


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
        rcak__ihev = ', '.join('e{}'.format(vldju__xrhsq) for vldju__xrhsq in
            range(len(args)))
        if rcak__ihev:
            rcak__ihev += ', '
        yvho__auut = ', '.join("{} = ''".format(mtf__tba) for mtf__tba in
            kws.keys())
        mzmv__flgbv = f'def format_stub(string, {rcak__ihev} {yvho__auut}):\n'
        mzmv__flgbv += '    pass\n'
        rilj__sxzug = {}
        exec(mzmv__flgbv, {}, rilj__sxzug)
        sars__aapqj = rilj__sxzug['format_stub']
        qcto__eaaj = numba.core.utils.pysignature(sars__aapqj)
        iker__nvy = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, iker__nvy).replace(pysig=qcto__eaaj)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for wwnbk__kvgj in ('logging.Logger', 'logging.RootLogger'):
        for dysea__vyxb in func_names:
            upu__lzt = f'@bound_function("{wwnbk__kvgj}.{dysea__vyxb}")\n'
            upu__lzt += (
                f'def resolve_{dysea__vyxb}(self, logger_typ, args, kws):\n')
            upu__lzt += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(upu__lzt)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for wkb__evvj in logging_logger_unsupported_attrs:
        cafh__ezbic = 'logging.Logger.' + wkb__evvj
        overload_attribute(LoggingLoggerType, wkb__evvj)(
            create_unsupported_overload(cafh__ezbic))
    for lcrsa__ulm in logging_logger_unsupported_methods:
        cafh__ezbic = 'logging.Logger.' + lcrsa__ulm
        overload_method(LoggingLoggerType, lcrsa__ulm)(
            create_unsupported_overload(cafh__ezbic))


_install_logging_logger_unsupported_objects()
