# Copyright 2012-2019 The Meson development team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Representations specific to the Texas Instruments compiler family."""

import os
import typing as T

from ...mesonlib import EnvironmentException

if T.TYPE_CHECKING:
    from ...environment import Environment
    from ...compilers.compilers import Compiler
else:
    # This is a bit clever, for mypy we pretend that these mixins descend from
    # Compiler, so we get all of the methods and attributes defined for us, but
    # for runtime we make them descend from object (which all classes normally
    # do). This gives up DRYer type checking, with no runtime impact
    Compiler = object

ti_buildtype_args = {
    'plain': [],
    'debug': [],
    'debugoptimized': [],
    'release': [],
    'minsize': [],
    'custom': [],
}  # type: T.Dict[str, T.List[str]]

ti_optimization_args = {
    '0': ['-O0'],
    'g': ['-Ooff'],
    '1': ['-O1'],
    '2': ['-O2'],
    '3': ['-O3'],
    's': ['-O4']
}  # type: T.Dict[str, T.List[str]]

ti_debug_args = {
    False: [],
    True: ['-g']
}  # type: T.Dict[bool, T.List[str]]


class TICompiler(Compiler):

    id = 'ti'

    def __init__(self) -> None:
        if not self.is_cross:
            raise EnvironmentException('TI compilers only support cross-compilation.')

        self.can_compile_suffixes.add('asm')    # Assembly
        self.can_compile_suffixes.add('cla')    # Control Law Accelerator (CLA) used in C2000

        default_warn_args = []  # type: T.List[str]
        self.warn_args = {'0': [],
                          '1': default_warn_args,
                          '2': default_warn_args + [],
                          '3': default_warn_args + []}  # type: T.Dict[str, T.List[str]]

    def get_pic_args(self) -> T.List[str]:
        # PIC support is not enabled by default for TI compilers,
        # if users want to use it, they need to add the required arguments explicitly
        return []

    def get_buildtype_args(self, buildtype: str) -> T.List[str]:
        return ti_buildtype_args[buildtype]

    def get_pch_suffix(self) -> str:
        return 'pch'

    def get_pch_use_args(self, pch_dir: str, header: str) -> T.List[str]:
        return []

    def thread_flags(self, env: 'Environment') -> T.List[str]:
        return []

    def get_coverage_args(self) -> T.List[str]:
        return []

    def get_no_stdinc_args(self) -> T.List[str]:
        return []

    def get_no_stdlib_link_args(self) -> T.List[str]:
        return []

    def get_optimization_args(self, optimization_level: str) -> T.List[str]:
        return ti_optimization_args[optimization_level]

    def get_debug_args(self, is_debug: bool) -> T.List[str]:
        return ti_debug_args[is_debug]

    def get_compile_only_args(self) -> T.List[str]:
        return []

    def get_no_optimization_args(self) -> T.List[str]:
        return ['-Ooff']

    def get_output_args(self, target: str) -> T.List[str]:
        return [f'--output_file={target}']

    def get_werror_args(self) -> T.List[str]:
        return ['--emit_warnings_as_errors']

    def get_include_args(self, path: str, is_system: bool) -> T.List[str]:
        if path == '':
            path = '.'
        return ['-I=' + path]

    @classmethod
    def unix_args_to_native(cls, args: T.List[str]) -> T.List[str]:
        result = []
        for i in args:
            if i.startswith('-D'):
                i = '--define=' + i[2:]
            if i.startswith('-Wl,-rpath='):
                continue
            elif i == '--print-search-dirs':
                continue
            elif i.startswith('-L'):
                continue
            result.append(i)
        return result

    def compute_parameters_with_absolute_paths(self, parameter_list: T.List[str], build_dir: str) -> T.List[str]:
        for idx, i in enumerate(parameter_list):
            if i[:15] == '--include_path=':
                parameter_list[idx] = i[:15] + os.path.normpath(os.path.join(build_dir, i[15:]))
            if i[:2] == '-I':
                parameter_list[idx] = i[:2] + os.path.normpath(os.path.join(build_dir, i[2:]))

        return parameter_list

    def get_dependency_gen_args(self, outtarget: str, outfile: str) -> T.List[str]:
        return ['--preproc_with_compile', f'--preproc_dependency={outfile}']
