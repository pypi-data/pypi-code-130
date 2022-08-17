"""This module setup the base infomation of dissect_site."""


from setuptools import setup, find_packages


VERSION = '0.0.3.2'
DESCRIPTION = 'Get the title and heading of the site'
LONG_DESCRIPTION = """Get the title and heading of the site\
    if no title/heading return None
"""


setup(
    name="dissect_site",
    version=VERSION,
    author="Cuong Doan",
    author_email="<cuong.doan@asnet.com.vn>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'argparse',
        'validators',
        'requests',
        'beautifulsoup4'
    ],
    entry_points='''
        [console_scripts]
        dissect_site=dissect_site.__main__:main
    ''',
    keywords=['python', 'dissect_site'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)
