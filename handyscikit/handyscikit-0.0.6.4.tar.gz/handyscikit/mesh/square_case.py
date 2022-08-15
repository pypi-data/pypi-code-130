from .mesh_base import MeshBase
import gmsh


# todo: gmsh 有getBaryCenter的接口。（闲着没事的时候再升级）
# todo: 有哪些边界条件没指定的检测。(闲着没事的时候再升级)
# todo: 分出两个case，一个是square case, 一个是rectangle case。（遇到Rectangle case的时候再做）
# todo: 给Mesh分出2D和3D两个版本（这个后期3D升级的时候再做）
class SquareCase(MeshBase):
    def __init__(self, size, mesh_number, coordinate=[0, 0]):
        MeshBase.__init__(self)

        gmsh.initialize()
        gmsh.model.occ.addRectangle(coordinate[0], coordinate[1], 0, size[0], size[1])
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.set_transfinite_curve(1, mesh_number[0]+1)  # down
        gmsh.model.mesh.set_transfinite_curve(2, mesh_number[1]+1)  # right
        gmsh.model.mesh.set_transfinite_curve(3, mesh_number[0]+1)  # up
        gmsh.model.mesh.set_transfinite_curve(4, mesh_number[1]+1)  # left
        gmsh.model.mesh.set_transfinite_surface(1, "Left")

        self._dim = 2
        self._face_per_cell = 4
        self._node_per_cell = 4
        self._node_per_face = 2
        self._gmsh_element_type = 3

    def synchronize(self):
        gmsh.model.mesh.generate(2)
        gmsh.model.mesh.recombine()
        # gmsh.fltk.run()

        self._generate_topology_information()
        self._calculate_face_info_2D()

        gmsh.finalize()

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
