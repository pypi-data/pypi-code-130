#
#   Backbone/Head base class
#   Copyright EAVISE
#
import logging
from collections import OrderedDict
import torch.nn as nn

__all__ = ['BaseModule']
log = logging.getLogger(__name__)


class BaseModuleMeta(type):
    def __new__(cls, clsname, bases, clsdict):              # noqa: B902
        obj = super().__new__(cls, clsname, bases, clsdict)
        if clsname == 'BaseModule':
            return obj

        layers = []
        primary = None
        multiple = False
        for name, func in clsdict.items():
            if isinstance(func, LayerDescriptor):
                layers.append(name)

                if primary is None:
                    primary = func
                elif func._primary:
                    if primary.__primary:
                        raise TypeError('There can only be one primary "@BaseModule.layers" function')
                    primary = func
                else:
                    multiple = True

        for base in bases:
            base_layers = getattr(base, '_layers', [])
            layers += base_layers

            base_primary = getattr(base, '_primary', None)
            if base_primary is not None:
                if primary is None:
                    primary = base_primary
                elif not primary._primary:
                    primary = base_primary if base_primary._primary else None

        obj._layers = tuple(layers)
        if len(obj._layers) == 0:
            log.error('"%s" has no "@BaseModule.layers" defined', clsname)

        if not multiple or primary._primary:
            obj._primary = primary
        else:
            obj._primary = None

        return obj


class BaseModule(metaclass=BaseModuleMeta):
    def __new__(cls, *args, **kwargs):
        if cls._primary is not None:
            log.debug(
                'Returning primary layers function: %s.%s',
                cls.__name__,
                cls._primary._name,
            )
            return cls._primary(*args, **kwargs)
        else:
            raise TypeError(
                'There is no primary "@BaseModuler.layers" to choose. Use one of the following methods: %s',
                cls._layers,
            )

    @staticmethod
    def layers(*f, wrapper=nn.Sequential, named=False, primary=False, classmethod=False):
        if len(f) == 0:
            return lambda func: LayerDescriptor(func, named, wrapper, primary, classmethod)
        else:
            return LayerDescriptor(f[0], named, wrapper, primary, classmethod)


class LayerDescriptor:
    def __init__(self, func, named, wrapper, primary, classmethod):
        self._func = func
        self._named = named
        self._wrapper = wrapper
        self._primary = primary
        self.__doc__ = func.__doc__

        self._classmethod = classmethod
        self._cls = None

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, cls=None):
        if self._classmethod:
            self._cls = cls if cls is not None else obj._cls
        return self

    def __call__(self, *args, **kwargs):
        if self._classmethod:
            result = self._func(self._cls, *args, **kwargs)
        else:
            result = self._func(*args, **kwargs)

        if self._named:
            return self._wrapper(OrderedDict(result))
        else:
            return self._wrapper(*result)
