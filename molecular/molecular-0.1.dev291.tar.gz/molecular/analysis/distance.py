"""
distance.py

language: python
version: 3.x
author: C. Lockhart <chris@lockhartlab.org>
"""

from molecular.analysis._analysis_utils import _distances, _minimum_distances

import numpy as np
import pandas as pd
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
    numpy.ndarray
    """

    return distances(a, b) < cutoff


def contacts_to_vector(contacts, axis1=None, axis2=None):
    """
    Convert contacts array to contact vector. With `axis1` and `axis2`, `contacts` can be changed such that indices
    besides the atom IDs are used.

    Parameters
    ----------
    contacts : numpy.ndarray
    axis1 : list-like
        (Optional) New indices for axis 1 of `contacts`
    axis2 : list-like
        (Optional) New indices for axis 2 of `contacts`

    Returns
    -------
    numpy.ndarray
    """

    # Get sparse representation of contacts
    contacts_sparse = COO(contacts)

    # Update axis IDs if necessary
    def _update_id(i, x):
        contacts_sparse.coords[i] = \
            pd.Series(dict(zip(range(contacts.shape[i]), x)))[contacts_sparse.coords[i]].to_numpy()
    if axis1 is not None:
        _update_id(1, axis1)
    if axis2 is not None:
        _update_id(2, axis2)

    # Create DataFrame
    df = pd.DataFrame({
        'structure_id': contacts_sparse.coords[0],
        f'i': contacts_sparse.coords[1],
        f'j': contacts_sparse.coords[2],
    })

    # Aggregate to series
    sr = (
        df
        .drop_duplicates()
        .sort_values(['structure_id', 'j'])
        .groupby('structure_id')['j']
        .agg(list)
    )

    # Make a correction for missing structure IDs (if there were no contacts they'll be absent)
    is_empty = ~np.max(contacts, axis=(1, 2))
    if np.sum(is_empty) > 0:
        for i in np.argwhere(is_empty).ravel():
            sr.loc[i] = []

        sr.sort_index(inplace=True)

    # Return as numpy array
    return sr.to_numpy()


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


# Compute the minimum distances across all images
def minimum_distances(a, b):
    """

    Parameters
    ----------
    a
    b

    Returns
    -------

    """

    # Make sure that `a` and `b` come from the same parent Trajectory
    if a.parent.designator != b.parent.designator:
        raise AttributeError('`a` and `b` must have same parent')

    # Extract coordinates and boxes
    a_xyz = a.xyz.to_numpy().reshape(*a.shape)
    b_xyz = b.xyz.to_numpy().reshape(*b.shape)
    a_box = a.box.to_numpy()
    b_box = b.box.to_numpy()

    # One more sanity check that `a_box` and `b_box` are identical
    if ~np.allclose(a_box, b_box):
        raise AttributeError('`a` and `b` have different dimensions')

    # Finally, we can compute
    return _minimum_distances(a_xyz, b_xyz, a_box)


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
