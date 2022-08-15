from setuptools import setup

with open('README.rst', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding='utf-8') as history_file:
    history = history_file.read()

setup(
    name='ProdNet',
    author="Leonardo Niccolò Ialongo, Davide Luzzati",
    author_email='leonardo.ialongo@gmail.com',
    python_requires='>=3.0',
    version='0.0.1',
    url='https://github.com/LeonardoIalongo/ProdNet',
    description=("A collection of models of economic Production Networks and "
                 "their associated measures and functions."),
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    license="GNU General Public License v3",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    packages=['ProdNet'],
    package_dir={'': 'src'},
    install_requires=["numpy>=1.15",
                      "numba>=0.55",
                      "scipy>=1.6.0"
                      ],
    extras_require={
        "dev": ["numba==0.55.2",
                "numpy==1.22.4",
                "pandas==1.4.3",
                "openpyxl==3.0.10",
                "ipykernel==6.15.1",
                "pytest==6.0.1",
                "hypothesis==6.54.1",
                "coverage==5.2.1",
                "pytest-cov==2.10.1",
                "flake8==3.8.3",
                "wheel==0.35.1",
                "matplotlib==3.3.2",
                "check-manifest==0.44",
                "setuptools==47.1.0",
                "twine==3.2.0",
                "tox==3.20.1"],
        },
    )