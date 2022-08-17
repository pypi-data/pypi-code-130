#!/usr/bin/env python3
from ribfind.writers import SummaryWriter, RigidBodyWriter
from ribfind.cluster import Clusters, RigidBody
from ribfind.model import Helix


class MockCluster:
    def __init__(
        self, edge_cutoff: float, num_clusters: int, num_members: int, weight: float
    ):
        self.edge_cutoff = edge_cutoff
        self._num_clusters = num_clusters
        self._num_members = num_members
        self._weight = weight

    def num_clusters(self):
        return self._num_clusters

    def num_members(self):
        return self._num_members

    def weight(self):
        return self._weight


def test_summary_writer():
    sw = SummaryWriter([])
    expected = """Summary of RIBFIND clusters for the range of cutoffs
% cutoff        # clusters      # clustered SSEs      Cluster weight"""
    assert sw.render() == expected

    sw = SummaryWriter([MockCluster(0.03, 2, 3, 4.5), MockCluster(0.6, 2, 3, 4.5)])
    expected = """Summary of RIBFIND clusters for the range of cutoffs
% cutoff        # clusters      # clustered SSEs      Cluster weight
3.00            2               3                     4.50
60.00           2               3                     4.50"""
    assert sw.render() == expected


def test_rigid_body_writer():
    mock = Clusters([], 0.034, 2)
    rbw = RigidBodyWriter(4.5, mock)
    expected = """#RIBFIND_clusters: 4.5 3.4 0 0 0 0
#individual_rigid_bodies 0"""
    assert rbw.render() == expected

    helix_a = Helix("A", 23, 42)
    helix_b = Helix("A", 87, 101)
    helix_c = Helix("A", 50, 60)
    helix_a.model_id = 1
    helix_b.model_id = 2
    helix_c.model_id = 3
    rb = RigidBody(helix_a)
    rb.models += [helix_b, helix_c]
    mock = Clusters([], 0.034, 2)
    mock._register(rb)
    rbw = RigidBodyWriter(4.5, mock)
    expected = """#RIBFIND_clusters: 4.5 3.4 1 3 0 0
23:A 41:A 87:A 100:A 50:A 59:A 
#individual_rigid_bodies 0"""
    assert rbw.render() == expected
