r"""
Module contains class to visualize the process of image matching
"""
from pathlib import Path
import numpy as np
import pandas as pd
from spinterface.inputs.lattice.CLattice import CLattice
import pyvista as pv
from typing import Union, List, Tuple
from spinterface.visualizations.lattices.utilities import get_colormap, HSVtoRGB


class CVisualImageMatching:
    r"""
    Class for visualizing the process of image matching
    """

    def __init__(self, color_background: str = 'white', transparent_background: bool = True,
                 cam: Union[List[Tuple[float, float, float]], None] = None):
        r"""

        """
        self.text_objects = []
        self.color_background = color_background
        self.transparent_background = transparent_background
        self.cam = cam
        self._i_settings = {'initial': False, 'cut_out': False}

    def _get_colors(self, plotspins: np.ndarray) -> np.ndarray:
        r"""
        Assigns each spin a color calculate by bivariat HSV

        Args:
            plotspins(np.ndarray): array of spins
        Returns:
            2D np-array of rgb's
        """
        colors = []
        for spin in plotspins:
            colors.append(HSVtoRGB(spin, saturation=1.0))
        return np.array(colors)

    def _configureplotter(self) -> None:
        r"""
        Configures the plotter object
        """
        pv.set_plot_theme("ParaView")
        pv.rcParams['transparent_background'] = self.transparent_background
        self.plotter.set_background(self.color_background)

        def cam() -> None:
            print('Camera postion: ', self.plotter.camera_position)

        self.plotter.add_key_event('c', cam)

    def _make_plotter(self, offscreen: bool = False) -> None:
        r"""
        Creates the plotter. Will be re-created when saving the image
        :param offscreen: bool for saving the image
        """
        self.plotter = pv.Plotter(off_screen=offscreen, lighting='three lights')
        self._configureplotter()
        self.plotter.camera_position = self.cam
        if not self._check_settings():
            raise ValueError('Only one stage can be loaded....')
        if self._i_settings['initial']:
            self._visu_initial()
        elif self._i_settings['cut_out']:
            self._visu_cutout()

    def _check_settings(self) -> bool:
        r"""
        Checks if one and only one initialize technique is loaded.
        """
        return list(self._i_settings.values()).count(True) == 1

    def load_show_initial_lattices(self, latt1: CLattice, latt2: CLattice, dist: float = 15) -> None:
        r"""
        Set the setting to show initial not shifted, not rotated lattices
        """
        self._latt1 = latt1
        self._latt2 = latt2
        self._initial_setting_distance = dist
        if latt1.nlayer != 1 or latt2.nlayer != 1:
            raise ValueError('Visualization of Image Matching not coded for Multilayers')
        for key in self._i_settings.keys():
            self._i_settings[key] = False
        self._i_settings['initial'] = True

    def load_show_cut_out(self, latt1: CLattice, latt2: CLattice, dist: float = 15) -> None:
        r"""
        """
        self._latt1 = latt1
        self._latt2 = latt2
        self._cutout_setting_distance = dist
        for key in self._i_settings.keys():
            self._i_settings[key] = False
        self._i_settings['cut_out'] = True

    def create_and_show(self) -> None:
        r"""
        Creates the plotter and shows it.
        """
        print('Look what you have done.......')
        print('to get current cam-position press key c')
        self._make_plotter()
        self.plotter.show()

    def _visu_initial(self) -> None:
        r"""
        Adds the elements to the plotter necessary for the initial visualization
        """
        self.PD_points1 = pv.PolyData(self._latt1.points[:, :])
        plot_colors1 = self._get_colors(plotspins=self._latt1.spins)
        self.PD_points1['colors'] = plot_colors1
        self.surf1 = self.PD_points1.delaunay_2d()
        # shift second points slightly
        self.PD_points2 = pv.PolyData(self._latt2.points[:, :] + np.array([0.0, 0.0, self._initial_setting_distance]))
        plot_colors2 = self._get_colors(plotspins=self._latt2.spins)
        self.PD_points2['colors'] = plot_colors2
        self.surf2 = self.PD_points2.delaunay_2d()

        self.plotter.add_mesh(self.surf1, scalars="colors", rgb=True, show_scalar_bar=False)
        self.plotter.add_mesh(self.PD_points1, point_size=5, render_points_as_spheres=True, show_scalar_bar=False)

        self.plotter.add_mesh(self.surf2, scalars="colors", rgb=True, show_scalar_bar=False)
        self.plotter.add_mesh(self.PD_points2, point_size=5, render_points_as_spheres=True, show_scalar_bar=False)

        self.build_bounding_box(self._latt1, color='firebrick', z=0)
        self.build_bounding_box(self._latt2, color='g', z=self._initial_setting_distance)
        self.build_topology_information(self._latt1, z=0)
        self.build_topology_information(self._latt2, z=self._initial_setting_distance)

    def _visu_cutout(self) -> None:
        r"""
        """
        self.PD_points1 = pv.PolyData(self._latt1.points[:, :])
        plot_colors1 = self._get_colors(plotspins=self._latt1.spins)
        self.PD_points1['colors'] = plot_colors1
        self.surf1 = self.PD_points1.delaunay_2d()
        # shift second points slightly
        self.PD_points2 = pv.PolyData(self._latt2.points[:, :]+ np.array([0.0, 0.0, self._cutout_setting_distance]))
        plot_colors2 = self._get_colors(plotspins=self._latt2.spins)
        self.PD_points2['colors'] = plot_colors2
        self.surf2 = self.PD_points2.delaunay_2d()

        self.plotter.add_mesh(self.surf1, scalars="colors", rgb=True, show_scalar_bar=False)
        self.plotter.add_mesh(self.PD_points1, point_size=5, render_points_as_spheres=True, show_scalar_bar=False)

        self.plotter.add_mesh(self.surf2, scalars="colors", rgb=True, show_scalar_bar=False)
        self.plotter.add_mesh(self.PD_points2, point_size=5, render_points_as_spheres=True, show_scalar_bar=False)

        pv_center_ax = pv.Cylinder(
            center=self._latt1.midpoint + np.array([0.0, 0.0, self._cutout_setting_distance / 2]),
            direction=np.array([0.0, 0.0, 1.0]),
            radius=0.3, height=self._cutout_setting_distance * 2)
        self.plotter.add_mesh(pv_center_ax, color='k')

    def build_topology_information(self, latt: CLattice, z: float) -> None:
        r"""
        """
        center = pv.Sphere(radius=1.0, center=latt.topologies[0].topological_center + np.array([0.0, 0.0, z]))
        self.plotter.add_mesh(center, color='k')
        pv_topo_ax = pv.Cylinder(center=latt.topologies[0].topological_center + np.array([0.0, 0.0, z]),
                                 direction=np.array([0.0, 0.0, 1.0]),
                                 radius=0.3, height=self._initial_setting_distance)
        self.plotter.add_mesh(pv_topo_ax, color='k')

    def build_bounding_box(self, latt: CLattice, color: str, z: float) -> None:
        r"""
        """
        edges = [np.array([np.max([latt.points[:, 0]]), np.max([latt.points[:, 1]])]), np.array(
            [np.max([latt.points[:, 0]]), np.min([latt.points[:, 1]])]), np.array(
            [np.min([latt.points[:, 0]]), np.max([latt.points[:, 1]])]), np.array(
            [np.min([latt.points[:, 0]]), np.min([latt.points[:, 1]])])]
        d1 = np.linalg.norm(edges[0] - edges[1])
        d2 = np.linalg.norm(edges[0] - edges[2])
        # first build the plane
        plane = pv.Plane(center=latt.midpoint + np.array([0.0,0.0,z]), direction=np.array([0.0, 0.0, 1.0]), i_size=d2, j_size=d1,
                         i_resolution=2, j_resolution=2)
        self.plotter.add_mesh(plane, color=color, opacity=0.5)
        for edge in edges:
            pv_edge = pv.Cylinder(center=np.array([edge[0], edge[1], z]),
                                  direction=np.array([0.0, 0.0, 1.0]),
                                  radius=0.1, height=self._initial_setting_distance)
            self.plotter.add_mesh(pv_edge, color=color)
        pv_center_ax = pv.Cylinder(center=latt.midpoint+ np.array([0.0,0.0,z]),
                                   direction=np.array([0.0, 0.0, 1.0]),
                                   radius=0.3, height=self._initial_setting_distance * 2)
        self.plotter.add_mesh(pv_center_ax, color=color)

    def add_text(self, **kwargs):
        r"""
        """
        self.plotter.add_text(**kwargs)
        self.text_objects.append(dict(**kwargs))

    def __call__(self, outpath: Path = Path.cwd() / 'spin.png', resolution: Tuple[float, float] = (4000, 4000)) -> None:
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
            resolution: size of the created immage
        """
        self._make_plotter(offscreen=True)
        for text_object in self.text_objects:
            self.plotter.add_text(**text_object)
        self.plotter.window_size = [resolution[0], resolution[1]]
        self.plotter.screenshot(str(outpath))
