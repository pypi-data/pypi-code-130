from pymatgen.core.structure import Structure, Lattice
from pymatgen.io.vasp.inputs import Poscar
import math
import numpy as np
from pymatgen.io.lammps.data import LammpsData
from pymatsci.printout import print_properties, print_author_info


class Nano(object):
    """model abstract class"""

    def __init__(self, n, m, bond_length, atom_type):
        self.n = n
        self.m = m
        if self.m > self.n:
            self.n, self.m = self.m, self.n
        self.bond_length = bond_length
        self.atom_type = atom_type

        """
        Args:
            n (int): chirality parameter
            m (int): chirality parameter
            bond_length (float): bond length
            atom_type (list): atomic species
        """

    def rotation_a1a2(self, theta):
        """
        Args:
            theta (float): angle

        Return:
            rotation_matrics (numpy.ndarray): rotation matrix
        """

        q1 = math.cos(theta)
        q2 = 1 / math.sqrt(3) * math.sin(theta)
        rotation_matrics = np.matrix([[q1 - q2, -2 * q2], [2 * q2, q1 + q2]])
        return rotation_matrics

    def rotation_ij(self, theta):
        """
        Args:
            theta (float): angle

        Return:
            rotation_matrics (numpy.ndarray): rotation matrix
         """
        q1 = math.cos(theta)
        q2 = math.sin(theta)
        rotation_matrics = np.matrix([[q1, -q2], [q2, q1]])  
        return rotation_matrics

    def get_structures(self):
        """
        Return:
            structure (pymatgen.core.structure.Structure)
        """
        properties = self.get_properties()
        atom_coord_info = self.build_structure()
        lattice = properties['Lattice']
        atom_coord = atom_coord_info[:, 0:3].astype('float')
        elements = list(atom_coord_info[:, 3])
        lattice = Lattice(lattice)
        structure = Structure(lattice=lattice, species=elements, coords=atom_coord,
                              coords_are_cartesian=True)
        return structure

    def get_properties(self):
        pass

    def build_structure(self):
        pass

    def printout(func):
        """printout"""
        def wrap(self, file_path):
            propertie = self.get_properties()
            print_author_info()
            print("The file has been successfully written!")
            print('-------------->')
            print_properties(propertie)
            func(self, file_path)
        return wrap

    @printout
    def write_vasp(self, file_path):
        """
        preprocessing of vasp input file

        Args:
            file_path (str): file path
        """
        structure = self.get_structures()
        poscar = Poscar(structure)
        poscar.write_file(file_path)

    @printout
    def write_lammps(self, file_path):
        """
        preprocessing of lammps input file

        Args:
            file_path (str): file path
        """
        structure = self.get_structures()
        data = LammpsData.from_structure(structure)
        data.write_file(file_path)






