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
@ 模块     : Baseic.Common
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os
import hashlib
import subprocess

from pathlib import Path

from .const import CONST


_ENVIRONMENT_VARIABLE = 'USERPROFILE'
_PLAYWRIGHT_PATH = Path(os.environ[_ENVIRONMENT_VARIABLE]).joinpath('AppData\Local\ms-playwright')

TASK_TEMPLATE_WEB = \
"""
## 自述
TaskName = ''
TaskDocs = ''
TaskType = 'WEB'


## 用例
CASE :: TestName :: Docs
    Goto >> 'http://www.baidu.com/'
"""

TASK_TEMPLATE_MAP = {
    CONST.Type.Task.Web : TASK_TEMPLATE_WEB
}


def check_browser_driver_is_installed():
    """
    [ 检查浏览器驱动是否安装 ]

    ---
    描述:
        NULL

    """
    browser_list = ['chromium', 'firefox', 'webkit']
    local_browser_list = []

    # 检查本地 playwright 环境是否安装浏览器驱动
    if _ENVIRONMENT_VARIABLE in os.environ:
        for dir_path in _PLAYWRIGHT_PATH.glob('*'):
            local_browser_list.append(dir_path.stem.split('-')[0])

        # 如果浏览器驱动不存在本地则下载
        for browser_name in browser_list:
            if browser_name not in local_browser_list:
                dos_result = subprocess.Popen(['pip', 'install', f'{ browser_name }'], stderr=subprocess.PIPE)
                dos_result.communicate()
                print(f'正在下载浏览器驱动 :: { browser_name }')
                os.system(f'playwright install { browser_name }')


def create_program_runtime_dependency_files():
    """
    [ 创建程序运行时的依赖文件 ]

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
        CONST.Path.FilePath.Init,
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

    if not project_path.exists():
        project_path.mkdir(parents=True, exist_ok=True)
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
    task_name = f'{task_name}.awaken-{task_type}'
    task_path = CONST.Path.CWD.joinpath(task_name)

    if not task_path.exists():
        task_path.touch(mode=0o777)
        task_path.write_bytes(bytes(TASK_TEMPLATE_MAP[task_type.upper()], encoding='UTF8'))
        return True
    else:
        return False


def md5_encrypt(string: str):
    """
    [ MD5加密 ]
    
    ---
    描述:
        NULL

    ---
    参数:
        string { str } : 需要加密的字符串。

    """
    file_md5hash = hashlib.md5(string.encode('UTF-8'))
    return file_md5hash.hexdigest()


def window_template_output(name: str, message: list):
    os.system('cls')
    max_limit = 50

    def calculate_offset(value):
        offset = 0
        for s in value:
            if u'\u4e00' <= s <= u'\u9fff':
                offset += 1
        return offset

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
