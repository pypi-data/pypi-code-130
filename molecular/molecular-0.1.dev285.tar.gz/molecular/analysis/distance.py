"""
distance.py

language: python
version: 3.x
author: C. Lockhart <chris@lockhartlab.org>
"""

from molecular.analysis._analysis_utils import _distances
from molecular.errors import TrajectoryError
from molecular.misc import is_monotonic

import numpy as np
import pandas as pd
from scipy.stats import binned_statistic_dd
from sparse import COO


def contacts(a, b, cutoff=4.5):
    """
    Compute atomic contacts.

    Parameters
    ----------
    a, b : Trajectory
    cutoff : float

    Returns
    -------
    nunpy.ndarray
    """

    return distances(a, b) < cutoff


def contacts_to_vector(contacts, a, b, by='residue'):
    # Get sparse representation of contacts
    contacts_sparse = COO(contacts)

    # Update IDs
    contacts_sparse.coords[1] = pd.Series(dict(zip(range(a.n_atoms), a.topology[f'{by}_id'])))[
        contacts_sparse.coords[1]].to_numpy()
    contacts_sparse.coords[2] = pd.Series(dict(zip(range(b.n_atoms), b.topology[f'{by}_id'])))[
        contacts_sparse.coords[2]].to_numpy()

    # Create DataFrame
    df = pd.DataFrame({
        'structure_id': contacts_sparse.coords[0],
        f'{by}_id0': contacts_sparse.coords[1],
        f'{by}_id1': contacts_sparse.coords[2],
    })

    # Aggregate and return
    return (
        df
        .drop_duplicates()
        .sort_values(['structure_id', f'{by}_id1'])
        .groupby('structure_id')[f'{by}_id1']
        .agg(list)
        .to_numpy()
    )


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
