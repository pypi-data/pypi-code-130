#  Copyright (c) 2022. Curie Zhang, Lanzhou Univ. of Tech.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""这是 nester.py 模块，提供一个名为 print_lol() 的函数，该函数的作用是打印列表，
其中可能包含（也可能不包含）嵌套列表"""


def print_lol(the_list, level=0):
    """这个函数取一个位置参数，名为 the_list，可以是任意 python 列表（也可以是包含嵌套列表的列表）。
    所指定的列表中的每个数据项会（递归地）输出到屏幕上，各数据项各占一行。
    第二个参数（名为 level）用来在遇到嵌套列表时插入制表符。"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)
