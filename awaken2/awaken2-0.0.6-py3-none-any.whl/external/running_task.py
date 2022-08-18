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
@ 模块     : 命令行指令::运行任务
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from ..baseic.const import CONST
from ..baseic.common import window_template_output
from ..core.perform.perform_pool import PerFormPool
from ..core.interpreter.grammar_parser import GrammarParser


def instruction_running_task(argv: list):
    """
    [ 命令行指令::运行任务 ]

    ---
    参数:
        argv { list } : 参数列表

    """
    dialog_box_title = '- 运行任务 -'
    task_list = []

    if len(argv) >= 1:

        if not CONST.Path.FilePath.Init.exists():
            window_template_output(
                [
                    dialog_box_title,
                    None,
                    '当前运行路径不是工程根目录;',
                    '请在工程根目录执行该命令.'
                ]
            )
            exit(0)
        
        # 循环解析任务参数
        for task_arg in argv:
            if task_arg in ['.', '/', './', 'all', 'ALL']:
                task_arg_path = CONST.Path.CWD
                task_projects = list(task_arg_path.glob('*'))
                for dir in task_projects:
                    project_ini = dir.joinpath(CONST.Name.FileName.ProjectInit)
                    if project_ini.exists():
                        awaken_list = dir.glob(f'*.awaken-*')
                        for awaken_file in awaken_list:
                            task_list.append(awaken_file)
            else:
                task_arg_path = CONST.Path.CWD.joinpath(task_arg)

            # 如果参数路径指向目录
            if task_arg_path.is_dir():
                awaken_list = task_arg_path.glob(f'*.awaken-*')
                for awaken_file in awaken_list:
                    task_list.append(awaken_file)

            # 如果参数路径指向文件
            else:
                if task_arg_path.exists():
                    task_list.append(task_arg_path)

        print(task_list)
        if len(task_list) < 1:
            window_template_output(
                [
                    dialog_box_title,
                    None,
                    '暂无任务可供执行 !',
                ]
            )
            exit(0)

        # 多进程执行任务
        window_template_output(
            [
                dialog_box_title,
                None,
                '多进程执行器正在消耗任务...',
            ]
        )
        grammar_parser = GrammarParser()
        perform_pool = PerFormPool()
        for task in task_list:
            task = grammar_parser.parsing(task)
            perform_pool.put_task(task)
        perform_pool.running()

    else:
        window_template_output(
            [
                dialog_box_title,
                None,
                '运行项目指令参数异常:',
                None,
                '示例:',
                '>> awaken -run task1',
                '>> awaken -run task1 task2',
                '>> awaken -run task1 task2 project1',
                '>> awaken -run .',
            ]
        )
        exit(0)
