from setuptools import setup, find_packages


def readme():
    return open('README.md', 'r').read()


setup(
    name="smooth_progress",
    version="0.2.0",
    author="Murdo Maclachlan",
    author_email="murdomaclachlan@duck.com",
    description=(
        "A simple progress bar made primarily for my own personal use. Made from"
        + " a combination of necessity and so much sloth that it overflowed into"
        + " productivity."
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://codeberg.org/MurdoMaclachlan/smooth_progress",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    license='AGPLv3+'
)
