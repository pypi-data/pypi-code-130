import random
import time
from pathlib import Path
from uuid import uuid1
import wrapt
from htsct import Calculator
from htsct.core.dataAnalysis import DataExtractor
from htsct.db.api import Config, TaskLog
from htsct.constants import ACTIVE_CONFIG


def endless():
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        cwd = Path.cwd()
        count = 0
        A = set()
        while True:
            if ACTIVE_CONFIG == "default":
                config = Config.getActive()
            else:
                config = Config.getConfig({"id": ACTIVE_CONFIG})[0]
            wait_interval = config["wait_interval"]
            input_file_type = config["input_file_type"]
            B = set()  # 用于本地保存所有.cif路径
            for i in cwd.iterdir():
                if i.is_file() and i.name.endswith(input_file_type) and not i.name.startswith("."):
                    B.add(cwd / i.name[0:-len(input_file_type)])
            C = A | B  # 两个集合相加
            D = C - A  # 判断是否有差别
            if not D:
                count += 1
                time.sleep(1)
                if count >= wait_interval:
                    break
                continue
            work_path = random.choice(list(D))
            try:
                work_path.mkdir(parents=True, exist_ok=True)
                input_file = f"{work_path.name}{input_file_type}"
                (cwd / input_file).replace(work_path / input_file)
                wrapped(work_path=work_path, config=config, *args, **kwargs)
                A.add(work_path)
            except Exception as e:
                TaskLog.setTaskLog([{
                    "id": uuid1().hex,
                    "log": f"{work_path}:{e}"
                }])
                continue

    return wrapper


@endless()
def band_high_throughput(**kwargs):
    """高通量能带计算脚本"""
    # config = Config.getActive()
    config = kwargs.pop("config")
    VASP_STD = config["vasp_std"]
    VASP_GAM = config["vasp_gam"]
    work_path = kwargs.pop("work_path")
    calc = Calculator(work_path, config)
    dataExtractor = DataExtractor(work_path)
    calc.structGam(command=VASP_GAM)
    dataExtractor.gamDataWriter(calc.structGamDir)
    calc.struct(command=VASP_STD)
    dataExtractor.structDataWriter(calc.structDir)
    calc.scf(command=VASP_STD)
    dataExtractor.scfDataWriter(calc.scfDir)
    calc.band(command=VASP_STD)
    dataExtractor.bandDataWriter(calc.bandDir)
    dataExtractor.clearFiles()
