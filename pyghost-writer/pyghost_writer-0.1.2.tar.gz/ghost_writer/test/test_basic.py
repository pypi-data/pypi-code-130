from pathlib import Path

import pytest

from ghost_writer.scriptify import scriptify_python
from ghost_writer.utils.package_data import get_path_of_data_file


def test_generator():

    scriptify_python(get_path_of_data_file("script.py"))

    with Path(get_path_of_data_file("generated_test_script.py")).open() as f:

        correct_lines = f.readlines()

    assert Path("generated_script.py").exists()

    with Path("generated_script.py").open() as f:

        new_lines = f.readlines()

    for x, y in zip(correct_lines, new_lines):

        assert x == y

    Path("generated_script.py").unlink()
