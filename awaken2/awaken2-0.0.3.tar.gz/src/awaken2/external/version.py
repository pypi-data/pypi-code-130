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
@ 模块     : 命令行指令::版本
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


def instruction_version():
    print('Loading...')
    
    dos_result = subprocess.Popen(f'pip install {ProjectInfo.Name}==', stderr=subprocess.PIPE)
    _, err = dos_result.communicate()
    newest_version = re.findall(r'from versions: (.*)\)', str(err))[0].split(',')[-1].strip()
    
    os.system('cls')
    print(re.sub('&new_version&', newest_version, _DIALOG_BOX))


_DIALOG_BOX = \
f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Awaken2 版本                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                  ┃
┃ 本地当前版本: { ProjectInfo.Version }                              ┃
┃ 线上最新版本: &new_version&                              ┃
┃                                                  ┃
┃ 更新 awaken2 版本请执行下方命令:                 ┃
┃                                                  ┃
┃ awaken2 -update                                  ┃
┃                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
