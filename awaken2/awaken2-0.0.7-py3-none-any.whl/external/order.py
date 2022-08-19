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
@ 模块     : 命令行指令::指令集
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from ..baseic.common import window_template_output


def instruction_order():
    """
    [ 命令行指令::指令集 ]

    """
    dialog_box_title = '- 指令集 -'

    window_template_output(
        [
            dialog_box_title,
            None,
            '-init    |  -i  |  工程初始化',
            '-make    |  -m  |  创建项目',
            '-task    |  -t  |  创建任务',
            '-run     |  -r  |  运行任务',
            '-server  |  -s  |  运行服务器',
            '-help    |  -h  |  查看帮助',
            '-version |  -v  |  查看版本',
            '-update  |  -u  |  更新版本',
        ]
    )
    exit(0)
