import json
from datetime import datetime
import ase.io
from htsct.utils.tools import Pipe
from htsct.io.vaspIO import writePotcar
from pathlib import Path
import wrapt
from htsct.db.api import TaskLog, VaspInputs
from uuid import uuid1


def taskLogDecorator(task_type):
    """
    类装饰器，用于记录类中函数执行时间
    :param task_type:工作类型
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        st = datetime.now()
        result = wrapped(*args, **kwargs)
        et = datetime.now()
        time_span = et - st
        TaskLog.setTaskLog([
            {
                "id": uuid1().hex,
                "log": json.dumps({
                    "start time": st.__str__(),
                    "end time": et.__str__(),
                    'path': str(instance.root),
                    "task type": task_type,
                    "time used": str(time_span)
                })
            }
        ])
        return result

    return wrapper


class Calculator:
    def __init__(self, root, config):
        self.root = Path(root).absolute()
        self.structGamDir = self.root / "gam"
        self.structDir = self.root / "struct"
        self.scfDir = self.root / "scf"
        self.bandDir = self.root / "band"
        self.config = config

    def checkPOSCAR(self, src: Path, target: Path):
        POSCAR = src / "POSCAR.ase"
        input_file_type = self.config["input_file_type"]
        target.mkdir(parents=True, exist_ok=True)
        for file in POSCAR.parent.iterdir():
            if file.suffix == input_file_type:
                ase.io.read(file).write(POSCAR, "vasp")
        if not POSCAR.exists():
            raise Exception("无法找到输入结构文件")
        with open(POSCAR) as fd:
            lines = fd.readlines()
        symbol = lines[5].split()
        number = lines[6].split()
        positions = lines[8:]
        d = {}
        for s, n in zip(symbol, number):
            n = int(n)
            if s not in d.keys():
                d.update({s: [0, []]})
            d[s][0] = d[s][0] + n
            d[s][1].extend([positions.pop(0) for _ in range(n)])
        _symbol = []
        _number = []
        _positions = []
        for k, v in d.items():
            _symbol.append(k)
            _number.append(str(v[0]))
            _positions.extend(v[1])
        name = "".join([f"{s}{n}" for s, n in zip(_symbol, _number)])
        content = f"{name}\n{''.join(lines[1:5])}{' ' + ' '.join(_symbol)}\n{'  ' + ' '.join(_number)}\n{lines[7]}{''.join(_positions)}"
        with open(target / "POSCAR", "w+") as fd:
            fd.write(content)

    @taskLogDecorator("struct_gam")
    def structGam(self, command):
        """Gam Structure optimization calculator.
        """
        self.structGamDir.mkdir(exist_ok=True, parents=True)
        inputs = VaspInputs.getVaspinputs({"name": "pbe_gam"})[0]["inputs"]  # type: dict
        for k, v in inputs.items():
            (self.structGamDir / k.upper()).write_text(v)
        self.checkPOSCAR(self.root, self.structGamDir)  # 生成POSCAR文件
        writePotcar(self.structGamDir)
        self.runCommand(command, self.structGamDir)

    @taskLogDecorator("struct")
    def struct(self, command):
        """Structure optimization calculator.
        """
        self.structDir.mkdir(exist_ok=True, parents=True)
        inputs = VaspInputs.getVaspinputs({"name": "pbe_struct"})[0]["inputs"]  # type: dict
        for k, v in inputs.items():
            (self.structDir / k.upper()).write_text(v)
        (self.structGamDir / "CONTCAR").replace(self.structDir / "POSCAR")  # 生成POSCAR
        writePotcar(self.structDir)
        self.runCommand(command, self.structDir)

    @taskLogDecorator("scf")
    def scf(self, command):
        """Scf calculator.
        """
        self.scfDir.mkdir(exist_ok=True, parents=True)
        inputs = VaspInputs.getVaspinputs({"name": "pbe_scf"})[0]["inputs"]  # type: dict
        for k, v in inputs.items():
            (self.scfDir / k.upper()).write_text(v)
        (self.structDir / "CONTCAR").replace(self.scfDir / "POSCAR")
        writePotcar(self.scfDir)
        self.runCommand(command, self.scfDir)

    @taskLogDecorator("band")
    def band(self, command):
        """Band calculator.
        """
        self.bandDir.mkdir(exist_ok=True, parents=True)
        inputs = VaspInputs.getVaspinputs({"name": "pbe_band"})[0]["inputs"]  # type: dict
        for k, v in inputs.items():
            (self.bandDir / k.upper()).write_text(v)
        (self.scfDir / "CONTCAR").replace(self.bandDir / "POSCAR")
        (self.scfDir / "CHGCAR").replace(self.bandDir / "CHGCAR")
        (self.scfDir / "WAVECAR").replace(self.bandDir / "WAVECAR")
        writePotcar(self.bandDir)
        self.runCommand(command, self.bandDir)

    @staticmethod
    def runCommand(command, directory: Path):
        _commands = ["local NP\n",
                     "local OPTIND\n",
                     'NP=$(cat "$PBS_NODEFILE" | wc -l)\n',
                     'cat "$PBS_NODEFILE" | sort | uniq | tee /tmp/nodes.$$ | wc -l\n',
                     'cat "$PBS_NODEFILE" >/tmp/nodefile.$$\n',
                     f'mpirun -genv I_MPI_DEVICE ssm -machinefile /tmp/nodefile.$$ -n "$NP" {command}\n',
                     'rm - rf / tmp / nodefile.$$\n',
                     'rm - rf / tmp / nodes.$$\n'
                     ]
        cmds = "".join(_commands)
        pipe = Pipe(cmds, directory)
        with open(directory / "vasp.out", "w+") as fd:
            fd.write(pipe.stdout)
