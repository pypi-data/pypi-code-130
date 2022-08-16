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
@ 模块     : 命令行指令::更新   
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os
import re
import subprocess

from ..awaken_info import ProjectInfo


def instruction_update():
    print('Loading...')

    dos_result = subprocess.Popen(['pip', 'install', f'{ ProjectInfo.Name }=='], stderr=subprocess.PIPE)
    _, err = dos_result.communicate()
    newest_version: str = re.findall(r'from versions: (.*)\)', str(err))[0].split(',')[-1].strip()

    os.system('cls')
    if newest_version > ProjectInfo.Version:
        print(re.sub('&new_version&', newest_version, _DIALOG_BOX1))
        dos_result = subprocess.Popen(['pip', 'install', '--upgrade', ProjectInfo.Name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dos_result.communicate()

        os.system('cls')
        print(re.sub('&new_version&', newest_version, _DIALOG_BOX3))
    
    else:
        print(re.sub('&new_version&', newest_version, _DIALOG_BOX2))


_DIALOG_BOX1 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2 更新                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 从 PYPI 中发现最新版本号: &new_version&                  ┃
┃                                                  ┃
┃ 正在执行更新程序...                              ┃
┃                                                  ┃
┃ {ProjectInfo.Version} >> &new_version&                                   ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

_DIALOG_BOX2 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2 更新                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 当前为最新版本号: &new_version&                          ┃
┃                                                  ┃
┃ 暂无更新...                                      ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

_DIALOG_BOX3 = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2 更新                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 当前版本号为: &new_version&                              ┃
┃                                                  ┃
┃ 已完成更新...                                    ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
