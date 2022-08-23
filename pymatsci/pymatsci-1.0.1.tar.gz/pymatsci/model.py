import math
import numpy as np
import sys
from pymatsci.abstract import Nano
import copy


class Graphene(Nano):
    """building a single layer of graphene"""

    def __init__(self, n, m, bond_length=1.42, atom_type=['C'], period=1,):
        super().__init__(n, m, bond_length, atom_type)
        self.period = period

        """
        Args:
            period (int): number of period  
        """

    def build_structure(self):
        """
        building structure

        Return:
            atom_coord_info (numpy.ndarray): coordinate
        """

        i_j_k = self.bond_length * math.sqrt(3)
        a1 = np.array([i_j_k, 0, 0])
        a2 = np.array([0.5 * i_j_k, math.sqrt(3) / 2 * i_j_k, 0])
        c = self.n * a1 + self.m * a2  
        c_norm = np.linalg.norm(c)
        g1 = math.gcd(self.n + 2 * self.m, self.m + 2 * self.n)
        hex_num = int(2 * (self.n * self.n + self.m * self.m + self.m * self.n) / g1)
        vector_AB = (a1 + a2) / 3
        b_Xmove_length = np.dot(vector_AB, c) / c_norm  
        b_Ymove_length = np.linalg.norm(np.cross(vector_AB, c)) / c_norm
        p1 = 0
        g2 = math.gcd(self.n, self.m)
        while (p1 * self.m + g2) % self.n != 0:
            p1 += 1
        p2 = (p1 * self.m + g2) / self.n
        h = p1 * a1 + p2 * a2
        unit_Ymove = np.linalg.norm(np.cross(h, c)) / c_norm  
        unit_Xmove = np.dot(h, c) / c_norm  
        single_atom_num = self.period * hex_num  
        A_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        B_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        orngin = np.array([0, 0, 5])
        index = 0
        for j in range(g2):  
            for i in range(int(self.period * hex_num / g2)):  
                X_move = j * c_norm / g2 + i * unit_Xmove
                Y_move = i * unit_Ymove
                A_atom_coord[index, 0:3] = orngin + np.array([X_move, Y_move, 0])
                B_atom_coord[index, 0:3] = orngin + np.array([X_move + b_Xmove_length, Y_move + b_Ymove_length, 0])
                index += 1
        atom_coord_info = np.vstack((A_atom_coord, B_atom_coord))
        atom_coord_info[:, 0] = atom_coord_info[:, 0] % c_norm
        num = len(self.atom_type)
        if num == 1:
            atom_coord_info[:, 3] = self.atom_type[0]
        elif num == 2:
            atom_coord_info[0:single_atom_num, 3] = self.atom_type[0]
            atom_coord_info[single_atom_num:, 3] = self.atom_type[1]
        return atom_coord_info

    def get_properties(self):
        """
        getting structural information

        Return:
            properties (dict): structural information
        """
        i_j_k = self.bond_length * math.sqrt(3)
        a1 = np.array([i_j_k, 0, 0])
        a2 = np.array([0.5 * i_j_k, math.sqrt(3) / 2 * i_j_k, 0])
        c = self.n * a1 + self.m * a2  
        c_norm = np.linalg.norm(c)
        g1 = math.gcd(self.n + 2 * self.m, self.m + 2 * self.n)
        p = -(2 * self.m + self.n) / g1
        q = (self.m + 2 * self.n) / g1
        t = p * a1 + q * a2
        t_norm = np.linalg.norm(t)
        hex_num = int(2 * (self.n * self.n + self.m * self.m + self.m * self.n) / g1)
        atom_num = hex_num * 2  
        lattice = [c_norm, 0, 0, 0, self.period * t_norm, 0, 0, 0, 10]
        properties = {'Total number of atoms': atom_num * self.period, 'Lattice': lattice}
        return properties


class MagicGraphene(Nano):
    """building a magic graphene"""

    def __init__(self, n, m, bond_length=1.42, atom_type=['C'], layer_spacing=3.4):
        super().__init__(n, m, bond_length, atom_type)
        self.layer_spacing = layer_spacing

        """
        Args:
            layer_spacing (float): layer spacing
        """

    def build_structure(self):
        """
        building structure

        Return:
            atom_coord_info (numpy.ndarray): coordinate
        """

        a = self.bond_length * math.sqrt(3)
        temp = self.rotation_ij(math.pi / 3)
        base_trans_matrics1 = np.matrix([[1, temp[0, 0]], [0, temp[1, 0]]])
        properties = self.get_properties()
        magic_theta = properties['Magic angle']
        seta = math.acos(
            ((2 * self.n) + self.m) / (2 * math.sqrt(self.m * self.m + self.m * self.n + self.n * self.n)))  
        N = int(properties['Total number of atoms'] / 2)
        base_trans_matrics2 = self.rotation_a1a2(seta)
        C1 = base_trans_matrics2.I * np.matrix([[self.n], [self.m]])
        A = np.matrix([[0], [0]])  
        A = base_trans_matrics2 * A  
        AB = base_trans_matrics2.I * np.matrix([[1 / 3], [1 / 3]])  
        b_c1_move_length = AB[0, 0]  
        b_c2_move_length = AB[1, 0]
        g2 = math.gcd(self.n, self.m)
        c1 = 0
        while (c1 * self.m + g2) % self.n != 0:
            c1 += 1
        c2 = (c1 * self.m + g2) / self.n
        h = base_trans_matrics2.I * np.matrix([[c1], [c2]])
        unit_c1_move = h[0, 0]  
        unit_c2_move = h[1, 0]
        single_atom_num = int(N / 2)  
        A_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        B_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        index = 0
        for j in range(g2):  
            for i in range(int(single_atom_num / g2)):  
                c1_move = float(j * C1[0, 0] / g2 + i * unit_c1_move)
                c2_move = float(i * unit_c2_move)
                A_temp = A.T + np.matrix([c1_move, c2_move])
                h1 = int(A_temp[0, 0] / C1[0, 0])
                A_temp = A_temp - C1.T * h1
                B_temp = A.T + np.matrix([c1_move + b_c1_move_length, c2_move + b_c2_move_length])
                h1 = int(B_temp[0, 0] / C1[0, 0])
                B_temp = B_temp - C1.T * h1
                A_atom_coord[index, 0:2] = A_temp
                B_atom_coord[index, 0:2] = B_temp
                index += 1
        layer1 = np.vstack((A_atom_coord, B_atom_coord))
        num = len(self.atom_type)
        if num == 1:
            layer1[:, 3] = self.atom_type[0]
        elif num == 2:
            layer1[0:single_atom_num, 3] = self.atom_type[0]
            layer1[single_atom_num:, 3] = self.atom_type[1]
        data1 = base_trans_matrics2 * layer1[:, 0:2].T

        layer2 = copy.deepcopy(layer1)
        data2 = copy.deepcopy(data1)
        for i in range(data2.shape[1]):
            n = data2[0, i]
            m = data2[1, i]
            if n != 0 or m != 0:
                seta = math.acos(((2 * n) + m) / (2 * math.sqrt(m * m + m * n + n * n)))
                data2[:, i] = self.rotation_a1a2(2 * (math.pi / 3 - seta)) * data2[:, i]
        data1 = base_trans_matrics1 * data1 * a  
        layer1[:, 0:2] = data1.T
        layer1[:, 2] = 1
        data2 = self.rotation_a1a2(-magic_theta) * data2  
        data2 = base_trans_matrics1 * data2 * a  
        layer2[:, 0:2] = data2.T
        layer2[:, 2] = 1 + self.layer_spacing
        atom_coord_info = np.vstack((layer1, layer2))
        return atom_coord_info

    def get_properties(self):
        """
        getting structural information

        Return:
            properties (dict): structural information
         """
        a = self.bond_length * math.sqrt(3)
        a1 = np.matrix([[1], [0]]) * a  
        a2 = np.matrix([[0.5], [math.sqrt(3) / 2]]) * a  
        magic_theta = math.acos(0.5 * (self.m * self.m + self.n * self.n + 4 * self.m * self.n) / (
                    self.m * self.m + self.n * self.n + self.m * self.n))  
        # L = a * math.sqrt(self.m * self.m + self.n * self.n + self.m * self.n)
        N = 2*int(2 * ((self.n + self.m) * self.n + self.m * self.m))
        L1 = self.n * a1 + self.m * a2
        L2 = self.rotation_ij(math.pi / 3) * L1
        lattice = list(np.array(L1).flatten()) + [0] + list(np.array(L2).flatten()) + [0] + [0, 0, 15]
        properties = {'Total number of atoms': 2 * N, 'Chirality': (self.n, self.m), 'Magic angle': magic_theta, 'Lattice': lattice}
        return properties


class Nanotube(Nano):
    """building a single nanotube"""

    def __init__(self, n, m, bond_length=1.42, atom_type=['C'], period=1):
        super().__init__(n, m, bond_length, atom_type)
        self.period = period

        """
        Args:
            period (float or int): number of period  
        """

    def get_properties(self):
        """
        getting structural information

        Return:
            properties (dict): structural information
        """

        i_j_k = self.bond_length * math.sqrt(3)
        a1 = np.array([i_j_k, 0, 0])
        a2 = np.array([0.5 * i_j_k, math.sqrt(3) / 2 * i_j_k, 0])
        c = self.n * a1 + self.m * a2  
        c_norm = np.linalg.norm(c)  
        d = c_norm / math.pi  
        seta = math.acos(((2 * self.n) + self.m) / (
                    2 * math.sqrt(self.m * self.m + self.m * self.n + self.n * self.n))) * 180 / math.pi  
        g1 = math.gcd(self.n + 2 * self.m, self.m + 2 * self.n)  
        
        p = -(2 * self.m + self.n) / g1
        q = (self.m + 2 * self.n) / g1
        t = p * a1 + q * a2
        t_norm = np.linalg.norm(t)  
        lattice = [d + 10, 0, 0, 0, d + 10, 0, 0, 0, self.period * t_norm]
        
        hex_num = int(2 * (self.n * self.n + self.m * self.m + self.m * self.n) / g1)
        atom_num = hex_num * 2  
        properties = {'Diameter': d, 'Total number of atoms': atom_num * self.period,
                      'Total length': self.period * t_norm, 'Chirality angle': seta, 'Period': self.period,
                      'Chirality': (self.n, self.m), 'Lattice': lattice}
        return properties

    def build_structure(self):
        """
        building structure

        Return:
            atom_coord_info (numpy.ndarray): coordinate
        """

        i_j_k = self.bond_length * math.sqrt(3)
        a1 = np.array([i_j_k, 0, 0])
        a2 = np.array([0.5 * i_j_k, math.sqrt(3) / 2 * i_j_k, 0])
        c = self.n * a1 + self.m * a2  
        c_norm = np.linalg.norm(c)  
        d = c_norm / math.pi  
        g1 = math.gcd(self.n + 2 * self.m, self.m + 2 * self.n)
        hex_num = int(2 * (self.n * self.n + self.m * self.m + self.m * self.n) / g1)
        vector_AB = (a1 + a2) / 3
        b_rotation_angel = 2 * math.pi * (np.dot(vector_AB, c)) / (c_norm ** 2)  
        b_move_length = np.linalg.norm(np.cross(vector_AB, c)) / c_norm
        p1 = 0
        g2 = math.gcd(self.n, self.m)
        while (p1 * self.m + g2) % self.n != 0:
            p1 += 1
        p2 = (p1 * self.m + g2) / self.n
        h = p1 * a1 + p2 * a2
        unit_move = np.linalg.norm(np.cross(h, c)) / c_norm
        unit_rotation = 2 * math.pi / c_norm ** 2 * np.dot(h, c)
        single_atom_num = self.period * hex_num  
        A_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        B_atom_coord = np.zeros([single_atom_num, 4], dtype='O')
        orngin = np.array([0, 0, 0])  
        index = 0
        for j in range(g2):  
            for i in range(int(self.period * hex_num / g2)):  
                rotation_angel = j * 2 * math.pi / g2 + i * unit_rotation
                
                A_atom_coord[index, 0:3] = orngin + d / 2 * np.array(
                    [math.cos(rotation_angel), math.sin(rotation_angel), 0]) + np.array([0, 0, i * unit_move])
                B_atom_coord[index, 0:3] = orngin + d / 2 * np.array(
                    [math.cos(rotation_angel + b_rotation_angel), math.sin(rotation_angel + b_rotation_angel),
                     0]) + np.array([0, 0, b_move_length + i * unit_move])
                index += 1
        atom_coord_info = np.vstack((A_atom_coord, B_atom_coord))
        atom_coord_info[:, 0:2] = atom_coord_info[:, 0:2] + d / 2 + 5
        
        num = len(self.atom_type)
        if num == 1:
            atom_coord_info[:, 3] = self.atom_type[0]
        elif num == 2:
            atom_coord_info[0:single_atom_num, 3] = self.atom_type[0]
            atom_coord_info[single_atom_num:, 3] = self.atom_type[1]
        return atom_coord_info


if __name__ == '__main__':
    
    model = MagicGraphene(9, 4)
    model.write_vasp('C:/Users/58353/Desktop/POSCAR')

    
    
    
    

    
    
    
    