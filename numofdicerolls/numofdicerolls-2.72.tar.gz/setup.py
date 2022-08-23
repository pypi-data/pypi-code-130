from setuptools import setup, find_packages

VERSION = '2.72'
DESCRIPTION = 'Python script from pipline'
LONG_DESCRIPTION = 'This pipeline was automated by Jenkins'

# Setting up
setup(
    name="numofdicerolls",
    version=VERSION,
    author="Dean",
    author_email="<dneugebauer@live.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
