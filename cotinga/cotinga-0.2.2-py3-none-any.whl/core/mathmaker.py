# -*- coding: utf-8 -*-

# Cotinga helps maths teachers creating worksheets
# and managing pupils' progression.
# Copyright 2018-2022 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Cotinga.

# Cotinga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Cotinga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Cotinga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import json
import subprocess
from pathlib import Path

DEFAULT_TEX_FILENAMES = {'en_US': {'01_white1_exam': 'white1',
                                   '02_white2_exam': 'white2',
                                   '03_yellow_exam': 'yellow0',
                                   '04_yellow1_exam': 'yellow1',
                                   '05_yellow2_exam': 'yellow2',
                                   '06_orange_exam': 'orange0', },
                         'fr_FR': {'01_white1_exam': 'blanche1',
                                   '02_white2_exam': 'blanche2',
                                   '03_yellow_exam': 'jaune0',
                                   '04_yellow1_exam': 'jaune1',
                                   '05_yellow2_exam': 'jaune2',
                                   '06_orange_exam': 'orange0', }}


def _prefix(use_venv=False, venv=''):
    if use_venv and venv:
        path = str(Path(venv) / 'bin/activate').replace(' ', r'\ ')
        return f"source {path}; "
    else:
        return ''


def is_available(use_venv=False, venv=''):
    cmd = f'{_prefix(use_venv=use_venv, venv=venv)}mathmaker --version'
    ret_code = subprocess.run(cmd, shell=True, executable='/bin/bash',
                              capture_output=True).returncode
    if ret_code:
        return False
    return True


def available_levels(use_venv=False, venv=''):
    """mathmaker is assumed to be available"""
    cmd = f'{_prefix(use_venv=use_venv, venv=venv)}mathmaker list | grep exam'
    result = subprocess.run(cmd, shell=True, executable='/bin/bash',
                            capture_output=True, text=True).stdout
    return [line.strip().split()[-1] for line in result.split('\n') if line]


def belt_filename(belt, language='en_US'):
    return DEFAULT_TEX_FILENAMES[language][belt]


def create_template(belt, cot_level, use_venv=False, venv='',
                    language='en_US', dest_dir=''):
    name = belt_filename(belt, language)
    of = f'{name}.tex'.replace(' ', r'\ ')
    dest_dir = str(dest_dir).replace(' ', r'\ ')
    options = f'--shift {belt} --cotinga-template "{cot_level}"'
    cmd = f'cd {dest_dir}; {_prefix(use_venv=use_venv, venv=venv)}'\
        f'mathmaker {options} > {of}'
    print(f'cmd={cmd}')
    return subprocess.run(cmd, shell=True, executable='/bin/bash',
                          capture_output=True).returncode


def get_user_config(use_venv=False, venv=''):
    cmd = f'{_prefix(use_venv=use_venv, venv=venv)}mathmaker config'
    stdout = subprocess.run(cmd, shell=True, executable='/bin/bash',
                            capture_output=True, text=True).stdout
    return json.loads(stdout)


def compile_tex_file(belt, language='en_US', directory=''):
    name = belt_filename(belt, language)
    p = subprocess.Popen(['lualatex', '-interaction',
                          'nonstopmode', name],
                         cwd=str(directory),
                         stdout=sys.stderr)
    return p.wait()
