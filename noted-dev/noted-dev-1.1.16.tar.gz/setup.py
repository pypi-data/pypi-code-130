"""
NOTED PyPI repository: https://pypi.org/project/noted-dev
Create virtual environment:
    python3 -m venv venv-noted
Activate virtual environment:
    . venv-noted/bin/activate
Install packages:
    pip install --upgrade pip
    python3 -m pip install -e . ---------no work
    python3 -m pip install build
Build package:
    python3 -m build --sdist --wheel
    python3 setup.py install
    twine check dist/*
    twine upload dist/*
    pip install noted-dev
Run program:
    noted src/noted/config/config-example.yaml
See:
https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="noted-dev", # pip install noted-dev
    version="1.1.16",
    description="NOTED: a framework to optimise network traffic via the analysis of data from File Transfer Services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/mmisamor/noted",
    author="Carmen Misa Moreira, Edoardo Martelli (CERN IT-CS-NE)",
    author_email="carmen.misa.moreira@cern.ch",
    license='GPLv3 (GNU General Public License)',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="networking, monitoring, transfers, throughput, dynamic circuit, load balance, fts, sense-o",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=['noted', 'noted.*']),
    python_requires=">=3.*",
    setup_requires=['wheel'],
    install_requires=[
        'cycler',
        'kiwisolver',
        'matplotlib',
        'numpy',
        'pandas',
        'Pillow',
        'pyparsing',
        'python-dateutil',
        'pytz',
        'PyYAML',
        'scipy',
        'seaborn',
        'six',
    ], # pip freeze > requirements.txt
    entry_points={
        "console_scripts": [
            "noted=noted.main:main",
        ],
    },
    include_package_data=True,
    project_urls={
        "Source": "https://gitlab.cern.ch/mmisamor/noted",
        "FTS": "https://es-monit-st.cern.ch/kibana/app/kibana#/home?_g=()",
    },
)
