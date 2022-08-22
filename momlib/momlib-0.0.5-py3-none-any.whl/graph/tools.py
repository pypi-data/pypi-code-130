"""
Provides an assortment of more advanced tools to work with `Graph` and
    `DiGraph` objects.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable

from .header import NegativeWeightError
from .graph import Graph
from .digraph import DiGraph

from ._minheap import (
    build_min_heap as _build_min_heap,
    extract_min as _extract_min,
    decrease_key as _decrease_key,
)

__all__ = ("shortest_paths",)


def shortest_paths(
    graph: Graph | DiGraph,
    source: int,
) -> tuple[list[Fraction | None], list[int | None]]:
    """
    Apply Dijkstra's algorithm to a graph to compute the shortest path
        from a source node to any other node. The first list returned
        will be the minimum distance between the node and the node
        that corresponds to a given index, while the second list
        returned will be the parent node of any node corresponding to a
        given index such that recursively following this path will
        lead to the source node.

    Arguments
    - graph: The graph for which to compute the shortest paths.
    - source: The "starting" node.

    Possible Errors
    - NegativeWeightError: If a negative weight is found.
    """
    # I wrote most of this while delirious with COVID-19, I'm sorry
    # future me (or anyone else)
    distance: list[Fraction | None] = [None] * len(graph)
    previous: list[int | None] = [None] * len(graph)
    node_queue: list[tuple[int, Fraction | None]] = []

    distance[source] = Fraction(0)
    for node in range(len(graph)):
        node_queue.append((node, distance[node]))
    _build_min_heap(node_queue)

    while len(node_queue) > 0:
        parent, _ = _extract_min(node_queue)
        for child_node, child_distance in _outgoing_edges(graph, parent):
            if child_distance < 0:
                raise NegativeWeightError(
                    "cannot compute the shortest path of a graph with "
                    "negative weights"
                )
            parent_distance = distance[parent]
            if parent_distance is None:
                alternate_path = None
            else:
                alternate_path = parent_distance + child_distance
            child_current_path = distance[child_node]
            if alternate_path is not None and (
                (child_current_path is None)
                or (alternate_path < child_current_path)
            ):
                distance[child_node] = alternate_path
                previous[child_node] = parent
                for index, (item, _) in enumerate(node_queue):
                    if item == child_node:
                        _decrease_key(node_queue, index, alternate_path)
    return distance, previous


# PRIVATE/PROTECTED METHODS


def _outgoing_edges(
    graph: Graph | DiGraph,
    source: int,
) -> Iterable[tuple[int, Fraction]]:
    """
    Finds the outgoing edges from a node in either a directed or
        undirected graph.
    """
    if isinstance(graph, Graph):
        return graph.get_neighbors(source)
    else:
        return graph.get_children(source)
