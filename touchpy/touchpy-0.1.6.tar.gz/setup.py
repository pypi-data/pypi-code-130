import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = '0.1.6'
setuptools.setup(
    name="touchpy",
    version=__version__,
    author="Talha Asghar",
    author_email="talhaasghar.contact@simplelogin.fr",
    description="A simple script which creates .py files with necessary docstrings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamtalhaasghar/touchpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[i for i in open('requirements.txt').readlines() if len(i)!=0],
    entry_points={'console_scripts': ['touchpy = touchpy:touchpy.main']},
)

