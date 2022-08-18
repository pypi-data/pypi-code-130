from arch_lint.graph import (
    FullPathModule,
    ImportGraph,
)
from typing import (
    NoReturn,
    Union,
)


def _check_private(
    graph: ImportGraph, parent: FullPathModule, module: FullPathModule
) -> None:
    importers = graph.find_modules_that_directly_import(module)
    is_private = module.name.startswith("_")

    def _valid_importer(importer: FullPathModule) -> bool:
        return importer.module.startswith(parent.module)

    if is_private:
        for i in importers:
            if not _valid_importer(i):
                raise Exception(
                    f"Illegal import of private module {i.module} -> {module.module}"
                )
    for c in graph.find_children(module):
        _check_private(graph, module, c)


def check_private(
    graph: ImportGraph, module: FullPathModule
) -> Union[None, NoReturn]:
    for c in graph.find_children(module):
        _check_private(graph, module, c)
    return None
