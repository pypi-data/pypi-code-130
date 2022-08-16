# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ Copyright 2022. quinn.7@foxmail.com All rights reserved.                 ║
# ║                                                                          ║
# ║ Licensed under the Apache License, Version 2.0 (the "License");          ║
# ║ you may not use this file except in compliance with the License.         ║
# ║ You may obtain a copy of the License at                                  ║
# ║                                                                          ║
# ║ http://www.apache.org/licenses/LICENSE-2.0                               ║
# ║                                                                          ║
# ║ Unless required by applicable law or agreed to in writing, software      ║
# ║ distributed under the License is distributed on an "AS IS" BASIS,        ║
# ║ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. ║
# ║ See the License for the specific language governing permissions and      ║
# ║ limitations under the License.                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
"""
@ 模块     : 命令行指令::创建任务
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os

from pathlib import Path

from ..baseic.const import CONST


TEMPLATE_WEB_TASK_PATH = 'task_template\\web_task_template.awaken-web'


def instruction_create_task(argv: list):
    """
    [ 命令行指令::创建任务 ]

    ---
    参数:
        argv { list } : 参数列表

    """
    if len(argv) >= 2:
        task_type: str = argv[0].upper()
        if task_type == CONST.Type.Task.Web:
            task_template_path = Path(os.path.split(os.path.realpath(__file__))[0]).joinpath(TEMPLATE_WEB_TASK_PATH)
        else:
            print(_DIALOG_BOX2)
            exit(0)

        for name in argv[1:]:
            task_name = f'{name}{task_template_path.suffix}'
            task_path = CONST.Path.CWD.joinpath(task_name)
            if not task_path.exists():
                task_template_bytes = task_template_path.read_bytes()
                task_path.touch(mode=0o777)
                task_path.write_bytes(task_template_bytes)
                print(_DIALOG_BOX3)
            else:
                print(_DIALOG_BOX4)

    else:
        print(_DIALOG_BOX1)
        exit(0)


_DIALOG_BOX1 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 创建任务指令参数异常:                            ┃
┃                                                  ┃
┃ 示例:                                            ┃
┃ >> awaken -make web task                         ┃
┃ >> awaken -make web task1 task2                  ┃
┃                                                  ┃
┃ 目前支持的任务类型:                              ┃
┃ web : WEB功能测试任务                            ┃
┃ api : API功能测试任务                            ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

_DIALOG_BOX2 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 创建任务指令参数异常:                            ┃
┃                                                  ┃
┃ 暂不支持的任务类型 !                             ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

_DIALOG_BOX3 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 任务创建成功 !                                   ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

_DIALOG_BOX4 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 任务创建失败 !                                   ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
