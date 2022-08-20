from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'My first Python package'
LONG_DESCRIPTION = 'My first Python package with a slightly longer description'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="simpleaddfunc1",
    version=VERSION,
    author="NS",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    py_modules=['add','sub'],
    python_requires='>=3.6'
)