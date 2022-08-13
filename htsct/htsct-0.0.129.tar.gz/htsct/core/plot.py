import json
import os
from pathlib import Path
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from pymatgen.electronic_structure.plotter import BSDOSPlotter
from pymatgen.io.vasp.outputs import Vasprun
from htsct.utils.tools import Pipe

mpl.use('Agg')  # 使得终端不显示图片


class BandPlot:
    font = {
        # 'family': 'simhei',
        'color': 'black',
        'weight': 'normal',
        'size': 12,
    }
    Greek_alphabets = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda',
                       'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Pega']

    def __init__(self, band_directory):
        self.band_directory = Path(band_directory)
        Pipe("echo -e '211\n0\n'| vaspkit", band_directory)
        self.x_labels = []  # x轴刻度标签
        self.x_value = []  # x轴刻度值
        self.band_data = None
        self.data = None
        self.color_maps = ['#00CDCD', '#FF4040']
        self.spin_labels = ['Spin-up', 'Spin-down']
        self.read_datas()
        self.plot()

    def read_datas(self):
        """
        从KLABELS和BAND.dat中分别读取x轴信息和(x,y)信息
        """
        self.data = json.loads((self.band_directory / "Band_Position_Info").read_text())
        self.band_data = np.loadtxt((self.band_directory / 'BAND.dat').__str__(), dtype=np.float64)
        lines = (self.band_directory / 'KLABELS').read_text(encoding="utf-8").splitlines(keepends=True)[1:]
        for line in lines:
            if len(line.split()) == 2 and not line.startswith('*'):  # 判断含有2列的行，且不以*开头
                klabel = line.split()[0]
                for j in range(len(BandPlot.Greek_alphabets)):
                    upper_case = BandPlot.Greek_alphabets[j].upper()
                    if klabel.find(upper_case) >= 0:  # 判断是否为希腊字母
                        latex_exp = r'' + '$\\' + BandPlot.Greek_alphabets[j] + '$'  # 使用latex格式
                        klabel = klabel.replace(upper_case, latex_exp)
                if klabel.find('_') > 0:
                    n = klabel.find('_')
                    klabel = klabel[:n] + '$' + klabel[n:n + 2] + '$' + klabel[n + 2:]
                self.x_labels.append(klabel)
                self.x_value.append(float(line.split()[1]))

    def plot(self):
        """
        能带图的绘制
        """
        figure = plt.figure()  # 创建画布
        figure.set_size_inches(8, 6)  # 设置画布尺寸
        ax1 = figure.add_subplot(111)  # 创建子图
        ax1.axhline(y=0, linestyle='--', linewidth=0.5, color='0.5')  # y=0水平线绘制
        for i in self.x_value[1:-1]:
            ax1.axvline(x=i, linestyle='--', linewidth=0.5, color='0.5')  # k点竖直线绘制
        n_spin = self.band_data.shape[1] - 1
        for i in range(n_spin):  # 若有自旋极化则绘制多条曲线，默认一条
            if i == 0:
                ax1.plot(self.band_data[:, 0], self.band_data[:, i + 1] - self.data["_vbm"], linewidth=2.0,
                         color=self.color_maps[i], label=self.spin_labels[i])
            else:
                ax1.plot(self.band_data[:, 0], self.band_data[:, i + 1] - self.data["_vbm"], linewidth=2.0,
                         color=self.color_maps[i], label=self.spin_labels[i], linestyle=":")
        if n_spin > 1:  # 如果考虑了自旋极化，则显示两条不同线的图例
            ax1.legend(loc='best', shadow=False, labelspacing=0.1)  # 图例效果
        ax1.set_xticks(self.x_value)  # x轴坐标刻度值
        ax1.set_xticklabels(self.x_labels, rotation=0, fontsize=BandPlot.font['size'] - 2,
                            # fontname=BandPlot.font['family'],
                            fontweight='bold')  # x轴标签
        ax1.set_xlim((self.x_value[0], self.x_value[-1]))  # 设置x轴范围
        ax1.set_ylabel(r'$\mathrm{Energy}$ (eV)',
                       fontdict=BandPlot.font,
                       fontweight='bold')  # y轴标签
        plt.yticks(fontsize=BandPlot.font['size'] - 2,
                   # fontname=BandPlot.font['family'],
                   fontweight='bold')  # y轴刻度字体及大小
        plt.ylim((-3, 3))  # 设置y轴范围
        plt.style.use("seaborn-bright")
        plt.savefig(os.path.join(self.band_directory, 'band2.png'), dpi=300)  # 设置图片分辨率dpi，并保存

    def band_dos(self):
        tmp = (self.band_directory / "BAND_GAP").read_text(encoding="utf-8").splitlines(keepends=True)
        for line in tmp:
            if line.strip().startswith("Eigenvalue of VBM"):
                efermi = float(line.split()[-1])
        vasprun = self.band_directory / "vasprun.xml"
        vasprun = Vasprun(vasprun.__str__(), parse_projected_eigen=True, parse_potcar_file=False)
        bs_data = vasprun.get_band_structure(line_mode=True, efermi=efermi)
        dos_data = vasprun.complete_dos
        dos_data.efermi = efermi + 0.1
        banddos_fig = BSDOSPlotter(bs_projection='elements', dos_projection='elements',
                                   vb_energy_range=4, fixed_cb_energy=True)
        banddos_fig.get_plot(bs=bs_data, dos=dos_data)
        plt.savefig(self.band_directory / 'banddos_fig.png')
        return self


if __name__ == '__main__':
    bp = BandPlot(".")
