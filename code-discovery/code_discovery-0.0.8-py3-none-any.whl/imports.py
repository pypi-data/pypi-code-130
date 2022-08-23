import dis
import os
import re
from io import StringIO
from typing import List, Set, Tuple

IMPORT_NAME_BYTE_CODE = 'IMPORT_NAME'
DIS_ROW_REGEX = r"""\d* \s* ([a-zA-z]*) \s* \d* \s* \((.*)\)"""


def get_data_from_dis_row(dis_row: str) -> Tuple[str, str]:
    """
    @param path: the row from dis.dis
    @return: op code and op value
    """
    search = re.search(DIS_ROW_REGEX, dis_row, re.MULTILINE |
                       re.IGNORECASE | re.VERBOSE)
    return search.groups()


def get_imports_of_file(path: str) -> Set[str]:
    """
    @param path: the file path
    @return: the module names that imported in file
    """

    with open(path, encoding='utf-8') as file_obj:
        code = file_obj.read()

    try:
        f = StringIO()
        dis.dis(code, file=f)
        f.seek(0)
        rows = f.readlines()
        f.close()
    except SyntaxError:
        return set()

    modules = set()
    for row in rows:
        if IMPORT_NAME_BYTE_CODE in row:
            op_code, op_value = get_data_from_dis_row(row)
            if op_code == IMPORT_NAME_BYTE_CODE:
                modules.add(op_value.split('.')[0])
    return modules


def is_project_python_file(directory_path: str, filename: str) -> bool:
    return os.path.splitext(filename)[1] == '.py' and \
           'site-packages' not in directory_path


def get_all_python_files(root_path: str) -> List[str]:
    """
    @param root_path: the root path
    @return: the python file paths under the root path
    """
    project_files = [os.path.join(directory_path, filename)
                     for directory_path, _, filenames in os.walk(root_path)
                     for filename in filenames if is_project_python_file(directory_path, filename)]
    return project_files


def get_all_imports_of_project(project_path: str) -> List[str]:
    """
    @param root_path: the project path
    @return: the module names that imported in all files of the project
    """
    project_files = get_all_python_files(project_path)
    imports = set()
    for file in project_files:
        file_imports = get_imports_of_file(file)
        imports.update(file_imports)
    return sorted(list(imports))
