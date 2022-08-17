from setuptools import setup

setup(
    name='ribfind',
    version='2.0.1',    
    description='',
    url='https://gitlab.com/topf-lab/ribfind',
    author='Topf Lab',
    author_email='thomas.mulvaney@cssb-hamburg.de',
    license='BSD 2-clause',
    packages=['ribfind'],
    install_requires=['biopython>=1.5', 'numpy', 'jinja2'],
    entry_points = {
        'console_scripts': ['ribfind=ribfind.cli:main']
    },

    package_data={'ribfind': ['template/*.txt']},
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

