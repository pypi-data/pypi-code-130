from .core import (
    DAG,
)
from arch_lint.graph import (
    FullPathModule,
    ImportGraph,
)
from typing import (
    FrozenSet,
    NoReturn,
    Optional,
    Tuple,
    Union,
)


def _chain_exist(
    graph: ImportGraph,
    importer: FrozenSet[FullPathModule],
    imported: FrozenSet[FullPathModule],
) -> Optional[Tuple[FullPathModule, FullPathModule]]:
    for s in importer:
        for t in imported:
            if graph.chain_exists(s, t, True):
                return (s, t)
    return None


def _independence(
    graph: ImportGraph, modules: FrozenSet[FullPathModule]
) -> Optional[Tuple[FullPathModule, FullPathModule]]:
    for m in modules:
        checks = modules - frozenset([m])
        for c in checks:
            if graph.chain_exists(m, c, True):
                return (m, c)
    return None


def _check_independence(
    graph: ImportGraph, modules: FrozenSet[FullPathModule]
) -> Union[None, NoReturn]:
    result = _independence(graph, modules)
    if result:
        raise Exception(
            f"Broken DAG same lvl modules should be independent {result[0].module} -> {result[1].module}"
        )
    return None


def _check_dag_over_modules(
    graph: ImportGraph,
    lower: FrozenSet[FullPathModule],
    upper: FrozenSet[FullPathModule],
) -> Union[None, NoReturn]:
    _chain = _chain_exist(graph, upper, lower)
    if _chain:
        raise Exception(
            f"Broken DAG with illegal import {_chain[0].module} -> {_chain[1].module}"
        )
    return None


def check_dag(
    dag: DAG, graph: ImportGraph, module: FullPathModule
) -> Union[None, NoReturn]:
    _children = graph.find_children(module)
    children = frozenset(s.name for s in _children)
    dag_modules = dag.get_children(module.module)
    missing = children - dag_modules
    if len(_children) > 1 and missing:
        raise Exception(
            f"Missing children modules of `{module.module}` at DAG i.e. {missing}"
        )
    dag_struct = dag.get(module.module)
    if dag_struct:
        for n, c in enumerate(dag_struct):
            current_modules = frozenset(module.new_child(x) for x in c)
            _check_independence(graph, current_modules)
            for upper_modules in dag_struct[n + 1 :]:
                _check_dag_over_modules(
                    graph,
                    current_modules,
                    frozenset(module.new_child(x) for x in upper_modules),
                )
    for child in _children:
        check_dag(dag, graph, child)

    return None
