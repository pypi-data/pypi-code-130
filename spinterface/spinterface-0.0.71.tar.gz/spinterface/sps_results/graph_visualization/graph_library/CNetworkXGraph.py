r"""
Backend for graph visualization in plotly
"""
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
from typing import List, Any, Tuple, Dict, Union
from spinterface.sps_results.graph_visualization.graph_library.utilities import distribute_around_node
from spinterface.sps_results.evaluation.CMetrics import CGeodesicMetric
from spinterface.inputs.lattice.CLattice import CLattice
import statistics as stat
import pickle


class CNetworkXGraph:
    r"""
    Backend class for graph visualization
    """

    def __init__(self, path_sps_calculation: Path = Path.cwd(), edge_distance: Union[str,float] = 'auto', i_create_or_load_graph: str = 'create', p_graph: Path = Path.cwd() / 'graph.pickle') -> None:
        r"""
        Initializes Graph Structure based on saddle point search calculation
        :param path_sps_calculation: directory for sps data
        :param edge_distance: edge distance for edges without defined length. Can be float or string. If "auto" the edge
        length will be defined upon the median distances in the escape stage.
        """
        self.path_sps_calculation = path_sps_calculation
        self.Natom = self._findoutnumberatoms()
        if i_create_or_load_graph == 'create':
            self.graph = nx.Graph()
            self._add_initial()
            self._add_displaced()
            self._add_escaped(infofilename='info_mf.dat')
            if type(edge_distance) == float:
                self._edge_distance = edge_distance
            else:
                if edge_distance == 'auto':
                    self._edge_distance = self._findoutmedian_edgelengths()
                else:
                    raise ValueError("edge distance descriptor not coded...")
            self._add_converged(infofilename_converge='info_mmf.dat', infofilename_reescape='info_reesc.dat')
            # save graph object to file
            pickle.dump(self.graph, open(p_graph, 'wb'))
        elif i_create_or_load_graph == 'load':
            # load graph object from file
            self.graph = pickle.load(open(p_graph, 'rb'))


    def _findoutmedian_edgelengths(self) -> float:
        r"""
        :return: The median of the existing edge lengths in the graph
        """
        edge_lengths = []
        for edge in self.graph.edges(data=True):
            edge_lengths.append(edge[2]["length"])
        return stat.median(edge_lengths)

    def _findoutnumberatoms(self) -> int:
        r"""
        Calculates the number of atoms from the SpinSTMi file
        """
        return pd.read_csv(self.path_sps_calculation / 'SpinSTMi.dat', sep=r'\s+').shape[0]

    def _findoutnumberofreescapes(self, directory: Path, infofilename_converge: str, infofilename_reescape: str) -> \
            Tuple[int, int]:
        r"""
        Finds out the number of info_mmf and number of info_reesc files
        :return: n_info_mmf, n_info_reesc
        """
        l_info_conv = infofilename_converge[:-4]
        l_info_reesc = infofilename_reescape[:-4]
        count_conv = 0
        count_reesc = 0
        for file in directory.iterdir():
            if str(file.stem).startswith(l_info_conv):
                count_conv += 1
            if str(file.stem).startswith(l_info_reesc):
                count_reesc += 1
        return count_conv, count_reesc

    def _add_initial(self) -> None:
        r"""
        Adds center node, which is the initial state
        """
        eval_range = [1, 9]
        try:
            df = pd.read_csv(self.path_sps_calculation / 'info_sps_eigenvalues.dat', sep=r'\s+')
            eigenvalues = np.array(
                [df[f'eig00{eval}'].to_numpy()[0] for eval in range(eval_range[0], eval_range[1] + 1)])
            spinfile = self.path_sps_calculation / (self.path_sps_calculation / df['spin_file'].to_numpy()[0]).stem
            self.graph.add_node("Initial", eigenvalues=eigenvalues, pos=(0, 0), stage="ini", text="Initial State",
                                file=spinfile, level=0)
        except FileNotFoundError:
            print('Graph-WARNING: Did not find the eigenvalue file for the initial state. Info will be missing.')
            print('Graph-WARNING: Also initial visualization will be missing.')
            self.graph.add_node("Initial", pos=(0, 0), text="Initial State", stage="ini", level=0)

    def _add_displaced(self) -> None:
        r"""
        Adds the displaced nodes
        """
        # draw nodes
        df = pd.read_csv(self.path_sps_calculation / 'info_sps_disp.dat', sep=r'\s+')
        l_folders_sps_attempts = df['folder'].to_numpy()
        l_files_sps_attempts = df['spin_file'].to_numpy()
        # distribute displaced states around a circle
        arc = 2 * np.pi / len(df['DISPKEY'].to_numpy())
        for index, dispkey in enumerate(df['DISPKEY'].to_numpy()):
            df_disp = pd.read_csv(self.path_sps_calculation / l_folders_sps_attempts[index] / 'info_displaced.dat',
                                  sep=r'\s+')
            geo_dist_to_initial = df_disp['geodesic_distance_per_atom'].to_numpy()[0]
            position = (np.cos(index * arc) * geo_dist_to_initial, np.sin(index * arc) * geo_dist_to_initial)

            l_p_evecfile = self.path_sps_calculation / l_folders_sps_attempts[index] / str(
                (self.path_sps_calculation / l_files_sps_attempts[index]).stem).replace('spin', 'evec')
            l_p_spinfile = self.path_sps_calculation / l_folders_sps_attempts[index] / (
                    self.path_sps_calculation / l_files_sps_attempts[index]).stem
            self.graph.add_node(dispkey, eig0=df_disp['eig0'].to_numpy()[0], eig1=df_disp['eig1'].to_numpy()[0],
                                text=dispkey, pos=position, geodist=geo_dist_to_initial, file=l_p_spinfile,
                                evecfile=l_p_evecfile, stage='displace',level=1)
            self.graph.add_edge("Initial", dispkey, length=geo_dist_to_initial)

    def _add_escaped(self, infofilename: str = 'info_mf.dat', angle_opening: float = 180) -> None:
        r"""
        Adds the escaped nodes
        """
        df = pd.read_csv(self.path_sps_calculation / 'info_sps_esc.dat', sep=r'\s+')
        l_dispkeys_unique = set(df['DISPKEY'].to_numpy())
        # create metric to calculate geodesic distances
        geo_metric = CGeodesicMetric()
        # iterate over displaced nodes:
        for dispkey in l_dispkeys_unique:
            df_filtered = df[df['DISPKEY'] == dispkey]
            dispnode_pos = [dnode for dnode in self.get_displaced() if dnode[0] == dispkey][0][1].get('pos')
            dispnode_file = [dnode for dnode in self.get_displaced() if dnode[0] == dispkey][0][1].get('file')
            latt_disp = CLattice(source='STM', path=Path(str(dispnode_file) + '.dat'))
            esc_folders = df_filtered['folder'].to_numpy()
            nodenames = []
            geodists_total_travelled, geodist_total = [], []
            esckeys = []
            eigenvalues = []
            files = []
            for index, esckey in enumerate(df_filtered['ESCKEY'].to_numpy()):
                nodenames.append(dispkey + esckey)
                esckeys.append(esckey)
                df_esc = pd.read_csv(self.path_sps_calculation / esc_folders[index] / infofilename, sep=r'\s+')
                files.append(self.path_sps_calculation / esc_folders[index] / 'spin_mf_end')
                latt_esc = CLattice(source='STM', path=Path(str(files[index]) + '.dat'))
                eigcols = [colheader for colheader in df_esc.columns if colheader.startswith('eig0')]
                last_row = df_esc.iloc[-1]
                geodist_total.append(
                    geo_metric.distance(latt_disp, latt_esc, label1=dispkey, label2=nodenames[index]) / self.Natom)
                geodists_total_travelled.append(float(last_row['distance_total'] / self.Natom))
                eigenvalues.append(
                    np.array([float(last_row[eigcol]) for eigcol in eigcols if not last_row[eigcol] == '-']))
            pos_esc, dir_esc = distribute_around_node(dispnode_pos, opening_angle=180,
                                             distances_child_parent=geodist_total)
            for index, node in enumerate(nodenames):
                self.graph.add_node(node, dispkey=dispkey, esckey=esckeys[index], text=esckeys[index],
                                    pos=pos_esc[index], stage='escape', geodist=geodist_total[index],
                                    geodist_travelled=geodists_total_travelled[index],
                                    stagger=geodists_total_travelled[index] / geodist_total[index],
                                    eigenvalues=eigenvalues[index], file=files[index], direction = dir_esc[index], level=2)
                self.graph.add_edge(dispkey, node, length=geodist_total[index])

    def _add_converged(self, infofilename_converge: str = 'info_mmf.dat',
                       infofilename_reescape: str = 'info_reesc.dat') -> None:
        r"""
        Adds the converged/ re-escaped nodes to the graph
        :param infofilename: name of the info files
        """
        df = pd.read_csv(self.path_sps_calculation / 'info_sps_conv.dat', sep=r'\s+')
        l_folders = df['folder'].to_numpy()
        l_esckeys = df['ESCKEY'].to_numpy()
        geo_metric = CGeodesicMetric()
        for index, dispkey in enumerate(df['DISPKEY'].to_numpy()):
            n_mmf, n_reesc = self._findoutnumberofreescapes(directory=self.path_sps_calculation / str(l_folders[index]),
                                                            infofilename_converge=infofilename_converge,
                                                            infofilename_reescape=infofilename_reescape)
            # the calculations where during an converge-calculation the number of iterations exceeded are not here (since
            # not included in sps_info_conv.dat...
            # -> therefore n_mmf = n_reesc + 1
            parent_node_name = dispkey + l_esckeys[index]
            parent_node = self.get_node(parent_node_name)
            latt_parent = CLattice(source='STM', path=Path(str(parent_node[1]['file']) + '.dat'))
            parent_pos = np.array([parent_node[1]['pos'][0], parent_node[1]['pos'][1]])
            parent_direction = parent_node[1]['direction']
            for i_mmf in range(n_mmf):
                df_conv = pd.read_csv(
                    self.path_sps_calculation / l_folders[index] / f'{infofilename_converge[:-4]}{i_mmf}.dat', sep=r'\s+')
                last_row = df_conv.iloc[-1]
                eigcols = [colheader for colheader in df_conv.columns if colheader.startswith('eig0')]
                eigenvalues = np.array([float(last_row[eigcol]) for eigcol in eigcols if not last_row[eigcol] == '-'])
                if i_mmf == n_mmf - 1:
                    # converged calculation
                    suffix = 'conv'
                    node = dispkey + l_esckeys[index] + suffix
                    stage = 'converge'
                    latt_node = CLattice(source='STM',
                                         path=self.path_sps_calculation / l_folders[index] / 'spin_mmf_end.dat')
                    file = self.path_sps_calculation / l_folders[index] / 'spin_mmf_end'
                    l_distance_to_parent = geo_metric.distance(latt_parent, latt_node, label1=parent_node_name,
                                                               label2=node) / self.Natom
                    edge_length = l_distance_to_parent
                    l_distance_travelled = df_conv['geodist_per_atom'].sum()
                else:
                    # re-entered calculation
                    suffix = f'reen{i_mmf}'
                    node = dispkey + l_esckeys[index] + suffix
                    stage = 'reentered'
                    try:
                        latt_node = CLattice(source='STM', path=self.path_sps_calculation / l_folders[
                            index] / f'spin_reen{i_mmf}.dat')
                        file = self.path_sps_calculation / l_folders[index] / f'spin_reen{i_mmf}.dat'
                        l_distance_to_parent = geo_metric.distance(latt_parent, latt_node, label1=parent_node_name,
                                                                   label2=node) / self.Natom
                        l_distance_travelled = df_conv['geodist_per_atom'].sum()
                        edge_length = l_distance_to_parent
                    except FileNotFoundError:
                        print(
                            f'WARNING: re-entered spin file not found. Cannot calculate geodesic distance to parent ({l_folders[index]})')
                        print(f'WARNING: will read the cumulated geodesic distance.')
                        l_distance_travelled = df_conv['geodist_per_atom'].sum()
                        l_distance_to_parent = None
                        edge_length = self._edge_distance
                        latt_node = None
                        file = None
                if l_distance_to_parent is None or l_distance_travelled is None:
                    stagger = None
                else:
                    stagger = l_distance_travelled / l_distance_to_parent

                pos = parent_pos + edge_length * parent_direction
                self.graph.add_node(node, dispkey=dispkey, esckey=l_esckeys[index], stage=stage, file=file,
                                    pos=(pos[0], pos[1]), geodist=l_distance_to_parent,
                                    geodist_travelled=l_distance_travelled, text=suffix,
                                    stagger= stagger, eigenvalues=eigenvalues, level=4+2*i_mmf-1)
                self.graph.add_edge(parent_node_name, node, length=edge_length)
                if i_mmf == n_mmf - 1:
                    # no need for re-escape calculation
                    break
                # define parents:
                parent_node_name = node
                latt_parent = latt_node
                parent_pos = pos
                # re-escape calculation
                suffix = f'reesc{i_mmf}'
                node = dispkey + l_esckeys[index] + suffix
                stage = 'reescape'
                df_reesc = pd.read_csv(
                    self.path_sps_calculation / l_folders[index] / f'{infofilename_reescape[:-4]}{i_mmf}.dat', sep=r'\s+')
                last_row = df_conv.iloc[-1]
                eigcols = [colheader for colheader in df_conv.columns if colheader.startswith('eig0')]
                eigenvalues = np.array([float(last_row[eigcol]) for eigcol in eigcols if not last_row[eigcol] == '-'])
                latt_reesc = CLattice(source='STM', path=self.path_sps_calculation / l_folders[
                    index] / f'spin_reesc{i_mmf}_end.dat')
                file = self.path_sps_calculation / l_folders[index] / f'spin_reesc{i_mmf}_end'
                if latt_parent is None:
                    try:
                        l_distance_travelled = df_reesc['geodist_per_atom'].sum()
                        print('WARNING: Re-entered image does not exist. Will use cumulated geodesic distance.')
                        l_distance_to_parent = None
                        edge_length = self._edge_distance
                    except KeyError:
                        print('WARNING: Re-entered image does not exist and no information about cumulated geodesic'
                              'distance. Distance will be the same as previously')
                        l_distance_travelled = None
                        l_distance_to_parent = None
                        edge_length = self._edge_distance
                else:
                    l_distance_to_parent = geo_metric.distance(latt_parent, latt_reesc, label1=parent_node_name,
                                                               label2=node) / self.Natom
                    edge_length = l_distance_to_parent
                pos = parent_pos + edge_length * parent_direction
                if l_distance_travelled is None or l_distance_to_parent:
                    stagger = None
                else:
                    stagger = l_distance_travelled / l_distance_to_parent
                self.graph.add_node(node, dispkey=dispkey, esckey=l_esckeys[index], stage=stage, file=file,
                                    pos=(pos[0], pos[1]), geodist=l_distance_to_parent,
                                    geodist_travelled=l_distance_travelled, text=suffix,
                                    stagger=stagger, eigenvalues=eigenvalues, level=4+2*i_mmf)
                self.graph.add_edge(parent_node_name, node, length=edge_length)
                # define parents for next iteration:
                parent_node_name = node
                latt_parent = latt_reesc
                parent_pos = pos


    def get_initial(self) -> List[Any]:
        r"""
            :return: The List with the initial state
            """
        return [node for node in self.graph.nodes(data=True) if node[1].get('stage') == "ini"]

    def get_displaced(self) -> List[Any]:
        r"""
        :return: The List with the displaced states
        """
        return [node for node in self.graph.nodes(data=True) if node[1].get('stage') == 'displace']

    def get_node(self, nodekey) -> Tuple[Any, Dict[Any, Any]]:
        r"""
        :return: A specific node
        """
        return [node for node in self.graph.nodes(data=True) if node[0] == nodekey][0]

    def get_escaped(self) -> List[Any]:
        r"""
            :return: The List with the escaped states
            """
        return [node for node in self.graph.nodes(data=True) if node[1].get('stage') == 'escape']
