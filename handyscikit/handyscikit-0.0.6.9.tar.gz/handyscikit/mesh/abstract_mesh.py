from handyscikit.common.advanced_print import cprint
import numpy as np
import time

# Content: Dim | Node per cell | Node per face | Face per cell.
mesh_type_param = {"square": [2, 4, 2, 4]}


class AbstractMeshBase:
    def __init__(self, type, node_num, face_num, cell_num, float_dtype):
        print("[handyscikit] Mesh Info: Meshing start.")
        self._cell_num = cell_num
        self._dim = mesh_type_param[type][0]
        self._face_num = face_num
        self._face_per_cell = mesh_type_param[type][3]
        self._node_num = node_num
        self._node_per_cell = mesh_type_param[type][1]
        self._node_per_face = mesh_type_param[type][2]

        self._cell_cell = np.zeros([self._cell_num, self._face_per_cell], dtype=np.int32)
        self._cell_volume = np.zeros([self._cell_num], dtype=float_dtype)
        self._cell_face = np.zeros([self._cell_num, self._face_per_cell], dtype=np.int32)
        self._cell_coord = np.zeros([self._cell_num, self._dim], dtype=float_dtype)
        self._cells = np.zeros([self._cell_num, self._node_per_cell], dtype=np.int32)
        self._face_cell = np.full([self._face_num, 2], fill_value=-1, dtype=np.int32)
        self._face_center = np.zeros([self._face_num, self._dim], dtype=float_dtype)
        self._face_length = np.zeros([self._face_num], dtype=float_dtype)
        self._face_mark = np.zeros([self._face_num], dtype=np.int32)
        self._face_type = np.zeros([self._face_num, 3], dtype=float_dtype)
        self._face_norm = np.zeros([self._face_num, self._dim], dtype=float_dtype)
        self._faces = np.zeros([self._face_num, 2], dtype=np.int32)
        self._nodes = np.zeros([self._node_num, self._dim], dtype=float_dtype)

        self._boundary_condition_setting_list = []
        self._time_start = time.time()

    def _cal_cell_cell(self):
        cprint("[handyscikit] Mesh Error: Undefine cal cell cell function.")
        exit(7)

    def _cal_cell_coord(self):
        cprint("[handyscikit] Mesh Error: Undefine cal cell coord function.")
        exit(7)

    def _cal_cell_face(self):
        cprint("[handyscikit] Mesh Error: Undefine cal cell face function.")
        exit(7)

    def _cal_cell_volume(self):
        cprint("[handyscikit] Mesh Error: Undefine cal cell volume function.")
        exit(7)

    def _cal_cells(self):
        cprint("[handyscikit] Mesh Error: Undefine cal cells function.")
        exit(7)

    def _cal_face_cell(self):
        cprint("[handyscikit] Mesh Error: Undefine cal face cell function.")
        exit(7)

    def _cal_face_center(self):
        cprint("[handyscikit] Mesh Error: Undefine cal face center function.")
        exit(7)

    def _cal_face_length(self):
        cprint("[handyscikit] Mesh Error: Undefine cal face length function.")
        exit(7)

    def _cal_face_mark(self):
        cprint("[handyscikit] Mesh Error: Undefine cal face mark function.")
        exit(7)

    def _cal_face_norm(self):
        cprint("[handyscikit] Mesh Error: Undefine cal face norm function.")
        exit(7)

    def _cal_faces(self):
        cprint("[handyscikit] Mesh Error: Undefine cal faces function.")
        exit(7)

    def _cal_nodes(self):
        cprint("[handyscikit] Mesh Error: Undefine cal nodes function.")
        exit(7)

    def _check_boundary_condition_setting(self):
        if 0 in self._boundary_condition_setting_list:
            cprint("[handyscikit] Mesh Error: There are unset boundary.")
            exit(1)

    def _generate(self):
        self._cal_nodes()
        self._cal_faces()
        self._cal_cells()

        self._cal_cell_cell()
        self._cal_cell_face()
        self._cal_face_cell()

        self._cal_face_center()
        self._cal_face_length()
        self._cal_cell_coord()
        self._cal_cell_volume()
        self._cal_face_norm()

        self._cal_face_mark()


class AbstractMesh(AbstractMeshBase):
    def __init__(self, type, node_num, face_num, cell_num, float_dtype):
        AbstractMeshBase.__init__(self, type, node_num, face_num, cell_num, float_dtype)

    @property
    def cell_cell(self):
        self._check_boundary_condition_setting()
        return self._cell_cell

    @property
    def cell_coord(self):
        self._check_boundary_condition_setting()
        return self._cell_coord

    @property
    def cell_face(self):
        self._check_boundary_condition_setting()
        return self._cell_face

    @property
    def cell_num(self):
        self._check_boundary_condition_setting()
        return self._cell_num

    @property
    def cell_volume(self):
        self._check_boundary_condition_setting()
        return self._cell_volume

    @property
    def cells(self):
        self._check_boundary_condition_setting()
        return self._cells

    @property
    def dim(self):
        self._check_boundary_condition_setting()
        return self._dim

    @property
    def face_cell(self):
        self._check_boundary_condition_setting()
        return self._face_cell

    @property
    def face_center(self):
        self._check_boundary_condition_setting()
        return self._face_center

    @property
    def face_length(self):
        self._check_boundary_condition_setting()
        return self._face_length

    @property
    def face_mark(self):
        self._check_boundary_condition_setting()
        return self._face_mark

    @property
    def face_norm(self):
        self._check_boundary_condition_setting()
        return self._face_norm

    @property
    def face_type(self):
        self._check_boundary_condition_setting()
        return self._face_type

    @property
    def face_num(self):
        self._check_boundary_condition_setting()
        return self._face_num

    @property
    def face_per_cell(self):
        self._check_boundary_condition_setting()
        return self._face_per_cell

    @property
    def faces(self):
        self._check_boundary_condition_setting()
        return self._faces

    @property
    def node_num(self):
        self._check_boundary_condition_setting()
        return self._node_num

    @property
    def node_per_cell(self):
        self._check_boundary_condition_setting()
        return self._node_per_cell

    @property
    def node_per_face(self):
        self._check_boundary_condition_setting()
        return self._node_per_face

    @property
    def nodes(self):
        self._check_boundary_condition_setting()
        return self._nodes

    def transfer_result_to_node_data(self, result, gradient, return_dtype=np.float64):
        """
        Some CFD methods are cell-centered.
        However, some visualization interface need result at node. So, this interface is used to transfer cell data to
        node data based on cell-centered result and gradient.
        :return:
        """
        print("[handyscikit] Mesh Info: Transfer cell data to node data.")
        # Calculate multi-value of each node.
        tmp = [[] for _ in range(self._node_num)]
        for i in range(self._cell_num):
            for j in self._cells[i]:
                tmp[j].append(result[i] + np.dot(self._nodes[j] - self._cell_coord[i], gradient[i]))
        # Average upper.
        for i in range(self._node_num):
            tmp[i] = sum(tmp[i])/len(tmp[i])
        # Boundary correction.
        # todo: 2D corner condition.
        # todo: Low precision for variant Dirichlet boudnary.
        # todo: Pass periodic boundary condition.
        for i in range(self._face_num):
            if self._face_type[i, 0] == 1:
                tmp[self._faces[i, 0]] = self._face_type[i, 1]
                tmp[self._faces[i, 1]] = self._face_type[i, 1]

        return np.array(tmp, dtype=return_dtype)