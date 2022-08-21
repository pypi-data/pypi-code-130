"""
Setup script for PyCoolPlot

How to upload new release

1. run bum-version.sh

2. setup twine, see:https://blog.amedama.jp/entry/2017/12/31/175036

3. create zip file: python setup.py sdist

4. twine check dist/ {}.tar.gz

5. upload: twine upload --repository pypi dist/{}.tar.gz

pip install --upgrade -i https://test.pypi.org/simple/ pyroombaadapter
"""

from setuptools import setup, find_packages
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# read __version__
with open(PROJECT_PATH + "/pycoolplot/VERSION", 'r') as fd:
    __version__ = fd.readline().rstrip('\n')

setup(
    name="PyCoolPlot",
    version=__version__,
    url="https://github.com/AtsushiSakai/PyCoolPlot",
    author="Atsushi Sakai",
    author_email="asakai.amsl@gmail.com",
    maintainer='Atsushi Sakai',
    maintainer_email='asakai.amsl@gmail.com',
    description=("A cool plotting module in Python"),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>3.6.0',
    license="MIT",
    keywords="python plot matplotlib",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
    ],
)
