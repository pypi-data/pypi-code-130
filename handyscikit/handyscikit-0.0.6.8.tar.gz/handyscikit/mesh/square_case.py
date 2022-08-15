from ..common.advanced_print import cprint
from .mesh_base import MeshBase
import gmsh
import time


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

        self._mesh_number = mesh_number
        self._size = size

        self._dim = 2
        self._face_per_cell = 4
        self._node_per_cell = 4
        self._node_per_face = 2
        self._gmsh_element_type = 3

    def synchronize(self):
        cprint("[handyscikit | Mesh] Meshing start.", color="purple")
        start_time = time.time()

        gmsh.model.mesh.set_transfinite_curve(1, self._mesh_number[0] + 1)  # down
        gmsh.model.mesh.set_transfinite_curve(2, self._mesh_number[1] + 1)  # right
        gmsh.model.mesh.set_transfinite_curve(3, self._mesh_number[0] + 1)  # up
        gmsh.model.mesh.set_transfinite_curve(4, self._mesh_number[1] + 1)  # left
        gmsh.model.mesh.set_transfinite_surface(1, "Left")
        gmsh.model.mesh.generate(2)
        gmsh.model.mesh.recombine()
        # todo: 可视化接口怎么设计？
        # gmsh.fltk.run()

        self._generate_topology_information()
        self._calculate_face_info_2D()

        gmsh.finalize()

        spend_time = time.time() - start_time
        cprint("[handyscikit | Mesh] Meshing finished and takes %f seconds." % (spend_time), color="purple")

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
    def mesh_number(self):
        return self._mesh_number

    @property
    def size(self):
        return self._size

    # todo: 回头这个功能要分离出去，为了快捷测试暂且先放在这里。
    def transfer_result_to_node_data(self, result, gradient, return_dtype=np.float64):
        """
        Some CFD methods are cell-centered.
        However, some visualization interface need result at node. So, this interface is used to transfer cell data to
        node data based on cell-centered result and gradient.
        :return:
        """

        cprint("[handyscikit | Mesh] Transfer cell data to node data.")

        # Calculate multi-value of each node.
        tmp = [[] for _ in range(self._node_num)]
        for i in range(self._cell_num):
            for j in self._cells[i]:
                tmp[j].append(result[i] + np.dot(self._nodes[j] - self._cell_center[i], gradient[i]))

        # Average upper.
        for i in range(self._node_num):
            tmp[i] = sum(tmp[i])/len(tmp[i])

        # Boundary correction.
        # todo: 2D corner condition.
        # todo: Low precision for variant Dirichlet boudnary.
        # todo: Pass periodic boundary condition.
        for i in range(self._face_num):
            if self._face_info[i, 0] == 1:
                tmp[self._faces[i, 0]] = self._face_info[i, 1]
                tmp[self._faces[i, 1]] = self._face_info[i, 1]

        return np.array(tmp, dtype=return_dtype)