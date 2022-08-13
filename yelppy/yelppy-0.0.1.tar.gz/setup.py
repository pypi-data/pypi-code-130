from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Yelp results'
LONG_DESCRIPTION = 'Using Yelp API to create a pandas dataframe'

# Setting up
setup(
        name="yelppy", 
        version=VERSION,
        author="Goutam Konapala",
        author_email="<goutam.iitbbs@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas','requests'],
        zip_safe=False # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
)
