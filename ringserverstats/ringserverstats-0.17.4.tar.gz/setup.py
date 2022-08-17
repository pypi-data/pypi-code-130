from io import open
from setuptools import setup, find_packages

package_vers = 4
with open('ringserverstats/ringserverstats.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"') + '.' + str(package_vers)
            break
    else:
        version = '0.0.1'


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='ringserverstats',
    version=version,
    description='Export logs from ringserver as postgresql timeseries',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Jonathan Schaeffer',
    author_email='jonathan.schaeffer@univ-grenoble-alpes.fr',
    maintainer='Jonathan Schaeffer',
    maintainer_email='jonathan.schaeffer@univ-grenoble-alpes.fr',
    url='https://github.com/resif/ringserver-stats',
    license='GPL-3.0',
    packages=find_packages(),
    install_requires=[
        'Click>=7.0.0',
        'maxminddb>=1.5.2',
        'maxminddb-geolite2>=2018.703',
        'regex>=2020.2.20',
        'psycopg2>=2.8.5',
        'fdsnnetextender>=3.2.0',
        'geohash2>=1.1',
    ],
    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ],

    tests_require=['coverage', 'pytest'],
    entry_points='''
    [console_scripts]
    ringserverstats=ringserverstats.cli:cli
    '''
)
