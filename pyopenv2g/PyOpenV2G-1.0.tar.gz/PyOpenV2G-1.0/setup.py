from setuptools import setup, find_packages

setup(
    name='PyOpenV2G',
    version='1.0',
    license='MIT',
    author="Alexandre Machado",
    author_email='a.machado@ua.pt',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/alexmac98/PyOpenV2G',
    keywords='OpenV2G Electric Mobility V2G',
    install_requires=[
          'ctypes',
          'pathlib',
          'unittest'
      ],

)