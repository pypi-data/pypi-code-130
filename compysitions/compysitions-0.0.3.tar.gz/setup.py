from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='compysitions',
    version='0.0.3',
    packages=['compysitions'],
    package_dir={'compysitions': 'src'},
    url='https://github.com/zganger/compysitions',
    license='',
    author='zganger',
    author_email='zganger@icloud.com',
    description='Extensions for working with Python Dataclasses',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
