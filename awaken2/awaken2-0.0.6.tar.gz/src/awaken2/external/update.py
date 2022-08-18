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
@ 模块     : 命令行指令::更新版本   
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import re
import subprocess

from ..awaken_info import ProjectInfo
from ..baseic.common import window_template_output


def instruction_update():
    """
    [ 命令行指令::更新版本 ]

    ---
    参数:
        argv { list } : 参数列表

    """
    dialog_box_title = '- 更新版本 -'
    window_template_output(
        [
            dialog_box_title,
            None,
            '正在查询 PYPI 服务器...',
        ]
    )

    dos_result = subprocess.Popen(['pip', 'install', f'{ ProjectInfo.Name }=='], stderr=subprocess.PIPE)
    _, err = dos_result.communicate()
    newest_version: str = re.findall(r'from versions: (.*)\)', str(err))[0].split(',')[-1].strip()

    if newest_version > ProjectInfo.Version:
        window_template_output(

            [
                dialog_box_title,
                None,
                f'从 PYPI 中发现最新版本号: {newest_version}',
                None,
                '正在执行更新程序...',
                None,
                f'{ProjectInfo.Version} >> {newest_version}',
            ]
        )
        dos_result = subprocess.Popen(['pip', 'install', '--upgrade', ProjectInfo.Name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dos_result.communicate()

        window_template_output(
            [
                dialog_box_title,
                None,
                f'当前为最新版本号:: {newest_version}',
                None,
                '已完成更新...',
            ]
        )
    else:
        window_template_output(
            [
                dialog_box_title,
                None,
                f'当前为最新版本号:: {newest_version}',
                None,
                '暂无更新...',
            ]
        )
        exit(0)
