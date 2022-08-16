r"""
Module contains abstract base class for spin metrics
"""
from abc import ABC, abstractmethod
from spinterface.inputs.lattice.CLattice import CLattice
from typing import List
import numpy as np
import pandas as pd
from pathlib import Path


class ISpinMetric(ABC):
    r"""
    Abstract base class for metrics defining the distances between spin images produced by the Spinaker-Code
    """

    def __init__(self) -> None:
        r"""

        """
        self._distance_matrix = None

    @abstractmethod
    def distance(self, latt1: CLattice, latt2: CLattice, label1: str, label2: str) -> float:
        r"""
        :param latt1: Instance 1 of CLattice
        :param latt2: Instance 2 of CLattice
        :return: distance between latt1 and latt2
        """

    def distance_matrix(self, lattices: List[CLattice], labels: List[str]) -> np.ndarray:
        r"""
        :param lattices: List of instances of CLattice
        :return: symmetric distance matrix
        """
        if self._distance_matrix is None:
            n = len(lattices)
            dist_matrix = np.zeros(shape=(n, n))
            for (i_l, l) in enumerate(lattices[:-1]):
                for i_p in range(i_l, len(lattices)):
                    p = lattices[i_p]
                    d = self.distance(l, p, label1=labels[i_l], label2=labels[i_p])
                    dist_matrix[i_l, i_p] = d
                    dist_matrix[i_p, i_l] = d
            self._distance_matrix = dist_matrix
            return dist_matrix
        else:
            return self._distance_matrix

    def write_distance_matrix(self, labels: List[str], path: Path = Path.cwd() / 'dist_matrix.dat',
                              seperator: str = ',') -> None:
        r"""
        Write distance matrix to file
        :param labels: List of labels describing the objects the dist-matrix is calculated on
        :return: None
        """
        if self._distance_matrix is None:
            raise ValueError("Please calculate the distance matrix before you write it...")
        if len(labels) != np.shape(self._distance_matrix)[0]:
            raise ValueError("Sizes of distance matrix and labels do not match...")
        df_dict = {'label': labels}
        for (i_l, l) in enumerate(labels):
            df_dict[l] = self._distance_matrix[:, i_l]
        df = pd.DataFrame(df_dict)
        df.to_csv(path, sep=seperator, index=False)
