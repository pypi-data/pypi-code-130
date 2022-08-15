"""
end-to-end testing
"""
import os
from glob import glob

import pytest

from easy_sge.experiences_manager import ExperienceBase


@pytest.fixture()
def resource():
    for f in glob("output/*"):
        os.remove(f)
    yield "resource"
    for f in glob("output/*"):
        os.remove(f)


def test_simple_workflow(resource):
    my_experience = ExperienceBase(script_name="easy_sge/tests/simple_workflow.py")
    my_experience.add_experience_key_values("n", list(range(1, 101)))

    my_experience.add_grid_parameter("-P", "devel")
    my_experience.add_grid_parameter("-cwd", "")
    my_experience.add_grid_parameter("-N", "fizzbuzz")

    my_experience.run(sync=True)
    tot = 0
    for f in glob("output/*o*"):
        with open(f, "r") as my_file:
            assert "n=" in my_file.read()
            tot += 1
    assert tot == 100
