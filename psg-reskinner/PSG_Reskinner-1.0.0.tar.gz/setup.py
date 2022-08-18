from setuptools import setup, find_packages
from sys import path
path.append('src/')
from psg_reskinner import __version__ as VERSION

def readme():
    with open('README.md', 'r') as readme_file:
        README = readme_file.read()
    return README

REQUIRED_PACKAGES = ['PySimpleGUI']

setup(
    name="PSG_Reskinner",
    version=str(VERSION),
    author="Divine U. Afam-Ifediogor",
    author_email="divineafam@gmail.com",
    license="MIT License",
    description="Instantaneous theme changing for PySimpleGUI windows.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/definite-d/psg_reskinner/",
    packages = ['PSG_Reskinner'],
    project_urls={
        "Bug Tracker": "https://github.com/definite-d/psg_reskinner/issues/",
    },
    install_requires=REQUIRED_PACKAGES,
    python_requires=">=3.6",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ]
)