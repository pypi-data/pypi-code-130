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
    cuorw__dyrg = context.get_python_api(builder)
    return cuorw__dyrg.unserialize(cuorw__dyrg.serialize_object(pyval))


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
        eyxak__jnthr = ', '.join('e{}'.format(ohl__esmej) for ohl__esmej in
            range(len(args)))
        if eyxak__jnthr:
            eyxak__jnthr += ', '
        wpazz__ide = ', '.join("{} = ''".format(mytv__oxz) for mytv__oxz in
            kws.keys())
        qzoo__btel = f'def format_stub(string, {eyxak__jnthr} {wpazz__ide}):\n'
        qzoo__btel += '    pass\n'
        ioiwj__cxll = {}
        exec(qzoo__btel, {}, ioiwj__cxll)
        cmr__rnxe = ioiwj__cxll['format_stub']
        hmpqh__sgbj = numba.core.utils.pysignature(cmr__rnxe)
        gours__nrjr = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, gours__nrjr).replace(pysig=hmpqh__sgbj)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for jfe__bkbnq in ('logging.Logger', 'logging.RootLogger'):
        for gyh__iks in func_names:
            zvzv__bah = f'@bound_function("{jfe__bkbnq}.{gyh__iks}")\n'
            zvzv__bah += (
                f'def resolve_{gyh__iks}(self, logger_typ, args, kws):\n')
            zvzv__bah += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(zvzv__bah)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for ykit__oal in logging_logger_unsupported_attrs:
        gxvp__dyv = 'logging.Logger.' + ykit__oal
        overload_attribute(LoggingLoggerType, ykit__oal)(
            create_unsupported_overload(gxvp__dyv))
    for skvk__stlxc in logging_logger_unsupported_methods:
        gxvp__dyv = 'logging.Logger.' + skvk__stlxc
        overload_method(LoggingLoggerType, skvk__stlxc)(
            create_unsupported_overload(gxvp__dyv))


_install_logging_logger_unsupported_objects()
