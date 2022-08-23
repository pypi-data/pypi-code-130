import shlex
import subprocess

from ipynb_strip_copy import *
from prep import json_from_ipynb

file_test = 'test_case_in.ipynb'
file_expect = 'test_case_out.ipynb'

json_dict_in = json_from_ipynb(file_test)
json_dict_exp = json_from_ipynb(file_expect)


def test_search_cell():
    for str_target, cell_line_exp in ('clearme', [2, 3]), \
                                     ('DELETEME', [4, 5]):
        cell_list_obs = list(search_cell(json_dict_in, str_target))
        assert cell_line_exp == cell_list_obs


def strip_id(json_dict):
    """ removes 'id' key per cell ... neednt match """
    for d in json_dict['cells']:
        if 'id' in d:
            del d['id']


def test_search_act():
    target_act_list = [('keep-this', Action.RM_COMPLEMENT),
                       ('CLEARME', Action.CLEAR_CELL),
                       ('DELETEME', Action.RM_CELL)]

    json_dict_obs = search_act(json_dict_in, target_act_list, verbose=True)

    # strip id tag of each cell (needn't match to be correct)
    strip_id(json_dict_obs)
    strip_id(json_dict_exp)

    assert json_dict_exp == json_dict_obs


def test_cli():
    file = 'test_cli_hw_rub.ipynb'
    cmd = shlex.split(f'python3 -m ipynb_strip_copy {file} -t hw')
    subprocess.run(cmd, check=True)
