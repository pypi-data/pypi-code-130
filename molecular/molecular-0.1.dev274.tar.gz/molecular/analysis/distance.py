"""
distance.py

language: python
version: 3.x
author: C. Lockhart <chris@lockhartlab.org>
"""

from molecular.analysis._analysis_utils import _distances

import numpy as np
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

    # if by == 'residue':
    #     breaks = [
    #         np.arange(a.shape[0]),
    #         [0] + np.ravel(np.argwhere(np.diff(a.topology['residue_id']) > 0)).tolist() + [a.n_atoms],  # noqa
    #         [0] + np.ravel(np.argwhere(np.diff(b.topology['residue_id']) > 0)).tolist() + [b.n_atoms]  # noqa
    #     ]
    #
    #     results_sparse = COO(results)
    #
    #     statistic, bin_edges, bin_number = binned_statistic_dd(
    #         sample=results_sparse.coords.T,
    #         values=results_sparse.data,
    #         statistic='max',
    #         bins=breaks,
    #     )
    #
    #     results = np.nan_to_num(statistic).astype(bool)

    return results


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
