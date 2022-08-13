import textwrap
from pathlib import Path

import yaml

from htsct.db.api import Config, VaspInputs
from htsct.io.vaspIO import writePotcar
from htsct.utils.qsub import qsub

from htsct.core.calculator import Calculator
from argparse import ArgumentParser

from htsct.utils.tools import Pipe


class CLICommand:
    """连接数据库以获取vasp输入数据，并自动提交
    """

    @staticmethod
    def add_argments(parser: ArgumentParser):
        add = parser.add_argument
        add("--vaspCmd", default="vasp_std", dest="vaspCmd")
        add("--inputs", default="pbe_struct", dest="inputs")
        add("--path", default=".", dest="path")
        add("--show", default=None, dest="show")
        add("--ftype", default=".cif", dest="ftype", help="输入结构文件的格式[default:.cif]")
        add("--config", default=None, dest="config", help="配置文件选择，默认选择当前激活的[default:active]")

    @staticmethod
    def run(args, parser):
        if args.show:
            inputs_show = VaspInputs.getVaspinputs({"limit": int(args.show)})
            for i in inputs_show:
                print(i["name"], end=" ")
                print("\n")
            return
        p = Path(".").absolute()
        if args.config:
            config = Config.getConfig({"id": args.config})[0]
        else:
            config = Config.getActive()
        command = config[args.vaspCmd]
        with (p / "config").open(mode="w+", encoding="utf-8") as fd:
            yaml.dump({"path": p.__str__(), "command": command}, fd)
        # 生成输入文件
        inputs = VaspInputs.getVaspinputs({"name": args.inputs})[0]["inputs"]  # type: dict
        for k, v in inputs.items():
            (p / k.upper()).write_text(v)
        for i in Path(".").iterdir():
            if i.is_file() and i.suffix == args.ftype:
                from ase.io import read
                read(i, format=args.ftype.strip(".")).write("POSCAR.ase", "vasp")
        with open("POSCAR.ase") as fd:
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
        with open("POSCAR", "w+") as fd:
            fd.write(content)
        writePotcar(".")
        # 任务提交
        script = textwrap.dedent(f"""
                                import yaml
                                from pathlib import Path
                                from htsct import qsub, band_high_throughput
                                from htsct.core.calculator import Calculator
                                if __name__ == "__main__":
                                    qsub(1, 24)
                                    p = Path(".").absolute()
                                    with (p / "config").open(encoding="utf-8") as fd:
                                        data = yaml.load(fd, Loader=yaml.FullLoader)
                                    Calculator.runCommand(data["command"], Path(data["path"]))""").lstrip()
        with open("qsub.py", "w+") as fd:
            fd.write(script)
        pipe = Pipe("python qsub.py\n", ".")
        print(pipe.stdout, pipe.stderr)
