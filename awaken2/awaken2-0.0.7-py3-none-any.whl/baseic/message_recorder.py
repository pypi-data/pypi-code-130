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
from .decorator import singleton_pattern


class MessageRecorder: ...


@singleton_pattern
class MessageRecorder:
    """
    [ 错误记录器 ]

    ---
    描述:
        NULL

    """
    _error_warehouse: list
    """ 错误信息仓库 """

    def __init__(self) -> None:
        self._error_warehouse = []


    def record(self, message: str) -> None:
        """
        [ 记录 ]

        ---
        描述:
            NULL

        ---
        参数:
            message { str } : 记录信息文本

        """
        self._error_warehouse.append(message)


    def read(self) -> None:
        """
        [ 读取 ]

        ---
        描述:
            NULL

        """
        return self._error_warehouse


    def template_print(self) -> None:
        """
        [ 模板打印 ]

        ---
        描述:
            NULL

        """
        sym1 = '━'
        sym2 = '┃'
        sym3 = '┏'
        sym4 = '┗'
        sym5 = '┓'
        sym6 = '┛'
        tab_max_len = 50
        error_list = ['异常信息列表', ' ']
        error_number = 0

        # 处理初始错误信息
        for error in self._error_warehouse:
            error_list.append(f'error {error_number} ::')
            if len(error) > tab_max_len:
                while 1:
                    error_list.append(error[0: tab_max_len-3])
                    error = error[tab_max_len-3:]
                    error_list.append(error)
                    if len(error) >= tab_max_len:
                        continue
                    else:
                        error_list.append(error[tab_max_len-3:])
                        error_number += 1
                        break
            else:
                error_list.append(error)
                error_number += 1
            
            error_list.append(' ')

        # 消除空字符
        error_list = [error.replace(' ', '') for error in error_list if error != '']

        # 制表
        print(sym3 + sym1*(tab_max_len*2 + 3 - 20) + sym5)
        for error in error_list:
            offset = 0
            for s in error:
                if not u'\u4e00' <= s <= u'\u9fff':
                    offset += 1
            n = ' '*((tab_max_len*2 - len(error)*2 - 20) + offset)
            print(f'{sym2} {error} {n} {sym2}')
        print(sym4 + sym1*(tab_max_len*2 + 3 - 20) + sym6)



MESSAGE_RECORDER = MessageRecorder()
""" 错误记录器实例 """
