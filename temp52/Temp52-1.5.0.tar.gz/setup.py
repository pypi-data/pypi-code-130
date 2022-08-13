from setuptools import setup, find_packages


setup(
    name='Temp52',
    version='1.5.0',
    license='MIT',
    author="Pooya Ghiami",
    author_email='pooyagheyami@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/pooyagheyami/Temp52',
    keywords='Temp52',
    install_requires=[
          'wxpython','covertdate'
      ],

)
