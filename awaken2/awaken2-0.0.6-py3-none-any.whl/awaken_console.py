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
@ 模块     : 命令行工具
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    该模块适用于辅助 Awaken 进行命令行调用。

"""
import sys

from .baseic.common import window_template_output

from .external.order import instruction_order
from .external.init_engineering import instruction_init_engineering
from .external.create_project import instruction_create_project
from .external.create_task import instruction_create_task
from .external.running_task import instruction_running_task
from .external.running_server import instruction_running_server
from .external.help import instruction_help
from .external.version import instruction_version
from .external.update import instruction_update


# ----------------------------------------------------------------------------
# 命令行工具入口
# ----------------------------------------------------------------------------
def main():
    command = 'order'
    
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        argv    = sys.argv[2:]

    # ------------------------------
    if command in ['order', '-order', '-o']:
        instruction_order()

    # ------------------------------
    elif command in ['init', '-init', '-i']:
        instruction_init_engineering()

    # ------------------------------
    elif command in ['make', '-make', '-m']:
        instruction_create_project(argv)

    # ------------------------------
    elif command in ['task', '-task', '-t']:
        instruction_create_task(argv)

    # ------------------------------
    elif command in ['run', '-run', '-r']:
        instruction_running_task(argv)

    # ------------------------------
    elif command in ['server', '-server', '-s']:
        instruction_running_server(argv)

    # ------------------------------
    elif command in ['help', '-help', '-h']:
        instruction_help()

    # ------------------------------
    elif command in ['version', '-version', '-v']:
        instruction_version()

    # ------------------------------
    elif command in ['update', '-update', '-u']:
        instruction_update()

    else:
        window_template_output(
            [
                f'没有这样的指令:: [{command}] !'
            ]
        )
        exit(0)
