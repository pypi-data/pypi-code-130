"""
        COPYRIGHT (c) 2022 by Featuremine Corporation.
        This software has been provided pursuant to a License Agreement
        containing restrictions on its use.  This software contains
        valuable trade secrets and proprietary information of
        Featuremine Corporation and is protected by law.  It may not be
        copied or distributed in any form or medium, disclosed to third
        parties, reverse engineered or used in any manner not provided
        for in said License Agreement except with the prior written
        authorization from Featuremine Corporation.
"""

from collections import defaultdict
import yamal.sys_base as base
from typing import Optional, Callable, Any, List


class keydefaultdict(dict):
    def __init__(self, default_factory : Callable[[Any], Any]) -> None:
        self.default_factory = default_factory
        super().__init__()

    def __missing__(self, key : Any) -> Any:
        ret = self[key] = self.default_factory(key)
        return ret


class Sys(base.sys):
    @property
    def path(self) -> List[str]:
        return self.get_paths()

    @path.setter
    def path(self, value : List[str]) -> None:
        self.set_paths(value)


sys = Sys()

class Reactor(base.reactor):
    def run(self, live : bool) -> None:
        super().run(live=live)

    def run_once(self, now : int) -> int:
        return super().run_once(now=now)

    def stop(self) -> None:
        super().stop()

    def sched(self) -> int:
        return super().sched()

class Components:
    def __init__(self, modulename : str, module : object) -> None:
        def load_component(name : str) -> type:
            typename = f'yamal.modules.{modulename}.{name}'

            component_type = sys.get_component_type(module=module, name=name)

            arg_list = sys.get_component_type_spec(component_type=component_type)

            arg_names = ', '.join(map(lambda x: x[0], arg_list))
            arg_dict = '{' + ','.join(map(lambda x: f'"{x[0]}": {x[0]}', arg_list)) + '}'

            def _pre_init(cls : Any, reactor: Reactor, cfg : dict) -> None:
                for key, argtype, req in arg_list:
                    if key in cfg and cfg[key] is None and argtype != 'NoneType':
                        del cfg[key]
                base.component.__init__(cls, reactor=reactor, component_type=component_type, config=cfg)

            __init__ = eval(f'lambda cls, *args, **kwargs: _pre_init(cls, reactor=args[0], cfg=kwargs)', {
                '_pre_init': _pre_init
            })
            __init__.__name__ = '__init__'
            __init__.__doc__ = f'Initializes an instance of {typename}({arg_names})'
            __init__.__annotations__ = {}

            for key, argtype, req in arg_list:
                __init__.__annotations__[key] = eval(argtype if req else f'Optional[{argtype}]', {
                    'NoneType': type(None), 'Optional': Optional
                })
            __init__.__defaults__ = tuple(None for _ in arg_list)

            def __new__(cls : Any, *args : Any, **kwargs : Any) -> Any:
                return base.component.__new__(cls, *args, **kwargs)

            __new__.__annotations__ = __init__.__annotations__

            #__new__.__defaults__ = __init__.__defaults__
            setattr(__new__, '__defaults__', __init__.__defaults__)

            class_namespace = {
                '__doc__': f'{typename} class',
                '__new__': __new__,
                '__init__': __init__,
            }

            return type(typename, (base.component,), class_namespace)

        self._components = keydefaultdict(load_component)

    def __getattr__(self, name : str) -> Any:
        return self._components[name]


class Modules:
    def __init__(self) -> None:
        self._modules = keydefaultdict(lambda name: Components(name, sys.get_module(name=name)))

    def __getattr__(self, name : str) -> Any:
        return self._modules[name]


modules = Modules()
