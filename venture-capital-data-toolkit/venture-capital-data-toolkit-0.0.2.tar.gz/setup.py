from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Methods to manipulate and analyze data from platforms frequently used in venture capital.'
LONG_DESCRIPTION = '''
    Methods to manipulate and analyze data from platforms frequently used in venture capital.
    This package currently supports functions for the following platforms:
    - Affinity
    - Airtable
    - Aumni
    - Carta
'''

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="venture-capital-data-toolkit", 
        version=VERSION,
        author="Andrew Yu",
        author_email="<hello@yudrew.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['venture capital', 'affinity', 'airtable', 'aumni', 'carta', 'data analysis'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)