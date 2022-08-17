#!/usr/bin/env python3
"""
Used for calculating contact distances.
"""

import re
import numpy as np
from ribfind.model import Residue


class CentroidContact:
    """An object for checking contact distance between residues."""

    def __init__(self, dist_cutoff):
        self.id_to_centroid = {}
        self.dist_cutoff = dist_cutoff

    def make_box(self, residues):
        """Return an axis aligned bounding box around the residues."""
        return Box(self.dist_cutoff, [self.id_to_centroid[r] for r in residues])

    def in_contact(self, res_a: Residue, res_b: Residue):
        """Returns true if res_a and res_b are with in the contact distance"""
        try:
            center_a = self.id_to_centroid[res_a]
            center_b = self.id_to_centroid[res_b]
            dist = np.linalg.norm(center_a - center_b)
            if dist < self.dist_cutoff:
                return True
            return False
        except KeyError:
            return False

    def add_residue(self, res, coords):
        """Given a residue and a list of coordinates saves the
        centroid for the residue.
        """
        if len(coords) == 0:
            return
        total = sum(coord for coord in coords)
        self.id_to_centroid[res] = total / float(len(coords))


def make_protein_contacts(structure, dist_cutoff=6.5):
    """Create contact checking object with the following rules.

    - Residues are in contact if their centroids are with in
      'dist_cutoff' of one another.

    - Centroids are calculated as the average position of non-backbone
      atoms in the residue, with the exception of glycine which uses the
      C-alpha atom.
    """
    backbone_atom_names = ["CA", "N", "O", "C"]

    centroids = CentroidContact(
        dist_cutoff,
    )

    for chain in structure[0]:
        for residue in chain:
            _, res_num, _ = residue.get_id()
            if residue.get_resname() == "GLY":
                coords = [
                    np.array(list(a.get_vector()))
                    for a in residue.get_list()
                    if a.get_id() == "CA"
                ]
            else:
                coords = [
                    np.array(list(a.get_vector()))
                    for a in residue.get_list()
                    if a.get_id() not in backbone_atom_names
                ]
            centroids.add_residue(Residue(chain.get_id(), res_num), coords)

    return centroids


def make_rna_contacts(structure, dist_cutoff=7.5):
    """Create contact checking object with the following rules:

    - Residues are in contact if their centroids are with in
      'dist_cutoff' of each over.

    - Centroids are calculated as the average position of atoms in the
      residues, which do not contain `P` or `'` in there element
      names.
    """
    centroids = CentroidContact(dist_cutoff)
    for chain in structure[0]:
        for residue in chain:
            _, res_num, _ = residue.get_id()
            coords = [
                np.array(list(a.get_vector()))
                for a in residue.get_list()
                if not (re.search(r"P", a.get_name()) or re.search(r"'", a.get_name()))
            ]
            centroids.add_residue(Residue(chain.get_id(), res_num), coords)
    return centroids


class Box:
    """A class for speeding up contact checks between sets of residues.

    To avoid O(MN) checks between two sets of residues of size M and
    N, we compute two boxes in O(M+N) time and check whether they
    overlap in O(1).

    In practice, the box is computed once per model and cached.

    If boxes overlap, there _may_ be residues in contact distance, in which
    case expensive contact checks can take place.

    """

    def __init__(self, contact_dist, coords):
        self.contact_dist = contact_dist
        x_vals = [v[0] for v in coords]
        y_vals = [v[1] for v in coords]
        z_vals = [v[2] for v in coords]
        self.lower = [
            min(x_vals, default=0),
            min(y_vals, default=0),
            min(z_vals, default=0),
        ]
        self.upper = [
            max(x_vals, default=0),
            max(y_vals, default=0),
            max(z_vals, default=0),
        ]

    def overlaps_box(self, other):
        """Check if box overlaps with other box"""
        return (
            (self.upper[0] - other.lower[0]) > -self.contact_dist
            and (other.upper[0] - self.lower[0]) > -self.contact_dist
            and (self.upper[1] - other.lower[1]) > -self.contact_dist
            and (other.upper[1] - self.lower[1]) > -self.contact_dist
            and (self.upper[2] - other.lower[2]) > -self.contact_dist
            and (other.upper[2] - self.lower[2]) > -self.contact_dist
        )
