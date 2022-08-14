from setuptools import setup,find_packages
from typing import List
import os

CWD = os.getcwd()
#Declaring variables for setup functions
PROJECT_NAME="outlier-detector-z"
VERSION="0.0.9"
AUTHOR="Mohamed Naji Aboo"
DESRCIPTION="Application is used to detect the outliers in a list or tuple"

REQUIREMENT_FILE_NAME= os.path.join(CWD, "requirements.txt")
                       
 

HYPHEN_E_DOT = "-e ."


def get_requirements_list() -> List[str]:
    """
    Description: This function is going to return list of requirement
    mention in requirements.txt file
    return This function is going to return a list which contain name
    of libraries mentioned in requirements.txt file
    """
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
name=PROJECT_NAME,
version=VERSION,
author=AUTHOR,
description=DESRCIPTION,
packages=find_packages(), 
install_requires= ["numpy"],
long_description=long_description,
long_description_content_type="text/markdown",
)
