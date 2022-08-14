"""
distance.py

language: python
version: 3.x
author: C. Lockhart <chris@lockhartlab.org>
"""

from molecular.analysis._analysis_utils import _distances

import numpy as np
import pandas as pd
from scipy.stats import binned_statistic_dd
from sparse import COO


def contacts(a, b, by='atom', cutoff=4.5):
    """
    Compute atomic contacts.

    Parameters
    ----------
    a, b : Trajectory
    by : float
    cutoff : float

    Returns
    -------

    """

    results = distances(a, b) < cutoff

    if by == 'residue':
        if np.sum(results) > 0:
            # Create a list of break points that define structure and residues (by index in list)
            breaks = [
                np.arange(results.shape[0]).tolist() + [results.shape[0]],  # noqa
                [0] + np.ravel(np.argwhere(np.diff(a.topology['residue_id']) > 0)).tolist() + [a.n_atoms],  # noqa
                [0] + np.ravel(np.argwhere(np.diff(b.topology['residue_id']) > 0)).tolist() + [b.n_atoms]  # noqa
            ]

            # Turn the results into a sparse COO. This preserves structure ID and atom indices (0-based)
            results_sparse = COO(results)

            # Do a multidimensional bin and compute maximum along bins
            statistic, bin_edges, bin_number = binned_statistic_dd(
                sample=results_sparse.coords.T,
                values=results_sparse.data,
                statistic='max',
                bins=breaks,
            )

            # Nans occur when bin is empty, so convert this to False
            results = np.nan_to_num(statistic).astype(bool)
        else:  # We get here if results is empty, and then we set results to an array of all Falses
            results = np.zeros((results.shape[0], a.n_residues, b.n_residues), dtype='bool')

    return results


def contacts_to_vector(contacts, axis=1):
    return pd.DataFrame(np.argwhere(np.max(contacts, axis=axis))).groupby(0).agg(list)[1].to_numpy()


# Compute the distance between two Trajectories
def distances(a, b):
    """
    Compute the distance between two Trajectory instances.

    Parameters
    ----------
    a, b : Trajectory
        Two trajectories. Must have same dimensions.

    Returns
    -------
    numpy.ndarray
        Distance between every frame in the trajectory.
    """

    a_xyz = a.xyz.to_numpy().reshape(*a.shape)
    b_xyz = b.xyz.to_numpy().reshape(*b.shape)

    return _distances(a_xyz, b_xyz)


# Compute the distance between two Trajectories
def distance(a, b):
    """
    Compute the distance between two Trajectory instances.

    Parameters
    ----------
    a, b : Trajectory
        Two trajectories. Must have same dimensions.

    Returns
    -------
    numpy.ndarray
        Distance between every frame in the trajectory.
    """

    # TODO there must be a better way
    a_xyz = a.xyz.to_numpy().reshape(*a.shape)
    b_xyz = b.xyz.to_numpy().reshape(*b.shape)

    return np.sqrt(np.sum(np.square(a_xyz - b_xyz), axis=(1, 2)))

# Compute pairwise distance between two Trajectories (or within a Trajectory?)
def pairwise_distance(a, b):
    pass
