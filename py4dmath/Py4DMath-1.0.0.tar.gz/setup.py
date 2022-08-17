from os.path import abspath, dirname, join
from pathlib import Path
from setuptools import find_packages, setup

BASE_DIR = dirname(abspath(__file__))
VERSION_FILE = join(BASE_DIR, 'Py4DMath', 'version.py')

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def get_version():
    with open(VERSION_FILE) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                version = line.split()[-1].strip('"')
                return version
        raise AttributeError("Package does not have a __version__")

setup(
    name='Py4DMath',
    packages=find_packages(include=['Py4DMath']),
    version=get_version(),
    description='A math engine for controlling 3D objects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nicholas Chumney',
    license='MIT',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
