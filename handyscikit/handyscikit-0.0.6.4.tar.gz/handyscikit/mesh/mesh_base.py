import gmsh
import math
import numpy as np


class MeshBase:
    def __init__(self):
        self._cell_num = None
        self._dim = None
        self._face_num = None
        self._face_per_cell = None
        self._node_num = None
        self._node_per_cell = None
        self._node_per_face = None

        self._cell_cell = None
        self._cell_volume = None
        self._cell_face = None
        self._cell_center = None
        self._cells = None
        self._face_area = None
        self._face_cell = None
        self._face_center = None
        self._face_info = None
        self._face_norm = None
        self._faces = None
        self._nodes = None

        self._gmsh_element_type = None

        self.__physical_group_info = {}

    def set_dirichlet_boundary(self, boundaries, info):
        physical_group_dim_tag = (self._dim-1, gmsh.model.add_physical_group(self._dim-1, boundaries))
        self.__physical_group_info[physical_group_dim_tag] = [1, info, 0]

    def set_periodic_boundary(self, boundaries):
        """
        This periodic interface only support translation type periodic boundaries.
        :param boundaries:
        :return:
        """
        assert len(boundaries)==2

        # todo: 这个提炼一个提取点的函数，检测是不是均值更准一点。
        # Calculate center coordinate of boundaries 0.
        upward, downward = gmsh.model.get_adjacencies(self._dim-1, boundaries[0])
        tuple0 = gmsh.model.get_bounding_box(self._dim-2, downward[0])
        tuple1 = gmsh.model.get_bounding_box(self._dim-2, downward[1])
        center = np.zeros(3, dtype=np.float64)
        center[0] = (tuple0[0] + tuple0[3] + tuple1[0] + tuple1[3])/4
        center[1] = (tuple0[1] + tuple0[4] + tuple1[1] + tuple1[4])/4
        center[2] = (tuple0[2] + tuple0[5] + tuple1[2] + tuple1[5])/4
        # Calculate center coordinate of boundaries 1.
        upward, downward = gmsh.model.get_adjacencies(self._dim - 1, boundaries[1])
        tuple0 = gmsh.model.get_bounding_box(self._dim-2, downward[0])
        tuple1 = gmsh.model.get_bounding_box(self._dim-2, downward[1])
        center[0] -= (tuple0[0] + tuple0[3] + tuple1[0] + tuple1[3]) / 4
        center[1] -= (tuple0[1] + tuple0[4] + tuple1[1] + tuple1[4]) / 4
        center[2] -= (tuple0[2] + tuple0[5] + tuple1[2] + tuple1[5]) / 4

        affine = np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], dtype=np.float64)
        affine[3] = center[0]
        affine[7] = center[1]
        affine[11] = center[2]
        gmsh.model.mesh.set_periodic(self._dim-1, [boundaries[0]], [boundaries[1]], affine)

        physical_group_dim_tag = (self._dim-1, gmsh.model.add_physical_group(self._dim-1, boundaries))
        self.__physical_group_info[physical_group_dim_tag] = [4, boundaries[0], 0]

    def _calculate_face_info_2D(self):
        self._face_info = np.zeros([self._face_num, 3], dtype=np.float32)

        physical_group_dim_tags = gmsh.model.get_physical_groups()
        for dim_tag in physical_group_dim_tags:
            physical_group_info = self.__physical_group_info[dim_tag]

            if physical_group_info[0] == 1:
                self.__deal_dirichlet_face_2D(dim_tag)
            elif physical_group_info[0] == 4:
                self.__deal_periodic_face_2D(dim_tag)
            else:
                assert False

    def _calculate_face_info_3D(self):
        pass

    def _generate_topology_information(self):
        self.__make_nodes()
        self.__make_cells()
        self.__make_faces_and_other_relationships()

        self.__calculate_cell_center()
        self.__calculate_cell_volume()
        self.__calculate_face_area()
        self.__calculate_face_center()
        self.__calculate_face_norm()

    def __deal_dirichlet_face_2D(self, physical_group_dim_tag):
        physical_group_info = self.__physical_group_info[physical_group_dim_tag]
        entity_tags = gmsh.model.get_entities_for_physical_group(physical_group_dim_tag[0], physical_group_dim_tag[1])

        for entity_tag in entity_tags:
            # Line element type mark number is 1.
            node_tags = gmsh.model.mesh.get_element_edge_nodes(1, entity_tag)

            face_tags, unuse = gmsh.model.mesh.get_edges(node_tags)
            # Node tag in gmsh starts from 1, however, index starts from zero.
            face_tags -= 1
            node_tags -= 1

            if isinstance(physical_group_info[1], float) or isinstance(physical_group_info[1], int):
                for face_tag in face_tags:
                    self._face_info[face_tag] = physical_group_info
            elif isinstance(physical_group_info[1], str):
                # todo: In this condition, only straight line can be used.
                node_s = self._nodes[node_tags[0]]
                node_e = self._nodes[node_tags[-1]]
                if np.linalg.norm(node_e) < np.linalg.norm(node_s):
                    node_e, node_s = node_s, node_e
                line_length = np.linalg.norm(node_e - node_s)

                if physical_group_info[1] == "cos":
                    for face_tag in face_tags:
                        percent = np.linalg.norm(self._face_center[face_tag] - node_s) / line_length
                        self._face_info[face_tag] = [physical_group_info[0], math.cos(percent * 2 * math.pi), 0]
                else:
                    assert False
            else:
                assert False

    def __deal_periodic_face_2D(self, physical_group_dim_tag):
        """
        [4, periodic_face, periodic_cell]
        :param physical_group_dim_tag:
        :return:
        """
        physical_group_info = self.__physical_group_info[physical_group_dim_tag]
        master_tag, nodes, master_nodes, affine = gmsh.model.mesh.get_periodic_nodes(1, physical_group_info[1])

        # Reset node order.
        nodes[1], nodes[-1] = nodes[-1], nodes[1]
        master_nodes[1], master_nodes[-1] = master_nodes[-1], master_nodes[1]

        face_num = len(nodes) - 1
        for i in range(face_num):
            tag_face, unuse = gmsh.model.mesh.get_edges([nodes[i], nodes[i+1]])
            tag_master_face, unuse = gmsh.model.mesh.get_edges([master_nodes[i], master_nodes[i+1]])
            self._face_info[tag_face-1, 0] = 4
            self._face_info[tag_face-1, 1] = tag_master_face-1
            self._face_info[tag_face-1, 2] = self._face_cell[tag_master_face-1, 0]
            self._face_info[tag_master_face-1, 0] = 4
            self._face_info[tag_master_face-1, 1] = tag_face-1
            self._face_info[tag_master_face-1, 2] = self._face_cell[tag_face-1, 0]

    def __make_cells(self):
        (cell_tags, node_tags) = gmsh.model.mesh.get_elements_by_type(self._gmsh_element_type)  # 3 means quadrilateral.
        self._cells = node_tags.reshape([-1, self._node_per_cell])
        self._cells -= 1  # Gmsh cells index starts from 1, but index start from zero, transfer it.
        self._cell_num = self._cells.shape[0]

    def __make_faces_and_other_relationships(self):
        gmsh.model.mesh.create_edges()

        element_node_tags = gmsh.model.mesh.get_element_edge_nodes(self._gmsh_element_type)
        element_node_num = element_node_tags.size

        (face_tags, unuse) = gmsh.model.mesh.get_edges(element_node_tags)  # Inner face repeated in face tags.
        element_face_num = face_tags.size

        # Calculate face number.
        self._face_num = 0
        tmp = np.full(element_face_num, fill_value=-1)
        for i in range(element_face_num):
            if tmp[face_tags[i]] == -1:
                tmp[face_tags[i]] = 0
                self._face_num += 1

        self._faces = np.zeros([self._face_num, self._node_per_face], dtype=np.int32)
        for i in range(element_node_num):
            self._faces[int(face_tags[i//2]-1), i%2] = element_node_tags[i]-1

        self._cell_face = face_tags.reshape([self._cell_num, self._face_per_cell])
        self._cell_face -= 1

        self._face_cell = np.full([self._face_num, 2], fill_value=-1, dtype=np.int32)
        for i in range(self._cell_num):
            for j in range(self._face_per_cell):
                if self._face_cell[self._cell_face[i, j], 0] == -1:
                    self._face_cell[self._cell_face[i, j], 0] = i
                else:
                    self._face_cell[self._cell_face[i, j], 1] = i

        self._cell_cell = np.full([self._cell_num, self._face_per_cell], fill_value=-1, dtype=np.int32)
        for i in range(self._face_num):
            if self._face_cell[i, 0]!=-1 and self._face_cell[i, 1]!=-1 :
                for j in range(self._face_per_cell):
                    if self._cell_cell[self._face_cell[i, 0], j] == -1:
                        self._cell_cell[self._face_cell[i, 0], j] = self._face_cell[i, 1]
                        break
                for j in range(self._face_per_cell):
                    if self._cell_cell[self._face_cell[i, 1], j] == -1:
                        self._cell_cell[self._face_cell[i, 1], j] = self._face_cell[i, 0]
                        break

    def __make_nodes(self):
        (node_tags, node_coordinates, unuse) = gmsh.model.mesh.get_nodes()
        self._node_num = node_tags.size
        self._nodes = node_coordinates.reshape([-1, 3])

    def __calculate_cell_center(self):
        self._cell_center = np.zeros([self._cell_num, 3], dtype=np.float32)

        for i in range(self._cell_num):
            for j in range(self._node_per_cell):
                self._cell_center[i] += self._nodes[self._cells[i, j]]
            self._cell_center[i] /= self._node_per_cell

    def __calculate_cell_volume(self):
        self._cell_volume = np.zeros([self._cell_num], dtype=np.float32)

        if self._gmsh_element_type == 3:
            for i in range(self._cell_num):
                vector_0 = self._nodes[self._cells[i, 0]] - self._nodes[self._cells[i, 1]]
                vector_1 = self._nodes[self._cells[i, 0]] - self._nodes[self._cells[i, 3]]
                self._cell_volume[i] = abs(np.cross(vector_0, vector_1)[2])  # 3D vector cross makes a new vector.
        else:
            self._cell_volume = None

    def __calculate_face_area(self):
        self._face_area = np.zeros([self._face_num], dtype=np.float32)

        if self._gmsh_element_type == 3:
            for i in range(self.face_num):
                self._face_area[i] = np.linalg.norm(self._nodes[self._faces[i,0]] - self._nodes[self._faces[i, 1]])
        else:
            None

    def __calculate_face_center(self):
        self._face_center = np.zeros([self._face_num, 3], dtype=np.float32)

        if self._gmsh_element_type == 3:
            for i in range(self._face_num):
                self._face_center[i] = (self._nodes[self._faces[i,0]] + self._nodes[self._faces[i,1]])/2
        else:
            self._face_center = None

    def __calculate_face_norm(self):
        self._face_norm = np.zeros([self._face_num, 3], dtype=np.float32)

        for i in range(self._face_num):
            x0 = self._nodes[self._faces[i,0], 0]
            y0 = self._nodes[self._faces[i,0], 1]
            x1 = self._nodes[self._faces[i,1], 0]
            y1 = self._nodes[self._faces[i,1], 1]

            if abs(x0 - x1) < 1e-15:
                self._face_norm[i,0] = 1
            elif abs(y0 - y1) < 1e-15:
                self._face_norm[i,1] = 1
            else:
                tmp = (x0 - x1)/(y1 - y0)
                self._face_norm[i,0] = 1/(1 + tmp**2)**0.5
                self._face_norm[i,1] = tmp/(1 + tmp**2)**0.5
            vector = self._cell_center[self._face_cell[i,0]] - \
                     (self._nodes[self._faces[i,0]] + self._nodes[self._faces[i,1]])/2
            if np.dot(self._face_norm[i], vector) > 0:
                self._face_norm[i] *= -1

    @property
    def cell_cell(self):
        return self._cell_cell

    @property
    def cell_center(self):
        return self._cell_center

    @property
    def cell_face(self):
        return self._cell_face

    @property
    def cell_num(self):
        return self._cell_num

    @property
    def cell_volume(self):
        return self._cell_volume

    @property
    def cells(self):
        return self._cells

    @property
    def dim(self):
        return self._dim

    @property
    def face_cell(self):
        return self._face_cell

    @property
    def face_center(self):
        return self._face_center

    @property
    def face_area(self):
        return self._face_area

    @property
    def face_norm(self):
        return self._face_norm

    @property
    def face_info(self):
        return self._face_info

    @property
    def face_num(self):
        return self._face_num

    @property
    def face_per_cell(self):
        return self._face_per_cell

    @property
    def faces(self):
        return self._faces

    @property
    def node_num(self):
        return self._node_num

    @property
    def node_per_cell(self):
        return self._node_per_cell

    @property
    def node_per_face(self):
        return self._node_per_face

    @property
    def nodes(self):
        return self._nodes
