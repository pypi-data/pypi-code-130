import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dipwmsearch",
    version="0.1.2",
    author="Marie Mille (main contributor), Bastien Cazaux, Julie Ripoll and Eric Rivals",
    author_email="dipwm@lirmm.fr",
    license_files = ('LICENSE.txt'),
    description="Provides functions to search for any di-nucleotidic Position Weight Matrix (di-PWM) in a genomic sequence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gite.lirmm.fr/rivals/dipwmsearch",
    project_urls={
        "Bug Tracker": "https://gite.lirmm.fr/rivals/dipwmsearch/-/issues",
        "Documentation": "https://rivals.lirmm.net/dipwmsearch/",
        "Team": "http://www.lirmm.fr/equipes/mab",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CeCILL-B Free Software License Agreement (CECILL-B)",
        "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['dipwmsearch'],
    package_dir={'dipwmsearch': 'src'},
    package_data={'dipwmsearch': ['../data/*', '../examples/*.py']},
    install_requires=[
          'pytest',
          'pyahocorasick'
    ],
    python_requires=">=3.6"
)
