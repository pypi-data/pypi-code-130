from pymatsci.printout import print_author_info
import os
from pymatgen.io.vasp.outputs import Outcar
from optparse import OptionParser
import numpy as np
from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Poscar
import shutil


class Surface():
    """输出表面吸附结构参数"""

    def get_structure_info(self, index_adorp_atom, num_layer, relaxed_slab):
        """
         argv:
             index_adorp_atom： 吸附原子索引
             num_layer：slab层数
             relaxed_slab：弛豫的表面层数
         """
        index_adorp_atom = [i-1 for i in index_adorp_atom]
        structure = Structure.from_file("./CONTCAR")
        coords = structure.cart_coords
        total_atoms = coords.shape[0]  # 总原子数
        index_slab_atom = list(range(total_atoms))
        for i in index_adorp_atom:
            index_slab_atom.remove(i)
        num_adorp_atom = len(index_adorp_atom)  # 吸附原子数

        slab_atoms = total_atoms - num_adorp_atom  # 平板原子数
        coords_slab = coords[index_slab_atom, :]  # 平板坐标
        coords_adorp_atoms = coords[index_adorp_atom, :]  # 吸附原子坐标
        atoms_per_layper = int((total_atoms - num_adorp_atom) / num_layer)  # 每层slab的原子数
        coords_slab = coords_slab[np.argsort(-coords_slab[:, 2])]  # 按z值从大到小排列

        print_author_info()
        # 求每层原子的平均z值
        z_layer_list = []
        for i in range(num_layer):
            z_layer = 0
            for j in range(atoms_per_layper):
                z_layer += coords_slab[i * atoms_per_layper + j, 2]
            z_layer = z_layer / atoms_per_layper
            print("The z-coordinate in the {}th layer: {}".format(i + 1, z_layer))
            z_layer_list.append(z_layer)
        print('-'*54)
        # 求层间距
        for i in range(relaxed_slab + 1):
            dis = z_layer_list[i] - z_layer_list[i + 1]
            print("Interlayer spacing between layers {} and {}: {}".format(i + 1, i + 2, dis))
        print('-' * 54)
        # 求吸附原子与表面的距离
        if num_adorp_atom > 0:
            for i in range(num_adorp_atom):
                dis = coords_adorp_atoms[i, 2] - z_layer_list[0]
                print("The distance between the {}th adatom and surface: {}".format(i + 1, dis))
        print('-' * 54)

    def generate_grid(self, super_a, super_b, a_grid=8, b_grid=8, ads_atom_index=0):
        """
        产生模型
        super_a, super_b：在晶格矢量ab方向的晶胞个数
        a_grid, b_grid：在晶格矢量ab方向的计算的网格数
        """
        structure = Structure.from_file("./PES/POSCAR")
        range_a = np.linspace(0, 1.0 / super_a, a_grid + 1)
        range_b = np.linspace(0, 1.0 / super_b, b_grid + 1)
        element = structure.species[ads_atom_index - 1]
        # 提取selective_dynamics
        for key, value in structure.site_properties.items():
            ele_properties = {key: value[ads_atom_index - 1]}
        z = structure.frac_coords[ads_atom_index - 1, 2]
        for i in range_a[:-1]:
            for j in range_b[:-1]:
                structure.replace(ads_atom_index - 1, element, [i, j, z], properties=ele_properties)
                filename = "%f-%f" % (i, j)
                filename = os.path.join('./PES', filename)
                if not os.path.exists(filename):
                    os.mkdir(filename)

                poscar = Poscar(structure)
                poscar.write_file(filename + "/POSCAR")
                shutil.copy('./PES/INCAR', filename + '/INCAR')
                shutil.copy('./PES/KPOINTS', filename + '/KPOINTS')
                shutil.copy('./PES/POTCAR', filename + '/POTCAR')
                shutil.copy('./PES/vasp.pbs', filename + '/vasp.pbs')

    def extract_data(self, super_a, super_b, total_energy, ads_atom_index=0):
        """提取数据"""
        root_list = []
        data_list = []
        file_path = './PES'
        for root, dirs, files in os.walk(file_path):
            if root != file_path:
                root_list.append(root)
        for root in root_list:
            data = Outcar(root + '/OUTCAR')
            energy = data.final_energy - total_energy   # 能量
            structure = Structure.from_file(root + "./CONTCAR")
            element = structure.species[ads_atom_index - 1]
            x, y, z = tuple(structure.frac_coords[ads_atom_index - 1])
            for i in range(super_a):
                for j in range(super_b):
                    coord = [x + i / super_a, y + j / super_b, z]
                    if coord[0] == 0:
                        coord1 = [1, y + j / super_b, z]
                        structure.replace(ads_atom_index - 1, element, coord1)
                        coord1 = list(structure.cart_coords[ads_atom_index - 1])
                        coord1.append(energy)
                        data_list.append(coord1)
                    if coord[1] == 0:
                        coord1 = [x + i / super_a, 1, z]
                        structure.replace(ads_atom_index - 1, element, coord1)
                        coord1 = list(structure.cart_coords[ads_atom_index - 1])
                        coord1.append(energy)
                        data_list.append(coord1)
                    if coord[0] == 0 and coord[1] == 0:
                        coord1 = [1, 1, z]
                        structure.replace(ads_atom_index - 1, element, coord1)
                        coord1 = list(structure.cart_coords[ads_atom_index - 1])
                        coord1.append(energy)
                        data_list.append(coord1)
                    structure.replace(ads_atom_index - 1, element, coord)
                    coord = list(structure.cart_coords[ads_atom_index - 1])
                    coord.append(energy)
                    data_list.append(coord)
        data = np.array(data_list)
        np.savetxt('data.txt', data, delimiter='\t')

    #
    #
    # data = Structure(lattice, species, coord)
    # poscar = Poscar(data)
    # poscar.write_file("hah")
