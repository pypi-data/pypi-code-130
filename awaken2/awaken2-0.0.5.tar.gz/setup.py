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
@ 模块     : Setup
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    PIP package manager build script.

"""
from setuptools import setup
from setuptools import find_packages
from src.awaken2.awaken_info import ProjectInfo


# ----------------------------------------------------------------------------
# 项目属性
# ----------------------------------------------------------------------------
NAME        = ProjectInfo.Name
VERSION     = ProjectInfo.Version
AUTHOR      = ProjectInfo.Author
EMAIL       = ProjectInfo.Email
DESCRIPTION = ProjectInfo.Desc
KEYWORDS    = ProjectInfo.Keywords
URL         = ProjectInfo.Url

LEGAL_PY_VERSION = [
    'Programming Language :: Python :: 3.10',
]

with open('README.md', 'r', encoding='UTF-8') as file:
    LONG_DESCRIPTION = file.read()

INSTALL_REQUIRES = [
    'playwright',
    'flask',
]


# ----------------------------------------------------------------------------
# 项目配置
# ----------------------------------------------------------------------------
setup(
    name                          = NAME, 
    version                       = VERSION, 
    author                        = AUTHOR, 
    author_email                  = EMAIL, 
    description                   = DESCRIPTION,
    keywords                      = KEYWORDS,
    url                           = URL,
    classifiers                   = LEGAL_PY_VERSION,
    long_description              = LONG_DESCRIPTION, 
    long_description_content_type = 'text/markdown',
    install_requires              = INSTALL_REQUIRES,
    packages                      = find_packages('src'), 
    package_dir                   = {'' : 'src'},

    entry_points = {
        'console_scripts':[
            'awaken = awaken2.awaken_console:main',
        ],
    },
)
