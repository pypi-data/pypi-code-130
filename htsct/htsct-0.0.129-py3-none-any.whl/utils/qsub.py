import sys
from datetime import datetime as __dt
from os import popen
from os.path import exists
import platform

from htsct.constants import HTS_HOME
from htsct.db.api import Config


def qsub(nodes=1, cores=28, python_script=sys.argv[0]):
    """
    用于python脚本提交
    :param python_script: 本脚本执行路径
    :param nodes:所用节点数，default:1
    :param cores:每个节点所用核数,default:28
    """
    if platform.system() == 'Windows':
        return
    if not python_script:
        raise Exception("Please specify python script name!")
    if not exists("run"):
        QSUB_PATH = HTS_HOME / Config.getActive()["qsub_filename"]
        qsub_data_lines = Config.getActive()["qsub"].split("\n")
        for line in qsub_data_lines:
            if line.startswith("#PBS -l"):
                index = qsub_data_lines.index(line)
                qsub_data_lines[index] = f"#PBS -l nodes={nodes}:ppn={cores}"
        with open(QSUB_PATH, "w+") as sh:
            for line in qsub_data_lines:
                sh.write(line + "\n")
        with open("run", "a+") as f1:
            info = popen(f'qsub -v path="{python_script}" {QSUB_PATH}').read()
            print("任务ID：", info, end="")
            f1.write(info)
        exit()
    else:
        with open("run", "a+") as f1:
            f1.write(f"start running! {__dt.now()}")
