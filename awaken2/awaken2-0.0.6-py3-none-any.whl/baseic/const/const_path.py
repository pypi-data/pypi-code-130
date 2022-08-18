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
@ 模块     : 路径常量
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os

from pathlib import Path

from . import const_name


class DirPath: ...
class FilePath: ...


ENVIRONMENT_VARIABLE = 'USERPROFILE'
""" 系统环境变量匙 :: 用户配置文件 """
PLAYWRIGHT_CACHE_PATH = Path(os.environ[ENVIRONMENT_VARIABLE]).joinpath('AppData\Local\ms-playwright')
""" Path对象 :: Playwright缓存目录路径 """

CWD = Path().cwd()
""" Path对象 :: 运行时路径 """


class DirPath:
    """
    [ 路径常量索引 :: 目录路径对象 ]

    ---
    描述: 
        NULL

    """

    Data = CWD.joinpath(const_name.DirName.EngineeringData)
    """ 数据目录 """

    Logs = Data.joinpath(const_name.DirName.EngineeringLogs)
    """ 日志目录 """

    BaseCode = Data.joinpath(const_name.DirName.EngineeringBaseCode)
    """ 底层编码目录 """


class FilePath:
    """
    [ 路径常量索引 :: 文件路径对象 ]

    ---
    描述: 
        NULL
        
    """

    Init = CWD.joinpath(const_name.FileName.EngineeringInit)
    """ 工程标识文件 """

    Config = DirPath.Data.joinpath(const_name.FileName.EngineeringConfig)
    """ 工程配置文件 """

    Database = DirPath.Data.joinpath(const_name.FileName.EngineeringDatabase)
    """ 工程数据库文件 """
