from setuptools import setup, find_packages


setup(
    name='sphinx_test_cases',
    version='0.4',
    license='Apache',
    author="Arturim",
    author_email='lozinski.artur@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ArtUrim/sphinx-test',
    keywords='sphinx test case scenario plan',
    install_requires=[
          'sphinx',
          'wheel',
      ],

)
