
from setuptools import setup, find_packages

setup(
    name='muse_an_libr',
    version='0.6',
    license='MIT',
    author="Priyanshu Mahey",
    author_email='priyanshu.mahey@yahoo.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/priyanshumahey/Muse-Analysis-Library',
    keywords='Muse project',
    install_requires=[
          'matplotlib',
          'numpy',
          'scipy',
          'pandas',
      ],

)