from setuptools import setup, find_packages
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_version():
    path_to_init=os.path.join(ROOT_DIR, os.getenv("SIIBRA_TOOLBOX_SRC", "siibra_toolbox_neuroimaging"), '__init__.py')
    with open(path_to_init, 'r', encoding="utf-8") as f:
        content=f.read()
        version_match=re.search(r"^__version__\W*?=\W*?['\"](.*?)['\"]$", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError('version cannot be found!')

with open(os.path.join(ROOT_DIR,"README.rst"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=os.getenv("SIIBRA_TOOLBOX_NAME", "siibra_toolbox_neuroimaging"),
    version=find_version(),
    author="Big Data Analytics Group, Institute of Neuroscience and Medicint (INM-1), Forschungszentrum Julich",
    author_email="inm1-bda@fz-juelich.de",
    description="siibra-toolbox-neuroimaging - siibra toolbox for assignment of neuroimaging signals to brain regions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FZJ-INM1-BDA/siibra-toolbox-neuroimaging",
    packages=find_packages(include=[ os.getenv("SIIBRA_TOOLBOX_SRC", "siibra_toolbox_neuroimaging")]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    entry_points='''
        [siibra_cli.assignment_plugins]
        nifti=siibra_toolbox_neuroimaging.cli:nifti
    ''',
    python_requires='>=3.6',
    install_requires=[
        'siibra>=0.3a17', 
        'siibra-cli>=0.2a0', 
        'matplotlib>=3.3',
        'fpdf'
        ]
)

