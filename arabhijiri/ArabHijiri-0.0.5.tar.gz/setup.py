from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.5'
DESCRIPTION = 'Getting the Hijiri (Arabic) date in arabic language and numbers'

# Setting up
setup(
    name="ArabHijiri",
    version=VERSION,
    author="Youssef M. Khalil",
    author_email="youssefkhalil320@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'datetime'],
    keywords=['python', 'date', 'time', 'Hijiridate', 'arabic', 'arabicdate','islamic'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)