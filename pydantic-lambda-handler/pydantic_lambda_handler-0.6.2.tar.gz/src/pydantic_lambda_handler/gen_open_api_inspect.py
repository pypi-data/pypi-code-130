import os
from ast import Import, ImportFrom, parse, walk
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers
from pathlib import Path
from sys import modules
from typing import Optional

from pydantic_lambda_handler.hooks.open_api_gen_hook import APIGenerationHook
from pydantic_lambda_handler.main import PydanticLambdaHandler


def get_top_imported_names(file: str) -> set[str]:
    """Collect names imported in given file.

    We only collect top-level names, i.e. `from foo.bar import baz`
    will only add `foo` to the list.
    """
    if not file.endswith(".pyi"):
        return set()
    with open(os.path.join(file), "rb") as f:
        content = f.read()
    parsed = parse(content)
    top_imported = set()
    for node in walk(parsed):
        if isinstance(node, Import):
            for name in node.names:
                top_imported.add(name.name.split(".")[0])
        elif isinstance(node, ImportFrom):
            if node.level > 0:
                # Relative imports always refer to the current package.
                continue
            assert node.module
            top_imported.add(node.module.split(".")[0])
    return top_imported


def gen_open_api_inspect(dir_path: Path):
    files = dir_path.rglob("*.py")

    PydanticLambdaHandler.add_hook(APIGenerationHook)

    app: Optional[PydanticLambdaHandler] = None

    for file in files:
        module_name = ".".join(str(file.relative_to(dir_path)).removesuffix(".py").split("/"))
        spec = spec_from_file_location(module_name, file)
        if not spec or not spec.loader:
            continue
        module = module_from_spec(spec)
        modules[module_name] = module
        spec.loader.exec_module(module)
        results = getmembers(module)

        for i in range(len(results)):
            if isinstance(results[i][1], PydanticLambdaHandler):
                app = deepcopy(results[i][1])

    if app:
        return (
            next(h for h in app._hooks if issubclass(h, APIGenerationHook)).generate(),  # type: ignore
            app.cdk_stuff,
            app.testing_stuff,
        )
    raise ValueError("App not found")
