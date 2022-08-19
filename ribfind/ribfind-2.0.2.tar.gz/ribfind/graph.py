#!/usr/bin/env python3
"""Weighted undirected graph data structure

Defines a graph where nodes are model_ids and edges model interaction
strength.

"""


class _Edge:
    def __init__(self, this_model_id, that_model_id):
        self.this = this_model_id
        self.that = that_model_id
        self.interaction_strength = 0


class Graph:
    """A Graph"""

    def __init__(self):
        self.edges = {}

    def add_edge(self, this_model, that_model, interaction_strength):
        """Add and edge to the graph"""
        edge = self.get_edge(this_model.model_id, that_model.model_id)
        edge.interaction_strength = interaction_strength

    def get_edges(self):
        """Returns a list of edges sorted by interaction strength"""
        edges = list(self.edges.values())
        edges.sort(key=lambda x: x.interaction_strength)
        return edges

    def get_weights(self):
        """Returns a sorted list of unique edge weights"""
        weights = [e.interaction_strength for e in self.edges.values()]
        weights.sort()
        return weights

    def get_edge(self, this_model_id, that_model_id):
        """Returns the edge between two contigs."""
        this = min(this_model_id, that_model_id)
        that = max(this_model_id, that_model_id)
        if self.edges.get((this, that)) is None:
            self.edges[(this, that)] = _Edge(this, that)
        return self.edges[(this, that)]
