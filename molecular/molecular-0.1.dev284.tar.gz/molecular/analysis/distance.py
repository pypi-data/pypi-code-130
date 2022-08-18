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

    # Compute distances
    results = distances(a, b) < cutoff

    # Turn results into DataFrame
    ndx = np.unravel_index(range(np.product(results.shape)), results.shape)
    df = pd.DataFrame({
        'structure_id': ndx[0],
        f'{by}_id0': pd.Series(dict(zip(range(a.n_atoms), a.topology[f'{by}_id'])))[ndx[1]].to_numpy(),
        f'{by}_id1': pd.Series(dict(zip(range(b.n_atoms), b.topology[f'{by}_id'])))[ndx[2]].to_numpy(),
        'contact': results.ravel()
    }).set_index(['structure_id', f'{by}_id0', f'{by}_id1'])

    # Aggregate (only necessary if `by` != 'atom')
    if by != 'atom':
        df = df.pivot_table(index=['structure_id', f'{by}_id0', f'{by}_id1'], values='contact', aggfunc='max')

    # Return
    return df  # results


def contacts_to_vector(contacts, column):
    """
    Helper function to convert output from `contacts` to a vector.

    Parameters
    ----------
    contacts : pandas.DataFrame
    along : str

    Returns
    -------
    numpy.ndarray
    """

    return (
        contacts
        .query('contact == True')
        .pivot_table(index=['structure_id', column], values='contact', aggfunc='max')
        .reset_index()
        .groupby('structure_id')['residue_id1']
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
