from __future__ import annotations

import importlib
import inspect
from typing import Callable

from cmdtools.callback import Callback
from cmdtools.ext.command import Command, Container, GroupWrapper


class ModuleLoader(Container):
    """A command module loader class.

    Parameters
    ----------
    filename : str
        The command module file to load.
    load_classes : bool
        Loads command classes in the module if true,
        if false just load the whole file as a command module.

    Raises
    ------
    NameError
        If not loading command classes, and callback is not set.
    """

    def __init__(self, filename: str, *, load_classes: bool = True):
        self.filename = filename
        super().__init__()

        module = importlib.import_module(filename)

        if load_classes:
            for obj in dir(module):
                obj = getattr(module, obj, None)

                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    if Command in inspect.getmro(obj):
                        self.commands.append(obj())
        else:
            modname = module.__name__.split(".")[-1]
            wrapper = GroupWrapper(modname, getattr(module, "__aliases__", None))
            callfunc: Callable = getattr(module, modname, None)

            if callfunc:
                wrapper._callback = Callback(callfunc)
            else:
                raise NameError("Could not load callback")

            self.commands.append(wrapper)
