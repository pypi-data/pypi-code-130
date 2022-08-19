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
@ 模块     : 命令行指令::创建项目   
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from ..baseic.common import create_project
from ..baseic.common import window_template_output


def instruction_create_project(argv: list):
    """
    [ 命令行指令::创建项目 ]

    ---
    参数:
        argv { list } : 参数列表

    """
    dialog_box_title = '- 创建项目 -'

    if len(argv) >= 1:
        success   = []
        unsuccess = []
        for pname in argv[0:]:
            result = create_project(pname)
            if result:
                success.append(pname)
            else:
                unsuccess.append(pname)

            template = [
                dialog_box_title,
                None,
            ]
            if len(success) > 0:
                template.append('项目创建成功:')
                for pname in success:
                    template.append(pname)

            if len(unsuccess) > 0:
                if len(success) > 0:
                    template.append(None)
                template.append('项目创建失败:')
                for pname in unsuccess:
                    template.append(pname)

        window_template_output(template)

    else:
        window_template_output(
            [
                dialog_box_title,
                None,
                '创建项目指令参数异常:',
                None,
                '示例:',
                '>> awaken -make project',
                '>> awaken -make project1 project2',
            ]
        )
        exit(0)
