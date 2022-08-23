from setuptools import setup, find_packages

VERSION = '0.2.3' 
DESCRIPTION = 'Speedy implementation of IBL (Instance-based Learning)'
LONG_DESCRIPTION = open("README.MD").read()


# Setting up
setup(
       
        name="speedyibl", 
        version=VERSION,
        author="Nhat Phan",
        author_email="<nhatsp@gmail.com",
        description=DESCRIPTION,
        license="Free for research purposes",
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['setuptools>=42','wheel', 'numpy', 'tabulate'], 
        
        keywords=['Decision Making', 'Instance-based Learning', 'Cognitive Model'],
        classifiers= [
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)