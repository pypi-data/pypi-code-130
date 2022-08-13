import json
import re
from pathlib import Path
from ase.io import read
from shutil import copy, rmtree
from htsct.constants import CALC_FILES, TASK_DESCRIPTION
from htsct.db.api import Ribbon, TaskLog
from htsct.utils.tools import Pipe, md5_hex, matchList, matchManyList
from htsct.utils.vaspOutAnlysis import VaspOutAnalysis


class DataExtractor:
    def __init__(self, root):
        self.root = Path(root)
        self.id = ""
        self.target_path = Path(CALC_FILES) / self.root.name

    def gamDataWriter(self, gamPath: Path):
        self.id = md5_hex(gamPath / "POSCAR")
        Ribbon.createRibbon([
            {
                "id": self.id,
                "poscar": (gamPath / "POSCAR").read_text(encoding="utf-8"),
                "formula": read(gamPath / "POSCAR").get_chemical_formula(),
                "work_path": self.root.__str__(),
                "description": TASK_DESCRIPTION
            }
        ])

    def structDataWriter(self, structPath: Path):
        vaspOutAnalysis = VaspOutAnalysis(structPath)
        if not vaspOutAnalysis.is_converge():
            err = vaspOutAnalysis.error_collection()
            warn = vaspOutAnalysis.warning_collection()
            TaskLog.setTaskLog([
                {
                    "id": self.id,
                    "log": f"Error:\n{err}\n\nWarn:\n{warn}\n\n结构未收敛,终止计算:{structPath}"
                }
            ])
            raise Exception(f"结构优化未收敛，计算中止。中止计算的文件夹为{structPath}")
        oszicar_content = (structPath / "OSZICAR").read_text(encoding="utf-8")
        line = matchList(oszicar_content.split("\n")[-2::], r".*?F=(.*?)E0=(.*?)d E.*?mag=(.*)")
        last, E0, mag = re.match(r".*?F=(.*?)E0=(.*?)d E.*?mag=(.*)", line).groups()
        self.copyFiles("gam")
        self.copyFiles("struct")
        Ribbon.updateRibbon([
            {
                "id": self.id,
                "contcar": (structPath / "CONTCAR").read_text(encoding="utf-8"),
                "last_step_energy": float(last),
                "E0": float(E0),
                "mag": float(mag)
            }
        ])

    def scfDataWriter(self, scfPath: Path):
        lines1 = Pipe("vaspkit -task 426\n", scfPath).stdout.splitlines(True)
        lines2 = Pipe("grep E-fermi OUTCAR\n", scfPath).stdout.splitlines(True)
        self.copyFiles("scf")
        Ribbon.updateRibbon([{
            "id": self.id,
            "vacuum_level": float(matchList(lines1, r"\s*?Vacuum-Level\s*?\(eV\)").split()[-1]),
            "e_fermi": float(matchList(lines2, r"\s*?E-fermi\s*?").split()[2])
        }])

    def bandDataWriter(self, bandPath: Path):
        band_dir = Path(bandPath).absolute()
        Pipe("vaspkit -task 211\n", band_dir)
        BAND_GAP = (band_dir / "BAND_GAP").read_text(encoding="utf-8").splitlines()
        patterns = [
            r"\s*?Band\s*?Gap",  # band_gap
            r"\s*?Eigenvalue of VBM\s*?",  # _vbm
            r"\s*?Eigenvalue of CBM\s*?",  # _cbm
            r"\s*?Fermi Energy\s*?",  # fermi_energy
            r"\s*?Location of VBM\s*?",  # vbm_position
            r"\s*?Location of CBM\s*?"  # cbm_position
        ]
        band_gap, _vbm, _cbm, fermi_energy, vbm_position, cbm_position = matchManyList(BAND_GAP, patterns)
        Ribbon.updateRibbon([{"id": self.id,
                              "band_gap": float(band_gap.split()[-1]),
                              "vbm_": float(_vbm.split()[-1]),
                              "cbm_": float(_cbm.split()[-1]),
                              "fermi_energy": float(fermi_energy.split()[-1]),
                              "vbm_position": vbm_position.split()[-3] + vbm_position.split()[-2] +
                                              vbm_position.split()[-1],
                              "cbm_position": cbm_position.split()[-3] + cbm_position.split()[-2] +
                                              cbm_position.split()[-1]
                              }])
        ribbon = Ribbon.getRibbon({"id": self.id})[0]
        Ribbon.updateRibbon([
            {
                "id": self.id,
                "work_function": ribbon["vacuum_level"] - ribbon["e_fermi"],
                "cbm": ribbon["cbm_"] - ribbon["fermi_energy"] - (ribbon["vacuum_level"] - ribbon["e_fermi"]),
                "vbm": ribbon["vbm_"] - ribbon["fermi_energy"] - (ribbon["vacuum_level"] - ribbon["e_fermi"])
            }
        ])
        self.copyFiles("band")
        with open(bandPath / "Ribbon_Info", "w+") as fd:
            ribbon = Ribbon.getRibbon({"id": self.id})[0]
            fd.write(json.dumps(ribbon, indent=2, sort_keys=True))

    def copyFiles(self, folder_name):
        target_path = self.target_path / folder_name
        src_path = self.root / folder_name
        if target_path.exists():
            rmtree(target_path)
        target_path.mkdir(parents=True, exist_ok=True)
        for f in src_path.iterdir():
            if f.is_file():
                copy(f.__str__(), target_path.__str__())

    def clearFiles(self):
        rmtree(self.root)
