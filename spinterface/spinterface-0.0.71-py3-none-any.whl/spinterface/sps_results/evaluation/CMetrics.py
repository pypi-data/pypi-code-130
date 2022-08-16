r"""
Module contains Metric classes for instances of spinaker spin lattices
"""
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.sps_results.evaluation.ISpinMetric import ISpinMetric
from spinterface.sps_results.evaluation.CMatchImages import CMatchImages
from spinterface.visualizations.algorithms.imagematching.CVisualImageMatching import CVisualImageMatching
import numpy as np
from pathlib import Path
from typing import List, Tuple, Union
from copy import deepcopy


class CGeodesicMetric(ISpinMetric):
    r"""
    Class for geodesic metric between spin images
    """

    def __init__(self) -> None:
        r"""

        """
        super().__init__()

    def distance(self, latt1: CLattice, latt2: CLattice, label1: str, label2: str) -> float:
        r"""
        :param latt1: Image 1
        :param latt2: Image 2
        :return: geodesic distance between images
        """
        dist_total = 0.0
        for (i_spin, spin) in enumerate(latt1.spins):
            dp = np.dot(spin, latt2.spins[i_spin, :])
            cp_n = np.linalg.norm(np.cross(spin, latt2.spins[i_spin, :]))
            dist_total = dist_total + np.arctan2(cp_n, dp) ** 2
        return np.sqrt(dist_total)

class CTotalMagMetric(ISpinMetric):
    r"""
    Class for metric of differences in total magnetization.
    """

    def distance(self, latt1: CLattice, latt2: CLattice, label1: str, label2: str) -> float:
        r"""
        :param latt1: Lattice Object 1
        :param latt2: Lattice Object 2
        :param label1: label of Lattice Object 1
        :param label2: label of Lattice Object 2
        :return: the difference in total magnetization between the lattices.
        """
        return abs(self._get_total_mag(latt1) - self._get_total_mag(latt2))

    def _get_total_mag(self, latt: CLattice) -> float:
        r"""
        :param latt: Lattice instance
        :return: the summation over the azimuthal angel
        """
        return float(np.sum(latt.spins[:, :]))

    def __init__(self) -> None:
        r"""
        Iniitializes the size metric
        """
        super().__init__()

    @staticmethod
    def _test_input_angle(angle_crit: float) -> float:
        r"""
        Test if angles lies in the desired intervall
        :param angle_crit: Angle criterium for spin to be considered out of plan (azimutal)
        :return: the tested angle, if not sufficient raises Value Error
        """
        if 0 < angle_crit < 360:
            return angle_crit
        else:
            raise ValueError('Angle criterium has to be in interval [0,360].')



class COopSizeMetric(ISpinMetric):
    r"""
    Class for metric of differences in size. The size is defined by the out of plane fraction of the spins (defined by
    a certain threshold.
    """

    def distance(self, latt1: CLattice, latt2: CLattice, label1: str, label2: str) -> float:
        r"""
        :param latt1: Lattice Object 1
        :param latt2: Lattice Object 2
        :param label1: label of Lattice Object 1
        :param label2: label of Lattice Object 2
        :return: the difference in size between the lattices.
        """
        #print('=================================================================================')
        #print(f'Number oop spins for {label1} = {self._get_number_oop_spin(latt1)}')
        #print(f'Number oop spins for {label2} = {self._get_number_oop_spin(latt2)}')
        #print(f'Distance between both = {abs(self._get_number_oop_spin(latt1) - self._get_number_oop_spin(latt2))}')
        if self._count_or_sum == 'count':
            return abs(self._get_number_oop_spin(latt1) - self._get_number_oop_spin(latt2))
        elif self._count_or_sum == 'sum':
            return abs(self._get_oop_angle_summated(latt1) - self._get_oop_angle_summated(latt2))

    def _get_number_oop_spin(self, latt: CLattice) -> int:
        r"""
        :param latt: Lattice instance
        :return: the number of oop spins
        """
        return np.count_nonzero((np.arccos(latt.spins[:, 2]) * 180.0 / np.pi) < self._angle_criterium)

    def _get_oop_angle_summated(self, latt: CLattice) -> float:
        r"""
        :param latt: Lattice instance
        :return: the summation over the azimuthal angel
        """
        return float(np.sum(np.arccos(latt.spins[:, 2]) * 180.0 / np.pi))

    def __init__(self, oop_angle_crit: float, count_or_sum: str = 'sum') -> None:
        r"""
        Iniitializes the size metric
        """
        self._angle_criterium = self._test_input_angle(oop_angle_crit)
        self._count_or_sum = count_or_sum
        super().__init__()

    @staticmethod
    def _test_input_angle(angle_crit: float) -> float:
        r"""
        Test if angles lies in the desired intervall
        :param angle_crit: Angle criterium for spin to be considered out of plan (azimutal)
        :return: the tested angle, if not sufficient raises Value Error
        """
        if 0 < angle_crit < 360:
            return angle_crit
        else:
            raise ValueError('Angle criterium has to be in interval [0,360].')



class CImageMatchingGeodesicMetric(ISpinMetric):
    r"""
    Class for geodesic metric between spin images after matching in terms of translation and rotation
    """

    def __init__(self, angle_step: float = 5, i_visu_image_matching: bool = False,
                 path_visu_image_matching: Path = Path.cwd(),
                 cams: Union[None, List[List[Tuple[float]]]] = None) -> None:
        r"""

        """
        self.i_visu_im = i_visu_image_matching
        self.p_visu_im = path_visu_image_matching
        self.cams = cams
        self.angle_step = angle_step
        super().__init__()

    def distance(self, latt1: CLattice, latt2: CLattice, label1: str, label2: str) -> float:
        r"""
        :param latt1:
        :param latt2:
        :return:
        """
        im = CMatchImages(lattice1=deepcopy(latt1), lattice2=deepcopy(latt2))
        if self.i_visu_im:
            visu_im = CVisualImageMatching()
            visu_im.cam = self.cams[0]
            visu_im.load_show_initial_lattices(im.lattice1, im.lattice2)
            visu_im(outpath=self.p_visu_im / (f'{label1}_{label2}_ini.png'))
        im.shift_to_center()
        if self.i_visu_im:
            visu_im.cam = self.cams[1]
            visu_im.load_show_initial_lattices(im.lattice1, im.lattice2)
            visu_im(outpath=self.p_visu_im / (f'{label1}_{label2}_shifted.png'))
        im.cut_out_circle(radius=18)
        if self.i_visu_im:
            visu_im.cam = self.cams[2]
            visu_im.load_show_cut_out(im.lattice1, im.lattice2)
            visu_im(outpath=self.p_visu_im / (f'{label1}_{label2}_circle.png'))
        dist, _ = im.rotate_to_minimum(angle_step=self.angle_step)
        if self.i_visu_im:
            visu_im.cam = self.cams[3]
            visu_im.load_show_cut_out(im.lattice1, im.lattice2)
            visu_im(outpath=self.p_visu_im / (f'{label1}_{label2}_rotated.png'))
        return dist
