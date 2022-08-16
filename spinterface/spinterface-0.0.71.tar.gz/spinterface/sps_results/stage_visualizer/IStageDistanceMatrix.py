r"""
Abstract class for calculating the distance matrix for different stages of the saddle point search.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.sps_results.evaluation.ISpinMetric import ISpinMetric
from spinterface.sps_results.evaluation.CMetrics import CGeodesicMetric, CImageMatchingGeodesicMetric, COopSizeMetric, CTotalMagMetric


class IStageDistanceMatrix(ABC):
    r"""
    Abstract Class for Distance Matrix of Stage
    """

    def __init__(self, files: List[Path], labels: List[str], metric: str = 'geodesic') -> None:
        r"""
        Initializes the Stage Distance Matrix
        :param files: sources for the spin images
        :param labels: labels for the spin images
        :param metric: Decider string for metric used
        """
        self._files = files
        self._labels = labels
        self._images = self._load_images()
        if metric == 'geodesic':
            self._metric = CGeodesicMetric()
        elif metric == 'geodesic_im':
            """cams = [[(104.20529619101353, 82.83625566006411, 33.530273771277415),
               (24.49999923631549, 0.0, 7.5),
               (-0.16798883722958197, -0.14477384756924983, 0.9751001403067527)],[(70.17602418323614, 62.220135990644344, 28.715096054494563),
               (10.094992775288723, 13.421974162151864, 6.581522135537),
               (-0.210469298624799, -0.1769563932087938, 0.9614515636468226)],[(41.083601166346014, 44.75891291756833, 40.83861541951548),
               (7.533239149799918, 10.581694947508504, 13.826171205352829),
               (-0.35003485603229234, -0.34477603838904014, 0.8709793814524036)],[(41.083601166346014, 44.75891291756833, 40.83861541951548),
               (7.533239149799918, 10.581694947508504, 13.826171205352829),
               (-0.35003485603229234, -0.34477603838904014, 0.8709793814524036)] ]"""
            cams=[None]*4
            self._metric = CImageMatchingGeodesicMetric(angle_step=5, i_visu_image_matching=False, path_visu_image_matching=Path.cwd(),cams=cams)
        elif metric == 'oop_size':
            self._metric = COopSizeMetric(oop_angle_crit=5)
        elif metric == 'total_mag':
            self._metric = CTotalMagMetric()
        else:
            raise ValueError(f'ERROR: Given metric: {metric} not coded...')

    def _load_images(self) -> List[CLattice]:
        r"""
        :return: List of Spin Lattice objects based on source files
        """
        return [CLattice(source='STM', path=f, N1=50, N2=50) for f in self._files]

    @property
    def images(self) -> List[CLattice]:
        r"""
        :return:
        """
        return self._images

    @property
    def labels(self) -> List[str]:
        r"""
        :return:
        """
        return self._labels

    @property
    def metric(self) -> ISpinMetric:
        r"""
        :return: The metric used. Can be used to calculate distance matrices and  so on.
        """
        return self._metric
