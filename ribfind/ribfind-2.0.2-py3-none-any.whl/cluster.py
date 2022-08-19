#!/usr/bin/env python3
"""Cluster

Here is some information
"""

from ribfind.model import Contig, ContigGroup


class RigidBody:
    """A rigid body is a set of SSEs and possibly connecting loops."""

    def __init__(self, model):
        self.models = [model]
        self.loop_ids = []

    def get_id(self):
        """The 'id' of a rigid body is simply the lowest model_id of
        the contained SSEs"""
        return min(c.model_id for c in self.models)

    def contains_model_id(self, model_id):
        """Check if rigid body contains sse_id."""
        return model_id in [s.model_id for s in self.models]

    def add_loops(self, model):
        """The rule for adding loops to clusters is as follows:

        If there exists two SSEs which are separated by a single loop,
        add the loop to the cluster.

        Because contigs are sequentialy numbered, adding loops
        involves a trivial check: Loop from the lowest to highest
        contig_id in the cluster checking whether the contig_id is
        missing from the cluster and the contig_id's either side are
        present.

        """
        contig_ids = [c.contig_id for c in self.get_contigs()]
        min_id = min(contig_ids)
        max_id = max(contig_ids)
        loops = []
        for loop_id in range(min_id, max_id):
            prev_id = loop_id - 1
            next_id = loop_id + 1
            if (
                loop_id not in contig_ids
                and prev_id in contig_ids
                and next_id in contig_ids
            ):
                loops.append(model.get_loop(loop_id))
        self.loop_ids = loops

    def __len__(self):
        return len(self.models)

    def get_contigs(self):
        """Return a list of all contigs"""
        contigs = []
        for sse in self.models + self.loop_ids:
            if isinstance(sse, Contig):
                contigs.append(sse)
            elif isinstance(sse, ContigGroup):
                contigs += sse.get_contigs()
        return contigs


class Clusters:
    """A collection of rigid bodies.

    Initialised from a list of models.

    Edges can be added by calling 'condense' which will merge rigid bodies that are
    now connected by the edge.

    """

    def __init__(self, models, edge_cutoff, dens_cutoff):
        self.dens_cutoff = dens_cutoff
        self.rigid_bodies = {}
        self.num_models = len(models)
        self.edge_cutoff = edge_cutoff
        for model in models:
            self._register(RigidBody(model))

    def dens_clusters(self):
        """Dense clusters are cluster with more than dens_cutoff models"""
        return [d for d in self.rigid_bodies.values() if len(d) >= self.dens_cutoff]

    def unclustered(self):
        """Unclustered are clusters with less than dens_cutoff models"""
        return [d for d in self.rigid_bodies.values() if len(d) < self.dens_cutoff]

    def num_clusters(self):
        """The number of clusters is the number of RigidBody objects with more than 1 SSE"""
        return len(self.dens_clusters())

    def num_members(self):
        """The number of members in the clusters including loops"""
        num_members = 0

        for rigid_body in self.dens_clusters():
            num_members += len(rigid_body)

        return num_members

    def weight(self):
        """TODO: the weight is"""
        if self.num_models == 0:
            return 0
        w_clust = float(self.num_clusters()) + (
            float(self.num_members()) / float(self.num_models)
        )
        return w_clust

    def _register(self, rigid_body):
        self.rigid_bodies[rigid_body.get_id()] = rigid_body

    def _deregister(self, rigid_body):
        self.rigid_bodies.pop(rigid_body.get_id())

    def _get_rb_by_model(self, model_id):
        for rigid_body in self.rigid_bodies.values():
            if rigid_body.contains_model_id(model_id):
                return rigid_body
        return None

    def condense(self, edge):
        """Adding an edge does nothing if it connects SSEs in a cluster. If it
        connects SSEs in different clusters the cluster with largest ID is
        merged into the smaller cluster."""
        if edge.interaction_strength <= self.edge_cutoff:
            return False

        this_rb = self._get_rb_by_model(edge.this)
        that_rb = self._get_rb_by_model(edge.that)

        if this_rb is None or that_rb is None:
            return True

        # Same cluster, so can't be condensed.
        if this_rb == that_rb:
            return True

        # Merge clusters.
        if this_rb.get_id() < that_rb.get_id():
            self._merge(that_rb, this_rb)
        else:
            self._merge(this_rb, that_rb)

        return True

    def _merge(self, source, dest):
        dest.models += source.models
        self._deregister(source)

    def add_loops(self, model):
        """Add any loops which connect SSEs in the rigid bodies to the
        respective rigid bodies"""
        for rigid_body in self.rigid_bodies.values():
            rigid_body.add_loops(model)


def get_solutions(model, interactions, dens_cutoff, add_loops=True):
    """Generate all the possible clusters for a model and interactions."""
    rigid_bodies = model.rigid_bodies()
    graph = interactions.graph(rigid_bodies)
    weights = [0] + graph.get_weights()
    prev_score = None
    results = []
    while True:
        if len(weights) == 0:
            break
        weight = weights.pop(0)
        clusters = Clusters(rigid_bodies, weight, dens_cutoff)

        for edge in graph.get_edges():
            clusters.condense(edge)

        if clusters.weight() != prev_score:
            if clusters.weight() >= 0:
                prev_score = clusters.weight()
                results.append(clusters)
            else:
                break

    if add_loops:
        for clusters in results:
            clusters.add_loops(model)
    return results
