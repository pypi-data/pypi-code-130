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
@ 模块     : 底层编码转换程序
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    读取 Awaken 脚本时, 该程序会将其文本编译成一种对于执行处理器来说更加底层的编码;
    这样做的目的在于节约重复读取脚本时的性能开支, 以及利于后续的解析执行。

    底层编码会以文件的格式保存在当前自动化项目的 Data/BaseCode 目录中;
    底层编码文件会根据脚本文件的命名与最后更新时间按照一定规则生成底层编码命名;
    读取 Awaken 脚本时, 如果存在底层编码文件则读取, 否则才会创建新的底层编码文件。

"""
import string
from pathlib import Path

from ...baseic.const import CONST
from ...baseic.common import encrypt_md5
from ...baseic.error import AwakenAnalysisBaseCodeError
from ...kit.common import ENGINE_TYPE_FUNCTION_MAP
from ...kit.global_method_map import GLOBAL_METHOD_FUNCTION_MAP


class BaseCodeConverter: ...


class BaseCodeConverter:
    """
    [ 底层编码转换程序 ]

    ---
    描述:
        用以解读 Awaken 脚本。

    """

    _temp_task_type: str
    """ 寄存器::任务类型 """
    _temp_translations: list
    """ 寄存器::译文列表 """
    _temp_decorators: list
    """ 寄存器::装饰器列表 """
    _temp_action_scope: str
    """ 寄存器::当前作用域 """
    _temp_case_is_assert: bool
    """ 寄存器::当前用例是否断言 """
    _temp_case_name: str = None
    """ 寄存器::当前用例名称 """
    _temp_codeline: str = None
    """ 寄存器::当前代码文本 """
    _temp_codeline_type: str = None
    """ 寄存器::当前代码类型 """
    _temp_codeline_number: int = None
    """ 寄存器::当前代码行数 """


    def convert(self, script_file_path: str | Path) -> tuple[str, list[str]]:
        """
        [ 转换 ]

        ---
        描述:
            解析Awaken脚本文件, 将其编译为底层编码文件。
        
        ---
        参数:
            script_file_path { str | Path } : Awaken脚本文件路径对象。

        ---
        返回:
            tuple[str, list[str]] : 任务类型 & 底层编码列表
        
        """
        self._temp_translations   = []
        self._temp_decorators     = []
        self._temp_action_scope   = CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE
        self._temp_case_is_assert = True

        script_fpath = script_file_path if isinstance(script_file_path, Path) else Path(script_file_path)
        self._temp_task_type = script_fpath.suffix.split('-')[1].upper()

        # --------------------------------------------------------------------
        # 创建脚本文件对应的底层编码文件路径对象
        # 命名规则: 脚本名-(脚本最后更新时间MD5码)-(脚本文件后缀)-basecode
        #
        # 底层编码文件不存在则尝试清理同名的历史底层编码文件, 然后重新编译脚本
        # --------------------------------------------------------------------
        basecode_fpath = CONST.Path.DirPath.BaseCode.joinpath(''.join([
            script_fpath.stem, 
            CONST.Interpreter.SYMBOL_BASECODE_FILE_SEPARATOR,
            encrypt_md5(str(script_fpath.stat().st_mtime)),
            script_fpath.suffix,
            CONST.Interpreter.SYMBOL_BASECODE_FILE_SEPARATOR,
            CONST.Interpreter.KEYWORD_BASECODE_FILE_SUFFIX
        ]))

        if not basecode_fpath.exists():
            for i in CONST.Path.DirPath.BaseCode.glob(f'{ script_fpath.stem }*'):
                if i.stem.split(CONST.Interpreter.SYMBOL_BASECODE_FILE_SEPARATOR)[0] == script_fpath.stem:
                    i.unlink()
                    break
            basecode_fpath.touch(0o777)
            try:
                self._parsing_script_and_write_codeline_file(script_fpath, basecode_fpath)
            except AwakenAnalysisBaseCodeError:
                basecode_fpath.unlink()
                raise

        # 读取底层编码文件并处理成列表
        translations = basecode_fpath.read_text(encoding='UTF-8')
        translations = [codeline for codeline in translations.split('\n') if codeline != '']
        return self._temp_task_type, translations


    def _parsing_script_and_write_codeline_file(self, script_fpath: Path, basecode_fpath: Path) -> None:
        """
        [ 解析脚本并写入文件 ]

        ---
        描述:
            NULL

        ---
        参数:
            script_fpath   { Path } : Awaken 脚本文件路径对象
            basecode_fpath { Path } : 底层编码文件路径对象
        
        """
        # 读取脚本文件
        with open(script_fpath, 'r', encoding='UTF-8') as f:
            content = f.readlines()

        self._temp_codeline_number = 1
        for codeline in content:

            # 清除换行符与注释内容
            codeline = codeline.strip().replace('\n', '')
            try:
                index = codeline.index(CONST.Interpreter.GrammarSymbol.Annotation)
            except ValueError:
                ...
            else: 
                codeline = codeline[0:index]

            # 代码文本不为空则解析
            if len(codeline) > 1:
                self._temp_codeline = codeline
                self._parse_currently_statement()

            self._temp_codeline_number += 1

        if not self._temp_case_is_assert:
            raise AwakenAnalysisBaseCodeError(CONST.Error.Interpreter.GrammarUseCaseNoAssertion.replace('#CASE_NAME#', self._temp_case_name))

        # 写入底层编码文件
        with basecode_fpath.open('a', encoding='UTF-8') as f:
            for translation in self._temp_translations:
                f.write(''.join([translation, '\n']))
                
        self._temp_translations.clear()


    def _parse_currently_statement(self) -> None:
        """
        [ 解析当前语句 ]

        ---
        描述:
            NULL

        """
        # 拆解关键字, 如果只有一个关键字则将其解析为执行语句
        keywords = [keyword for keyword in self._temp_codeline.split(' ') if keyword != '']
        if len(keywords) == 1:
            self._parse_logic_running()

        # 解析当前语句中的首个符号
        # 根据符号执行对应的解析逻辑
        else:
            symbol = self._parse_symbol(self._temp_codeline)

            try:
                {
                    # 赋值逻辑
                    CONST.Interpreter.GrammarSymbol.Give: self._parse_logic_give,

                    # 声明逻辑
                    CONST.Interpreter.GrammarSymbol.Statement: self._parse_logic_statement,

                    # 执行逻辑
                    CONST.Interpreter.GrammarSymbol.Run: self._parse_logic_running,

                    # 断言逻辑
                    CONST.Interpreter.GrammarSymbol.Assert: self._parse_logic_assert,
                    
                }[symbol]()
            
            except KeyError:
                raise AwakenAnalysisBaseCodeError(CONST.Error.Interpreter.GrammarSymbolWrongful.replace('#SYMBOL#', symbol))


    def _parse_logic_give(self):
        """
        [ 解析逻辑 :: 赋值 ]

        ---
        描述:
            NULL

        """
        # 拆解关键字
        kkey, kvalue = [keyword.replace(' ', '') for keyword in self._temp_codeline.split(CONST.Interpreter.GrammarSymbol.Give, 1)]

        # --------------------------------------------------------------------
        # 获取值中的方法执行符号的数量
        # 若方法执行符号为  0 则走赋值逻辑
        # 若方法执行符号为 !0 则走执行赋值逻辑
        # --------------------------------------------------------------------
        kvalue_call_symbol_count = kvalue[0:2].count(CONST.Interpreter.GrammarSymbol.Call)
        kvalue = kvalue[kvalue_call_symbol_count:]
        kvalue_split = kvalue.split(CONST.Interpreter.GrammarSymbol.Run)

        if kvalue_split[0] in [*GLOBAL_METHOD_FUNCTION_MAP.keys(), *ENGINE_TYPE_FUNCTION_MAP[self._temp_task_type].keys()]:
            self._temp_codeline_type = CONST.Interpreter.CodeLineType.RGive

            if kvalue_call_symbol_count != 0:
                function_region = CONST.Interpreter.CodeLineScopet.Global
            else:
                if self._temp_action_scope == CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE:
                    function_region = CONST.Interpreter.CodeLineScopet.Global
                else:
                    function_region = CONST.Interpreter.CodeLineScopet.Local

            function_keywords = []
            for value in kvalue_split:
                function_keywords.append(value)

            function_name = ''.join([function_region, CONST.Interpreter.GrammarSymbol.ScopePrefix, function_keywords[0]])
            kvalue = [keyword for keyword in [function_name, *function_keywords[1:]]]

        else:
            self._temp_codeline_type = CONST.Interpreter.CodeLineType.Give

        # --------------------------------------------------------------------
        # 赋值处理阶段
        # 获取键中资源引用符的数量并通过该值分析赋值作用域
        # --------------------------------------------------------------------
        kkey_quote_symbol_count = kkey[0:2].count(CONST.Interpreter.GrammarSymbol.Quote)
        give_value = []
        if not isinstance(kvalue, list):
            give_value.append(kvalue)
        else:
            for value in kvalue:
                give_value.append(value)

        if kkey_quote_symbol_count != 0:
            give_region = CONST.Interpreter.CodeLineScopet.Global
        else:
            if self._temp_action_scope == CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE:
                give_region = CONST.Interpreter.CodeLineScopet.Global
            else:
                give_region = CONST.Interpreter.CodeLineScopet.Local

        key_name = ''.join([give_region, CONST.Interpreter.GrammarSymbol.ScopePrefix, kkey[kkey_quote_symbol_count:]])
        translation = self._splice_translation([key_name, *give_value])
        self._temp_translations.append(translation)


    def _parse_logic_statement(self):
        """
        [ 解析逻辑 :: 声明 ]

        ---
        描述:
            NULL

        """
        # 拆解关键字
        kkey, kvalue = [keyword.replace(' ', '') for keyword in self._temp_codeline.split(CONST.Interpreter.GrammarSymbol.Statement, 1)]

        # --------------------------------------------------------------------
        # 校验参数与上一个用例是否完成断言
        # --------------------------------------------------------------------
        if kvalue == '':
            error_message = CONST.Error.Interpreter.GrammarStatementNoParameters.replace('#KEYWORD#', kkey)
            if kkey not in [
                CONST.Interpreter.StatementIdent.Case, 
                CONST.Interpreter.StatementIdent.Deco
            ]:
                error_message = CONST.Error.Interpreter.GrammarStatementWrongful.replace('#KEYWORD#', kkey)
            raise AwakenAnalysisBaseCodeError(error_message)

        if not self._temp_case_is_assert:
            raise AwakenAnalysisBaseCodeError(CONST.Error.Interpreter.GrammarUseCaseNoAssertion.replace('#CASE_NAME#', self._temp_case_name))
        
        # --------------------------------------------------------------------
        # 声明用例类型
        # --------------------------------------------------------------------
        if kkey == CONST.Interpreter.StatementIdent.Case:
            self._temp_codeline_type = CONST.Interpreter.CodeLineType.SCase
            kvalues = kvalue.split(CONST.Interpreter.GrammarSymbol.Statement, 1)
            self._temp_case_name = kvalues[0]
            self._temp_case_is_assert = False
            translation = self._splice_translation(kvalues)
            self._temp_translations.append(translation)

            # 如果装饰器声明语句列表不为空, 则替换作用域为用例名称并写入
            if len(self._temp_decorators) > 0:
                for decorator in self._temp_decorators:
                    self._temp_translations.append(decorator.replace(CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE, self._temp_case_name))
                self._temp_decorators.clear()

        # --------------------------------------------------------------------
        # 声明装饰器类型
        # --------------------------------------------------------------------
        elif kkey == CONST.Interpreter.StatementIdent.Deco:
            self._temp_codeline_type = CONST.Interpreter.CodeLineType.SDecorator
            kvalues = kvalue.split(CONST.Interpreter.GrammarSymbol.Statement, 1)
            translation = self._splice_translation(kvalues)
            self._temp_decorators.append(translation)


    def _parse_logic_running(self):
        """
        [ 解析逻辑 :: 执行 ]

        ---
        描述:
            NULL

        """
        self._temp_codeline_type = CONST.Interpreter.CodeLineType.Run
        
        # 拆解关键字
        kkey, *kvalue = [keyword.replace(' ', '') for keyword in self._temp_codeline.split(CONST.Interpreter.GrammarSymbol.Run)]

        # --------------------------------------------------------------------
        # 获取方法名中的方法调用符的数量
        # 若方法调用符号为  0 则使用全局方法
        # 若方法调用符号为 !0 则使用引擎方法
        # --------------------------------------------------------------------
        kkey_call_symbol_count = kkey.count(CONST.Interpreter.GrammarSymbol.Call)

        if kkey_call_symbol_count != 0:
            function_region = CONST.Interpreter.CodeLineScopet.Global
        else:
            if self._temp_action_scope == CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE:
                function_region = CONST.Interpreter.CodeLineScopet.Global
            else:
                function_region = CONST.Interpreter.CodeLineScopet.Local

        function_name = ''.join([function_region, CONST.Interpreter.GrammarSymbol.ScopePrefix, kkey[kkey_call_symbol_count:]])
        kvalue = [keyword for keyword in [function_name, *kvalue]]
        translation = self._splice_translation(kvalue)
        self._temp_translations.append(translation)


    def _parse_logic_assert(self):
        """
        [ 解析逻辑 :: 断言 ]

        ---
        描述:
            NULL

        """
        # 暂时每个 CASE 只会解析一条断言语句
        if self._temp_case_name:
            self._temp_codeline_type = CONST.Interpreter.CodeLineType.Assert
            keywords = [keyword for keyword in self._temp_codeline.split(CONST.Interpreter.GrammarSymbol.Assert, 1)]
            keywords = [keyword for keyword in keywords[1].split(' ') if keyword != '']
            translation = self._splice_translation(keywords)
            self._temp_translations.append(translation)
            self._temp_case_name = None
            self._temp_case_is_assert = True


    def _parse_symbol(self, codeline: str):
        """
        [ 解析代码行中的首个符号 ]

        ---
        描述:
            NULL

        """
        slicing = [i for i in codeline.split(' ') if i != '']
        for element in slicing:
            symbol = ''
            for str in element:
                if str not in string.punctuation: 
                    symbol = ''
                    break
                else:
                    symbol += str

            if len(symbol) != 0:
                return symbol


    def _splice_translation(self, keywords: list):
        """
        [ 拼接最终编码 ]

        ---
        描述:
            NULL
            
        """
        self._temp_action_scope = self._temp_case_name if self._temp_case_name else CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE

        if self._temp_codeline_type == CONST.Interpreter.CodeLineType.SCase:
            translation = f'{ self._temp_codeline_number } { CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE } { self._temp_codeline_type }'
        else:
            translation = f'{ self._temp_codeline_number } { self._temp_action_scope } { self._temp_codeline_type }'
        
        for key in keywords:
            translation += f' { key }'

        return translation
