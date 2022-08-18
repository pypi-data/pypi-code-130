from re import M
from setuptools import find_packages, setup

setup(
  name='mufid',
  version='2.0',
  author='Yasar Adeel Ansari',
  author_email='yasaradeel@gmail.com',
  description='some useful functions',
  packages=find_packages('src'),
  package_dir={'': 'src'},
  classifiers=[
           "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
  ]
)