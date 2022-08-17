from setuptools import setup, find_packages

setup(
    name='leo_landau-SDK',
    version='0.1.2',
    license='MIT',
    author="Leo Landau",
    author_email='leo_landau@yahoo.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/llandau/leo_landau-SDK',
    keywords='LibLab project',
    install_requires=[
      ],
)
