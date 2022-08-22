from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.3'
DESCRIPTION = 'Create simple Flask skeletons'
LONG_DESCRIPTION = 'Package that creates a simple Flask project structure to use in new projects'

# Setting up
setup(
    name="pyflaskcreator",
    version=VERSION,
    author="Jael Gonzalez",
    description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=['Flask'],
    packages=find_packages(),
    entry_points={
    'console_scripts': [
        'pyflaskcreator = pyflaskcreator.flaskbuilder:create',
    ]},
    package_data={
   'pyflaskcreator.assets': ['*'],     # All files from folder A
   },
)