import re
import numpy as np
from pymatgen.io.vasp import Outcar
from pymatgen.core import Structure, Molecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
from pymatgen.core.units import Unit, FloatWithUnit, ArrayWithUnit
from pymatgen.electronic_structure.dos import Dos
from pymatgen.electronic_structure.core import Spin


class ElectronicStructure(object):
    """Electronic structure processing"""

    @staticmethod
    def get_smeared_dos(file_path, save_path):
        data = np.loadtxt(file_path, comments='#')
        for i in range(1, data.shape[1]):
            dos = Dos(0, data[:, 0], {Spin.up: data[:, i]})
            densities = dos.get_smeared_densities(0.2)
            densities = list(densities.values())[0]
            data[:, i] = densities
        np.savetxt(save_path, data, comments='#')


class VaspProcess(object):
    """vasp result processing"""
    def __init__(self, strcture_file='CONTCAR', output='OUTCAR'):
        self.structure = Structure.from_file(strcture_file)
        self.molecule = Molecule(self.structure.species, self.structure.cart_coords)
        self.outcar = Outcar(output)

        self.E_DFT = FloatWithUnit(self.outcar.final_energy, Unit('eV'))   # DFT计算的能量

        self.sch_symbol = PointGroupAnalyzer(self.molecule).sch_symbol  # 点群符号
        self.sigma = self.symmetry_number  # 旋转对称数
        self.atomic_nums = self.molecule.atomic_numbers  # 原子数
        self.w = self.molecule.spin_multiplicity  # 自旋多重性
        self.center_of_mass = ArrayWithUnit(self.molecule.center_of_mass, Unit('ang')).to('m')  # 质心
        self.coords = ArrayWithUnit(self.molecule.cart_coords, Unit('ang')).to('m')
        self.total_atomic_mass = self.atomic_mass.sum()

    @property
    def is_line(self):
        pass

    @property
    def atomic_mass(self):
        """Atomic mass (kg)"""
        m = list()
        for i in self.molecule.species:
            m.append(i.atomic_mass.to('kg'))
        return ArrayWithUnit(np.array(m), Unit('kg'))

    @property
    def vib_freq(self):
        """Extract vibration frequency（Hz）"""
        f = open('OUTCAR')
        lines = f.read()
        f.close()
        vib_real = re.findall('.*f\s*=\s*(.*)\sTHz', lines)
        vib_imag = re.findall('.*f/i=\s*(.*)\sTHz', lines)
        real_freq = list()
        imag_freq = list()
        real_num = 0
        imag_num = 0
        for i in vib_real:
            real_freq.append(float(i))
            real_num += 1
        for i in vib_imag:
            imag_freq.append(float(i))
            imag_num += 1
        return ArrayWithUnit(real_freq, Unit('THz')).to('Hz'), ArrayWithUnit(imag_freq, Unit('THz')).to('Hz'), real_num, imag_num

    @property
    def symmetry_number(self):
        """Get Symmetry from Point Group"""
        sch_symbol = self.sch_symbol
        if sch_symbol in ['C1', 'Ci', 'Cs', 'C*v']:
            symmetrynumber = 1
        elif re.match('C\d+', sch_symbol):
            symmetrynumber = int(re.findall('C(\d+)', sch_symbol)[0])
        elif sch_symbol == 'D*h':
            symmetrynumber = 2
        elif re.match('D\d+', sch_symbol):
            symmetrynumber = int(re.findall('D(\d+)', sch_symbol)[0]) * 2
        elif sch_symbol in ['T', 'Td']:
            symmetrynumber = 12
        elif re.match('S\d+', sch_symbol):
            symmetrynumber = int(re.findall('S(\d+)', sch_symbol)[0]) // 2
        elif sch_symbol == 'Oh':
            symmetrynumber = 24
        elif sch_symbol == 'Ih':
            symmetrynumber = 60
        else:
            symmetrynumber = 1
        return symmetrynumber

    @property
    def moment_of_inertia(self):
        """Calculation of moment of inertia"""

        coords = self.coords - self.center_of_mass
        coords_m = np.hstack((coords, np.array(self.atomic_mass).reshape(len(self.atomic_mass), 1)))  # 数据处理
        I_xx = (coords_m[:, 3] * (coords_m[:, 1] * coords_m[:, 1] + coords_m[:, 2] * coords_m[:, 2])).sum()
        I_yy = (coords_m[:, 3] * (coords_m[:, 0] * coords_m[:, 0] + coords_m[:, 2] * coords_m[:, 2])).sum()
        I_zz = (coords_m[:, 3] * (coords_m[:, 0] * coords_m[:, 0] + coords_m[:, 1] * coords_m[:, 1])).sum()
        I_xy = (coords_m[:, 3] * coords_m[:, 0] * coords_m[:, 1]).sum()
        I_yz = (coords_m[:, 3] * coords_m[:, 1] * coords_m[:, 2]).sum()
        I_xz = (coords_m[:, 3] * coords_m[:, 0] * coords_m[:, 2]).sum()
        I = ArrayWithUnit(np.array([[I_xx, I_xy, I_xz], [I_xy, I_yy, I_yz], [I_xz, I_yz, I_zz]]), Unit('kg m^2'))
        return I


if __name__ == '__main__':

    pass