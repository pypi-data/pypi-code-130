r"""
Module containing a matching class between spin images
"""
import numpy as np
import copy
from spinterface.inputs.lattice.CLattice import CLattice
from typing import Tuple, List, Any, Union
from itertools import groupby


class CMatchImages:
    r"""
    This class performs operations to calculate the smallest geodesic difference between images
    """

    def __init__(self, lattice1: CLattice, lattice2: CLattice) -> None:
        r"""
        Initializes the matching process between the representations lattice1 and lattice2
        """
        self._lattice1 = lattice1
        self._lattice2 = lattice2
        self._update_distance_shells()

    def _update_distance_shells(self) -> None:
        r"""
        Updates the distance shells, could be needed if lattice was transformed
        """
        self._distance_shells_latt1 = self._analyse_distance_shells(latt=self._lattice1)
        self._distance_shells_latt2 = self._analyse_distance_shells(latt=self._lattice2)

    @property
    def lattice1(self) -> CLattice:
        r"""
        :return: Lattice Object 1
        """
        return self._lattice1

    @property
    def lattice2(self) -> CLattice:
        r"""
        :return: Lattice Object 1
        """
        return self._lattice2

    @staticmethod
    def _analyse_distance_shells(latt: CLattice) -> List[List[Union[float, List[int]]]]:
        r"""
        Calculates the distances shells (sorted by distance) for a fiven lattice.
        :return: A nested list [[distance_shell1,[shell1_idx1,...,shell1_idxM]],...,
        [distance_shellN,[shellN_idx1,...,shellN_idxM]]]
        """
        idx_list_sorted_by_distance = list(
            map(tuple, sorted([[round(np.linalg.norm(p), 4), idx] for (idx, p) in enumerate(latt.points[:, :2])])))
        idx_list = []
        for distance, indices in groupby(idx_list_sorted_by_distance, lambda x: x[0]):
            # for indic in indices:
            #    if indic[1]==1273:
            #        print(indic)
            idx_list.append([distance, [i[1] for i in indices]])
        return idx_list

    @staticmethod
    def _get_shell_from_distance_shells(shells: List[List[Union[float, List[int]]]], value: float) -> List[
        Union[float, List[int]]]:
        r"""
        :return: The distance shell with distance closest to the given reference value.
        """
        remaining_elements = len(shells)
        while remaining_elements > 6:
            mid_index = int(remaining_elements / 2)
            # print(f'Mid index: {mid_index}')
            # print(f'List after mid index: {shells[mid_index:][:10]}')
            # print(f'List before mid index: {shells[:mid_index+1][-10:]}')
            if shells[mid_index][0] > value:
                del shells[mid_index + 2:]
            else:
                del shells[:mid_index - 2]
            remaining_elements = len(shells)
        # search remaining part of the list
        min_value = abs(shells[0][0] - value)
        distance_shell = shells[0]
        for remaining_element in shells:
            diff = abs(remaining_element[0] - value)
            if diff <= min_value:
                min_value = diff
                distance_shell = remaining_element
        return distance_shell

    def _get_closest_distance_shell(self, shells: List[List[Union[float, List[int]]]], value: float) -> Tuple[int,float]:
        r"""
        """
        distances = [item[0] for item in shells]
        idx = min(range(len(distances)), key=lambda i: abs(distances[i] - value))
        return idx, distances[idx]

    def _get_distance_shells_in_range(self, shells: List[List[Union[float, List[int]]]], center: float, width: float = 1/np.sqrt(2.0)) -> List[List[Union[float, List[int]]]]:
        r"""

        :param shells:
        :param center:
        :param range:
        :return:
        """
        distances = [item[0] for item in shells]
        min_idx = min(range(len(distances)), key=lambda i: abs(distances[i] - (center-width)))
        max_idx = min(range(len(distances)), key=lambda i: abs(distances[i] - (center+width)))
        return shells[min_idx:max_idx+1]

    def _find_closest_point(self, distance_shells: List[List[Union[float, List[int]]]], points: np.ndarray,
                            reference_point: np.ndarray) -> Tuple[np.ndarray, int]:
        r"""
        Find fast a the closest point to some reference point
        :return:
        """
        idx_closest, distance_closest = self._get_closest_distance_shell(distance_shells, np.linalg.norm(reference_point))
        closest_shells = self._get_distance_shells_in_range(shells=distance_shells, center=distance_closest)
        # print(f'closest_shell: {closest_shell}')
        min_point_index = closest_shells[0][1][0]
        min_point = points[min_point_index, :]
        min_dist = np.linalg.norm(reference_point - min_point)
        for shell in closest_shells:
            for shell_idx in shell[1]:
                dist = np.linalg.norm(reference_point - points[shell_idx, :])
                if dist < min_dist:
                    min_dist = dist
                    min_point = points[shell_idx, :]
                    min_point_index = shell_idx
        return min_point, min_point_index

    def _find_closest_point_brute_force(self, points: np.ndarray, reference_point: np.ndarray) -> Tuple[
        np.ndarray, int]:
        r"""
        """
        min_point_index = 0
        min_point = points[min_point_index, :]
        min_dist = np.linalg.norm(reference_point - min_point)
        for idx, point in enumerate(points):
            dist = np.linalg.norm(reference_point - point)
            if dist < min_dist:
                min_dist = dist
                min_point = point
                min_point_index = idx
        return min_point, min_point_index

    def shift_to_center(self) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Center both lattices with respect the lattice point closest to their respective center of mass (with respect
        to topological density)
        :return: The lattice points closest to the topological center
        """
        # first of all we have to calculate the center of the lattice with respect to the topological density
        tc1, tc2 = self.topo_centers()
        # now we have to find the closest lattice point to the topological center
        # for fast searching look into the distance shells
        mp1, _ = self._find_closest_point(self._distance_shells_latt1, self._lattice1.points, tc1)
        mp2, _ = self._find_closest_point(self._distance_shells_latt2, self._lattice2.points, tc2)
        self._lattice1.points = self._lattice1.points.copy() - mp1
        self._lattice2.points = self._lattice2.points.copy() - mp2
        # update the distance shells
        self._update_distance_shells()
        return mp1, mp2

    def topo_centers(self) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        :return: The topological centers of both lattices
        """
        topo1 = self._lattice1.topologies[0]
        topo2 = self._lattice2.topologies[0]
        return topo1.topological_center, topo2.topological_center

    def cut_out_circle(self, radius: float = 40) -> None:
        r"""
        Cuts out circle in both lattices
        """
        self._lattice1.spins = np.array(
            [self._lattice1.spins[idx] for idx, point in enumerate(self._lattice1.points) if
             np.linalg.norm(point[:2]) < radius])
        self._lattice1.points = np.array(
            [point for point in self._lattice1.points if np.linalg.norm(point[:2]) < radius])
        self._lattice2.spins = np.array(
            [self._lattice2.spins[idx] for idx, point in enumerate(self._lattice2.points) if
             np.linalg.norm(point[:2]) < radius])
        self._lattice2.points = np.array(
            [point for point in self._lattice2.points if np.linalg.norm(point[:2]) < radius])
        self._update_distance_shells()

    def rotate_to_minimum(self, angle_step: float = 5) -> Tuple[float, float]:
        r"""
        Rotates the lower lattice and compares with the upper lattice
        """
        total_angle = 0.0
        copy_lattice1 = copy.deepcopy(self._lattice1)
        dist_min = self._approx_geodesic_distance(self._lattice1, self._lattice2)
        angle_min = total_angle
        print(f'angle: {total_angle}, distance: {dist_min}')
        while total_angle < 360:
            total_angle = total_angle + angle_step
            copy_lattice1.points = self._rotate_lattice(latt=copy_lattice1, angle=angle_step)
            dist = self._approx_geodesic_distance(copy_lattice1, self._lattice2)
            print(f'angle: {total_angle}, distance: {dist}')
            if dist < dist_min:
                dist_min = dist
                angle_min = total_angle
        self._lattice1.points = self._rotate_lattice(self._lattice1, angle=angle_min)
        self._update_distance_shells()
        return dist_min, angle_min

    def _approx_geodesic_distance(self, latt1: CLattice, latt2: CLattice) -> float:
        r"""
        Geodesic distance between images with not identical lattices
        """
        dist_total = 0.0
        for (i_point, point) in enumerate(latt1.points):
            _, idx_closest = self._find_closest_point(distance_shells=self._distance_shells_latt2,
                                                      points=latt2.points[:, :2],
                                                      reference_point=point[:2])
            dp = np.dot(latt1.spins[i_point, :], latt2.spins[idx_closest, :])
            cp_n = np.linalg.norm(np.cross(latt1.spins[i_point, :], latt2.spins[idx_closest, :]))
            dist_total = dist_total + np.arctan2(cp_n, dp) ** 2
        return dist_total

    @staticmethod
    def _rotate_lattice(latt: CLattice, angle: float = 5) -> np.ndarray:
        r"""
        Rotates the lattice around the origin by an angle
        """
        angle_rad = angle * (np.pi / 180)
        rot_mat_z = np.array([[np.cos(angle_rad), -1.0 * np.sin(angle_rad), 0.0],
                              [np.sin(angle_rad), 1.0 * np.cos(angle_rad), 0.0],
                              [0.0, 0.0, 1.0]])
        return np.dot(rot_mat_z, latt.points.T).T
