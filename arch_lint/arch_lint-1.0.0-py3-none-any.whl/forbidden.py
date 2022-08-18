from arch_lint.graph import (
    FullPathModule,
    ImportGraph,
)
from typing import (
    Dict,
    FrozenSet,
    NoReturn,
    Union,
)


def unauthorized_imports(
    forbidden: FullPathModule,
    allowlist: FrozenSet[FullPathModule],
    graph: ImportGraph,
) -> FrozenSet[FullPathModule]:
    return graph.find_modules_that_directly_import(forbidden) - allowlist


def check_forbidden(
    forbidden_allow_list: Dict[FullPathModule, FrozenSet[FullPathModule]],
    graph: ImportGraph,
) -> Union[None, NoReturn]:
    for forbidden, allowlist in forbidden_allow_list.items():
        illegal = unauthorized_imports(forbidden, allowlist, graph)
        if illegal:
            _illegal = frozenset(i.module for i in illegal)
            raise Exception(
                f"Forbidden module `{forbidden.module}` imported by unauthorized modules i.e. {_illegal}"
            )
    return None
