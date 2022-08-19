from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Recommendations of sports content'
LONG_DESCRIPTION = 'Recommendations of sports related tweets and subreddits based on Team preferences'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Sports_Recommender", 
        version=VERSION,
        author="Mathew Mammen Jacob",
        author_email="<mathew.mammenjacob@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=['Sports_Recommender'],
        install_requires=['spacy',' rt_sports_scrapers','smack_gsheets'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'package','Recommender'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)