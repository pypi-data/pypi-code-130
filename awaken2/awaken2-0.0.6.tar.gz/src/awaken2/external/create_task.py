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
from ..baseic.const import CONST
from ..baseic.common import create_task
from ..baseic.common import window_template_output


def instruction_create_task(argv: list):
    """
    [ 命令行指令::创建任务 ]

    ---
    参数:
        argv { list } : 参数列表

    """
    dialog_box_title = '- 创建任务 -'

    if len(argv) >= 2:
        task_type: str = argv[0]
        if task_type.upper() == CONST.Type.Task.Web:
            ...
        else:
            window_template_output(
                [
                    dialog_box_title,
                    None,
                    '创建任务指令参数异常:',
                    '暂不支持的任务类型 !'
                ]
            )
            exit(0)

        success = []
        unsuccess = []
        for name in argv[1:]:
            result = create_task(name, task_type)
            if result:
                success.append(name)
            else:
                unsuccess.append(name)

            template = [
                dialog_box_title,
                None,
            ]
            if len(success) > 0:
                template.append('任务创建成功:')
                for name in success:
                    template.append(name)

            if len(unsuccess) > 0:
                if len(success) > 0:
                    template.append(None)
                template.append('任务创建失败:')
                for name in unsuccess:
                    template.append(name)

        window_template_output(template)

    else:
        window_template_output(
            [
                '- 创建任务 -',
                None,
                '创建任务指令参数异常:',
                None,
                '示例:',
                '>> awaken -task web task',
                '>> awaken -task web task1 task2',
                None,
                '目前支持的任务类型:',
                'web : WEB功能测试任务',
                'api : API功能测试任务',
            ]
        )
        exit(0)
