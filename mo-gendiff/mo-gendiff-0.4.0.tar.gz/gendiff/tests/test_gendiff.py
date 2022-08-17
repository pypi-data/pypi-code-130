import os
from gendiff.run_gendiff import generate_diff


dirrectory = 'gendiff/tests/fixtures'


def make_file_path(file_name):
    return os.path.join(dirrectory, file_name)


def test_diff_json_format():
    file_1_path = make_file_path('file1.json')
    file_2_path = make_file_path('file2.json')
    f = open('gendiff/tests/fixtures/result1.txt', "r")
    assert generate_diff(file_1_path, file_2_path) == f.read()
    f.close()


def test_diff_yaml_format():
    file_1_path = make_file_path('file1.yaml')
    file_2_path = make_file_path('file2.yaml')
    f = open('gendiff/tests/fixtures/result1.txt', "r")
    assert generate_diff(file_1_path, file_2_path) == f.read()
    f.close()


def test_diff_different_formats():
    file_1_path = make_file_path('file1.json')
    file_2_path = make_file_path('file2.yaml')
    f = open('gendiff/tests/fixtures/result1.txt', "r")
    assert generate_diff(file_1_path, file_2_path) == f.read()
    f.close()
    