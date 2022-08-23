##from distutils.core import setup
##setup(
##  name = 'c:\\MPT5.1.0.0',         # How you named your package folder (MyLib)
##  packages = ['c:\\MPT5.1.0.0'],   # Chose the same as "name"
##  version = '0.1',      # Start with a small number and increase it with every change you make
##  license='GNU',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
##  description = 'MPT5 Test ML Environment',   # Give a short description about your library
##  author = 'Pooya Ghiami',                   # Type in your name
##  author_email = 'pooyagheyami@gmail.com',      # Type in your E-Mail
##  url = 'https://github.com/Srcfount/MPT5',   # Provide either the link to your github or to your website
##  download_url = 'https://github.com/Srcfount/MPT5/MPT5.0.1.tar.gz',    # I explain this later on
##  keywords = ['MACHINELEARNING', 'GUI', 'SQL'],   # Keywords that define your package best
##  install_requires=[            # I get to this in a second
##          'wxPython',
##          'sqlite3',
##      ],
##  classifiers=[
##    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
##    'Intended Audience :: Developers',      # Define that your audience are developers
##    'Topic :: Software Development :: Build Tools',
##    'License :: OSI Approved :: GNU License',   # Again, pick a license
##    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support
##    'Programming Language :: Python :: 3.8',
##    'Programming Language :: Python :: 3.9',
##    'Programming Language :: Python :: 3.10',
##  ],
##)

##
from setuptools import setup, find_packages


setup(
    name='MPT5.0.1',
    version='0.1',
    license='GNU',
    author="Pooya Ghiami",
    author_email='pooyagheyami@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Srcfount/MPT5/',
    keywords='MACHINELEARNING GUI SQL',
    install_requires=[
          'wxPython',
      ],

)
##
##import setuptools
##
##long_desc = open("README.md").read()
##required = ['wxpython'] # Comma seperated dependent libraries name
##
##setuptools.setup(
##    name="MPT5.1.0",
##    version="1.0.0", # eg:1.0.0
##    author="Pooya Ghiami",
##    author_email="pooyagheyami@gmail.com",
##    license="GNU",
##    description="MPT5 Test ML Environment",
##    long_description=long_desc,
##    #long_description_content_type="text/markdown",
##    url="https://github.com/Srcfount/MPT5/",
##    #packages = ['c:\\MPT5.1.0.0'],#setuptools.find_packages('src'), #['MPT5.1.0'],
##    # project_urls is optional
##    #project_urls={
##    #    "Bug Tracker": "<BUG_TRACKER_URL>",
##    #},
##    keywords="MACHINELEARNING GUI SQL",
##    install_requires=required,
##    packages=setuptools.find_packages(where="src"),
##    python_requires=">=3.6",
##)
