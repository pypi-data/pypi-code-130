from setuptools import setup, find_packages

VERSION = '1.0.0' 
DESCRIPTION = 'Ontology-based tool for cancer data analysis'
LONG_DESCRIPTION = 'A packaged set of functions for ontology-based reasoning of cancer patients'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="kk_ontology_module", 
        version=VERSION,
        author="Kaixuan Khoo",
        author_email="<kaixuan.khoo.98@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        package_data={'kk_ontology_module': ['extras/*']},
        install_requires=["cython", "wheel", "owlready2", "pandas"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'ontology', 'cancer'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)