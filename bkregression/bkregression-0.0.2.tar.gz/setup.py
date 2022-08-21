from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'A package for Bayesian kernel regression'
LONG_DESCRIPTION = 'A package for Bayesian kernel regression using a local uncertainty approximation using weighted sample variance.'

# Setting up
setup(
        name="bkregression", 
        version=VERSION,
        author="Marc Schlichting",
        author_email="mschl@stanford.edu",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["torch","ax-platform","tqdm"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
        ]
)