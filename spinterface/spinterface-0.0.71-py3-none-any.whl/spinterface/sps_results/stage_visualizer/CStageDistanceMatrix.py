r"""
Module contains class calculating the distance matrix for the displace stage
"""
from pathlib import Path
from spinterface.sps_results.stage_visualizer.IStageDistanceMatrix import IStageDistanceMatrix
import pandas as pd
from typing import Union, Tuple, List


class CStageDistanceMatrix(IStageDistanceMatrix):
    r"""
    Class for defining the distance matrix for saddle point search stages
    """

    def __init__(self, i_initial: bool = False, i_displaced: bool = False, i_escaped: bool = False,
                 info_file_displace: Union[Path, None] = None,
                 info_file_escape: Union[Path, None] = None, file_initial: Union[Path, None] = None, metric: str = 'geodesic') -> None:
        r"""
        Set up the distance matrix and decides on the included configurations
        """
        if all([not i_initial, not i_displaced, not i_escaped]):
            raise ValueError('Cannot build distance matrix for no defined stage')
        if info_file_displace is None:
            self._if_disp = Path.cwd() / 'info_sps_disp.dat'
        else:
            self._if_disp = info_file_displace
        self.parent_directory = Path(info_file_displace).parent
        if file_initial is None:
            self._if_ini = self.parent_directory / 'SpinSTMi.dat'
        else:
            self._if_ini = file_initial
        if info_file_escape is None:
            self._if_esc = self.parent_directory / 'info_sps_esc.dat'
        else:
            self._if_esc = info_file_escape

        paths, labels = [], []
        if i_initial:
            paths.append(self._if_ini)
            labels.append('initial')
        if i_displaced:
            l, p = self._load_displace()
            paths.extend(p)
            labels.extend(l)
        if i_escaped:
            l, p = self._load_escape()
            paths.extend(p)
            labels.extend(l)
        super().__init__(paths, labels, metric=metric)

    def _load_displace(self) -> Tuple[List[str], List[Path]]:
        r"""
        Loads the displace image
        :return: the labels and the source files
        """
        df = pd.read_csv(self._if_disp, sep=r'\s+')
        return df['DISPKEY'].to_list(), [self.parent_directory / sf for sf in df['spin_file'].to_list()]

    def _load_escape(self) -> Tuple[List[str], List[Path]]:
        r"""
        Loads the escape images
        :return: the labels and the source files
        """
        df = pd.read_csv(self._if_esc, sep=r'\s+')
        return [dkey + str(df['ESCKEY'][index]) for (index, dkey) in enumerate(df['DISPKEY'].to_list())], [
            self.parent_directory / sf for sf in df['spin_file'].to_list()]
