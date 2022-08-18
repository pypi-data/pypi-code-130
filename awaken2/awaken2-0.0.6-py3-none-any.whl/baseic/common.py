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
@ 模块     : 基础通用模块
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os
import hashlib

from .const import CONST
from ..awaken_info import ProjectInfo
from ..kit.common import TASK_TEMPLATE_MAP


def environment_check_browser_driver_exists():
    """
    [ 环境检查::是否安装浏览器驱动 ]

    ---
    描述:
        NULL

    """
    dialog_box_title = '- 检查本地浏览器驱动 -'
    browsers = ['chromium', 'firefox', 'webkit']
    local_browsers = []

    # ------------------------------------------------------------------------
    # 检查本地 playwright 环境是否安装浏览器驱动
    # 如果浏览器驱动不存在本地则下载
    # ------------------------------------------------------------------------
    if CONST.Path.ENVIRONMENT_VARIABLE in os.environ:
        for dir_path in CONST.Path.PLAYWRIGHT_CACHE_PATH.glob('*'):
            local_browsers.append(dir_path.stem.split('-')[0])

        for browser_name in browsers:
            if browser_name not in local_browsers:
                window_template_output(
                    [
                        dialog_box_title,
                        None,
                        f'正在下载浏览器驱动 >> {browser_name}'
                    ]
                )
                os.system(f'playwright install { browser_name }')


def environment_check_dependent_files_exists():
    """
    [ 环境检查::是否创建工程依赖 ]

    ---
    描述:
        NULL
    
    """
    for path in [
        CONST.Path.DirPath.Data,
        CONST.Path.DirPath.Logs,
        CONST.Path.DirPath.BaseCode,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    for path in [
        CONST.Path.FilePath.Config,
        CONST.Path.FilePath.Database,
    ]:
        path.touch(mode=0o777, exist_ok=True)


def create_project(name: str):
    """
    [ 创建项目 ]

    ---
    参数:
        name { str } : 项目名称

    ---
    返回:
        bool : 是否创建成功凭证
    
    """
    project_path = CONST.Path.CWD.joinpath(name)

    # ------------------------------------------------------------------------
    # 如果项目目录不存在则创建
    # ------------------------------------------------------------------------
    if not project_path.exists():
        project_path.mkdir(parents=True, exist_ok=True)
        project_path.joinpath(CONST.Name.FileName.ProjectInit).touch(0o777)
        return True

    else:
        return False


def create_task(task_name: str, task_type: str):
    """ 
    [ 创建任务 ]

    ---
    参数:
        name { str } : 任务名称

    ---
    返回:
        bool : 是否创建成功凭证
    
    """
    awaken_file_name = f'{task_name}.awaken-{task_type}'
    awaken_file_path = CONST.Path.CWD.joinpath(awaken_file_name)
    task_type_upper = task_type.upper()

    # ------------------------------------------------------------------------
    # 如果任务不存在则创建
    # ------------------------------------------------------------------------
    if not awaken_file_path.exists():
        awaken_file_path.touch(mode=0o777)
        task_template = TASK_TEMPLATE_MAP[task_type_upper]
        task_template = task_template.replace('#TASK_NAME#', task_name)
        task_template = task_template.replace('#TASK_TYPE#', task_type_upper)
        awaken_file_path.write_bytes(bytes(task_template, encoding='UTF8'))
        return True

    else:
        return False


def encrypt_md5(string: str):
    """
    [ MD5加密 ]
    
    ---
    描述:
        NULL

    ---
    参数:
        string { str } : 需要加密的字符串

    """
    file_md5hash = hashlib.md5(string.encode('UTF-8'))
    return file_md5hash.hexdigest()


def window_template_output(message: list, name: str = None):
    """
    [ 窗口模板输出 ]
    
    ---
    描述:
        NULL

    ---
    参数:
        message { list } : 需要输出的文本列表
        name     { str } : 窗口模板名称

    """
    os.system('cls')  # 清空黑框

    max_limit = 50
    if not name:
        name = f'{ProjectInfo.Name} - {ProjectInfo.Version}'

    def calculate_offset(value):
        offset = 0
        for s in value:
            if u'\u4e00' <= s <= u'\u9fff':
                offset += 1
        return offset

    # 绘制窗口模板表格
    print('┏' + '━'*max_limit + '┓')
    print('┃ ' + name + ' '*((max_limit - len(name) - 2) - calculate_offset(name)) + ' ┃')
    print('┣' + '━'*max_limit + '┫')
    print('┃' + ' '*max_limit + '┃')

    for mage in message:
        if not mage:
            print('┃' + ' '*max_limit + '┃')
        else:
            print('┃ ' + mage + ' '*((max_limit - len(mage) - 2) - calculate_offset(mage)) + ' ┃')

    print('┃' + ' '*max_limit + '┃')
    print('┗' + '━'*max_limit + '┛')
