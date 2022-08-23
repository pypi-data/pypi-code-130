#import pathlib
from setuptools import setup
from setuptools import find_packages

#The directory containing this file
#HERE = pathlib.Path(__file__).parent
#The text of the README file
#README = (HERE / "README.md").read_text()
README = ''.join([line for line in open("README.md").readlines()])
#This call to setup() does all the work
setup(
    name="muuusiiik",
    version="0.0.6",
    author="@muuusiiik",
    author_email="muuusiiikd@gmail.com",
    description="simple utilities",
    long_description=README,
    long_description_content_type="text/markdown",
    #url="https://github.com/c-tawayip/longbug_util",
    url="https://github.com/muuusiiik/utility",
    python_requires=">=3.7",
    license="MIT",
     classifiers=[
         "License :: OSI Approved :: MIT License",
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.7",
     ],
     #packages=["muuusiiik"],
     packages=find_packages(","),

     # DEAL WITH DATA
     #package_data={"vocab": ["vocab/*"]}
     #include_package_data=True,

     # DEPENDENCIES PACKAGES
     install_requires=["dill", "PyYaml"],
     #setup_requires=["logging", "time", "pathlib", "dill", "yaml"],
     #install_requires=[],
 )

