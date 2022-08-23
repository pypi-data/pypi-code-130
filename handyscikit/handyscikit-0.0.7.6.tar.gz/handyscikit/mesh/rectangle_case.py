from ..common.advanced_print import cprint
from .core.mesh_2D import Mesh2D
from .core.mesh_base import meshing_time_recorder
import gmsh
import numpy as np


class RectangleCase(Mesh2D):
    def __init__(self, size, coordinate=[0, 0]):
        Mesh2D.__init__(self)

        if not gmsh.is_initialized(): gmsh.initialize()
        gmsh.model.occ.add_rectangle(coordinate[0], coordinate[1], 0, size[0], size[1])
        gmsh.model.occ.synchronize()

        self._dim = 2
        self._node_per_face = 2
        self._size = size
        self._structured_num = None

    def extract_horizontal_line_data(self, y_coordinate, error=1e-6):
        """
        Extract a horizontal line data. Data number equals to segment_num[0].
        Direction is left to right.
        :param y: Y coordinate. | float.
        :param result: Result field to be extracted.
        :return: Cell index. | list.
        """
        # todo: 改成numpy数组。
        data = []
        for i in range(self._cell_num):
            if abs(self._cell_center[i, 1] - y_coordinate) < error:
                data.append(i)

        try:
            assert len(data) != 0
        except:
             cprint("[handyscikit | Mesh]: There isn't a horizontal line data along input coordinate y.")
             exit(1)

        return data

    def extract_vertical_line_data(self, x_coordinate, error=1e-6):
         """
         Extract a vertical line data. Data number equals to segment_num[1].
         Direction is lower to upper.
         :param x: X coordinate. | float.
         :param result: Result field to be extracted.
         :return: Cell index. | list.
         """
         data = []
         for i in range(self._cell_num):
             if abs(self._cell_center[i, 0] - x_coordinate) < error:
                data.append(i)

         try:
            assert len(data) != 0
         except:
             cprint("[handyscikit | Mesh] There isn't a vertical line data along input coordinate x.")
             exit(1)

         return data

    @meshing_time_recorder
    def generate_structured(self, mesh_number, show_mesh=False):
        self._structured_num = mesh_number
        self._gmsh_element_type = 3  # 3 means quadrilateral.
        self._face_per_cell = 4
        self._node_per_cell = 4

        gmsh.model.mesh.set_transfinite_curve(1, mesh_number[0] + 1)  # down
        gmsh.model.mesh.set_transfinite_curve(2, mesh_number[1] + 1)  # right
        gmsh.model.mesh.set_transfinite_curve(3, mesh_number[0] + 1)  # up
        gmsh.model.mesh.set_transfinite_curve(4, mesh_number[1] + 1)  # left
        gmsh.model.mesh.set_transfinite_surface(1, "Left")
        gmsh.model.mesh.generate(2)
        gmsh.model.mesh.recombine()
        if show_mesh: gmsh.fltk.run()

        self._generate_topology()
        gmsh.clear()

    @meshing_time_recorder
    def generate_unstructured(self, size_list=None, show_mesh=False):
        self._gmsh_element_type = 2  # 2 means triangle.
        self._face_per_cell = 3
        self._node_per_cell = 3

        if size_list is not None:
            gmsh.model.mesh.set_size([(0, 1)], size_list[0])
            gmsh.model.mesh.set_size([(0, 2)], size_list[1])
            gmsh.model.mesh.set_size([(0, 3)], size_list[2])
            gmsh.model.mesh.set_size([(0, 4)], size_list[3])
        gmsh.model.mesh.generate(2)
        if show_mesh: gmsh.fltk.run()

        self._generate_topology()
        gmsh.clear()

    @property
    def boundary_down(self):
        return 1

    @property
    def boundary_right(self):
        return 2

    @property
    def boundary_up(self):
        return 3

    @property
    def boundary_left(self):
        return 4

    @property
    def size(self):
        return self._size

    @property
    def structured_num(self):
        return self._structured_num