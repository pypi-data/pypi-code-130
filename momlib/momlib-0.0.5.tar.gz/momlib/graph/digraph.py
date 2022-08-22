"""
Implements the `DiGraph` class (see `help(DiGraph)`).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Optional

from .header import NodeNotFoundError

from ..linalg import Matrix

__all__ = ("DiGraph",)


class DiGraph:
    """
    Expresses the mathematical notion of a directed, optionally
        weighted graph in native Python datastructures and datatypes
        while providing an assortment of tools to perform basic graph
        manipulations.

    `DiGraph` objects are considered mutable, which means they can be
        modified and should not be used as dictionary keys or set items.
    """

    __slots__ = ("_edge_data", "_length")

    def __init__(
        self,
        node_count: int = 0,
        edges: Optional[Iterable[Iterable[float | Fraction | None]]] = None,
    ) -> None:
        """
        Initializes a new instance of the `DiGraph` class.

        Arguments
        - node_count: The number of nodes to initialize the digraph
            with.
        - edges: The edge data to initialize the digraph with - an
            iterable that must produce a matrix such that each entry
            describes a connection between the nodes that correspond to
            its coordinates.
            Using this parameter is not recommended, instead, consider
            using the `set_children`, `set_parents` or `set_edge`
            functions.
            Optional, defaults to `None`.

        Possible Errors
        - ValueError: If `edges` produces a malformed adjacency matrix.
        """
        edge_data: list[list[Fraction | None]] | None = None
        if edges is not None:
            edge_data = [
                [Fraction(item) if item is not None else None for item in row]
                for row in edges
            ]
            if len(edge_data) != node_count:
                raise ValueError("node count and edge data dimension mismatch")
            for edge_data_row in edge_data:
                if len(edge_data_row) != node_count:
                    raise ValueError(
                        "node count and edge data dimension mismatch"
                    )
        else:
            edge_data = [
                [None for _ in range(node_count)] for _ in range(node_count)
            ]
        self._edge_data: list[list[Fraction | None]] = edge_data
        self._length: int = node_count

    def __len__(
        self,
    ) -> int:
        """
        Returns the total number of nodes in this digraph.
        """
        return self._length

    def __str__(
        self,
    ) -> str:
        """
        Returns a "pretty" string representation of this digraph.
        """
        graph_string_builder: list[str | None] = [
            None for _ in range(self._length)
        ]
        for node in range(self._length):
            node_name = f"{node} \u25a1\u2500"
            node_name_space = " " * len(node_name)
            children = list(self.get_children(node))
            num_children = len(children)
            node_string_builder: list[str | None] = [
                None for _ in range(num_children)
            ]
            for i in range(num_children):
                if i == 0:
                    if num_children == 1:
                        node_string_builder[i] = (
                            f"{node_name}\u2500\u2500({children[i][1]})"
                            f"\u2500\u25b7 {children[i][0]}"
                        )
                    else:
                        node_string_builder[i] = (
                            f"{node_name}\u252c\u2500({children[i][1]})"
                            f"\u2500\u25b7 {children[i][0]}"
                        )
                elif i == num_children - 1:
                    node_string_builder[i] = (
                        f"{node_name_space}\u2514\u2500({children[i][1]})"
                        f"\u2500\u25b7 {children[i][0]}"
                    )
                else:
                    node_string_builder[i] = (
                        f"{node_name_space}\u251c\u2500({children[i][1]})"
                        f"\u2500\u25b7 {children[i][0]}"
                    )
            graph_string_builder[node] = "\n".join(
                s for s in node_string_builder if s is not None
            )
            if graph_string_builder[node] == "":
                graph_string_builder[node] = None
        return "\n\n".join(s for s in graph_string_builder if s is not None)

    def __repr__(
        self,
    ) -> str:
        """
        Returns a reproduction string representation of this digraph.

        Notes
        - Assuming all relevant libraries have been imported, the
            reproduction string can be run as valid Python to create
            an exact copy of this digraph.
        """
        obj_name = self.__class__.__name__
        node_count = self._length
        edge_data = "[\n        [{}],\n    ]".format(
            "],\n        [".join(
                ", ".join(repr(item) for item in row)
                for row in self._edge_data
            )
        )
        return (
            f"{obj_name}(\n"
            f"    node_count={node_count},\n"
            f"    edge_data={edge_data},\n"
            f")"
        )

    def new_node(
        self,
        children: Optional[
            Iterable[int | tuple[int, float | Fraction | None]]
        ] = None,
        parents: Optional[
            Iterable[int | tuple[int, float | Fraction | None]]
        ] = None,
    ) -> int:
        """
        Creates a new node in this digraph, and returns its index for
            convenience.

        Arguments
        - children: An iterable of node indices or index-weight tuples
            that will be used to initialize the new node's outbound
            connections.
            Optional, defaults to none.
        - parents: An iterable of node indices or index-weight tuples
            that will be used to initialize the new node's inbound
            connections.
            Optional, defaults to none.

        Notes
        - Specifying the children or parents parameters is equivalent to
            leaving it blank and calling the `set_children` or
            `set_parents` methods (respectively) manually.
        """
        new_node_index = self._length
        for edge_data_row in self._edge_data:
            edge_data_row.append(None)
        self._length += 1
        self._edge_data.append([None] * self._length)
        if children is not None:
            self.set_children(new_node_index, children)
        if parents is not None:
            self.set_parents(new_node_index, parents)
        return new_node_index

    def get_edge(
        self,
        parent: int,
        child: int,
    ) -> Fraction | None:
        """
        Gets the value of an edge from a parent to a child node.

        Arguments
        - parent: The parent node of the edge.
        - child: The child node of the edge.

        Possible Errors
        - NodeNotFoundError: If a specified node index does not exist.

        Notes
        - Since directed edges have directionality, the order of the
            operands matters.
        """
        try:
            return self._edge_data[parent][child]
        except KeyError:
            raise NodeNotFoundError(f"could not find edge {parent}->{child}")

    def get_parents(
        self,
        node: int,
    ) -> Iterable[tuple[int, Fraction]]:
        """
        Generate index-weight tuples for each edge from this a parent
            node to this node.

        Arguments
        - node: The node for which to find parent nodes.
        """
        for i in range(self._length):
            weight = self._edge_data[i][node]
            if weight is not None:
                yield i, weight

    def get_children(
        self,
        node: int,
    ) -> Iterable[tuple[int, Fraction]]:
        """
        Generate index-weight tuples for each edge from this node to a
            child node.

        Arguments
        - node: The node for which to find child nodes.
        """
        for i in range(self._length):
            weight = self._edge_data[node][i]
            if weight is not None:
                yield i, weight

    def set_edge(
        self,
        parent: int,
        child: int,
        weight: float | Fraction | None = Fraction(1),
    ) -> None:
        """
        Set the value of an edge by overwriting its old value.

        Arguments
        - parent: The source node for the edge.
        - child: The destination node for the edge.
        - weight: The weight of the edge.
            Optional, defaults to 1.

        Possible Errors
        - NodeNotFoundError: If a specified node index does not exist.

        Notes
        - A weight of 0 does not imply a non-connection, it simply means
            a connection with weight 0. To explicitly specify a
            non-connection, use a weight of `None`.
        - Since directed edges have directionality, the order of the
            operands matters.
        """
        try:
            if weight is None:
                self._edge_data[parent][child] = None
            else:
                self._edge_data[parent][child] = Fraction(weight)
        except KeyError:
            raise NodeNotFoundError(f"could not find edge {parent}->{child}")

    def set_parents(
        self,
        node: int,
        parents: Iterable[int | tuple[int, float | Fraction | None]],
    ) -> None:
        """
        Set edges based on indices or index-weight tuples for each edge
            from a parent node to a this node.

        Arguments
        - node: The node for which to set parent nodes.

        Notes
        - A weight of 0 does not imply a non-connection, it simply means
            a connection with weight 0. To explicitly specify a non-
            connection, use a weight of `None`.
        """
        for parent in parents:
            if isinstance(parent, int):
                self.set_edge(parent, node, Fraction(1))
            else:
                self.set_edge(parent[0], node, parent[1])

    def set_children(
        self,
        node: int,
        children: Iterable[int | tuple[int, float | Fraction | None]],
    ) -> None:
        """
        Set edges based on indices or index-weight tuples for each edge
            from this node to a child node.

        Arguments
        - node: The node for which to set child nodes.

        Notes
        - A weight of 0 does not imply a non-connection, it simply means
            a connection with weight 0. To explicitly specify a non-
            connection, use a weight of `None`.
        """
        for child in children:
            if isinstance(child, int):
                self.set_edge(node, child, Fraction(1))
            else:
                self.set_edge(node, child[0], child[1])

    def indegree(
        self,
        node: int,
    ) -> Fraction:
        """
        Calculates the in-degree of a node in this digraph, where
            in-degree refers to the combined weight of all incoming to
            the node.

        Arguments
        - node: The node for which to find the in-degree.
        """
        return sum(
            (
                v
                for v in (
                    self._edge_data[i][node] for i in range(self._length)
                )
                if v is not None
            ),
            start=Fraction(0),
        )

    def outdegree(
        self,
        node: int,
    ) -> Fraction:
        """
        Calculates the out-degree of a node in this digraph, where
            out-degree refers to the combined weight of all outgoing
            edges from the node.

        Arguments
        - node: The node for which to find the out-degree.
        """
        return sum(
            (v for v in self._edge_data[node] if v is not None),
            start=Fraction(0),
        )

    # PROPERTIES

    @property
    def adjacency_matrix(
        self,
    ) -> Matrix:
        return Matrix(
            (
                item if item is not None else Fraction(0)
                for item in (self.get_edge(i, j) for j in range(self._length))
            )
            for i in range(self._length)
        )

    @property
    def indegree_matrix(
        self,
    ) -> Matrix:
        return Matrix(
            (
                self.indegree(i) if i == j else Fraction(0)
                for j in range(self._length)
            )
            for i in range(self._length)
        )

    @property
    def outdegree_matrix(
        self,
    ) -> Matrix:
        return Matrix(
            (
                self.outdegree(i) if i == j else Fraction(0)
                for j in range(self._length)
            )
            for i in range(self._length)
        )
