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
@ 模块     : 自定义异常
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import re

from ..baseic.message_recorder import MESSAGE_RECORDER


class _AwakenBaseError(Exception):
    """ 
    [ 自定义异常基类 ]
    
    """

    def __init__(self, error_message: str):
        self.err_name = re.findall(r'\[ (.*) \]', self.__doc__)[0]
        self.message = ''.join([self.err_name, '::', str(error_message)])
        MESSAGE_RECORDER.record(self.message)

    def __str__(self) -> str:
        return self.message


class AwakenLogCreationError(_AwakenBaseError):
    """
    [ 日志创建异常 ]
    
    """


class AwakenLogOutputError(_AwakenBaseError):
    """
    [ 日志输出异常 ]
    
    """


class AwakenWebEngineError(_AwakenBaseError):
    """
    [ WEB引擎异常 ]
    
    """


class AwakenApiEngineError(_AwakenBaseError):
    """
    [ API引擎异常 ]
    
    """


class AwakenConvertCodelinError(_AwakenBaseError):
    """
    [ 转换代码行异常 ]
    
    """


class AwakenAnalysisBaseCodeError(_AwakenBaseError):
    """
    [ 解读底层编码异常 ]
    
    """


class AwakenTaskPretreatmentError(_AwakenBaseError):
    """
    [ 任务预处理异常 ]
    
    """

class AwakenWebApiServerError(_AwakenBaseError):
    """
    [ WebApi服务器异常 ]
    
    """


class AwakenDataBaseError(_AwakenBaseError):
    """
    [ 数据库异常 ]
    
    """


class AwakenWebEngineRunError(_AwakenBaseError):
    """
    [ WEB引擎运行异常 ]
    
    """

