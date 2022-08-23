import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysica",
    version="0.0.1",
    author="Pietro Mandracci",
    author_email="pietro.mandracci.software@gmail.com",
    description="PYthon tools for SImulation and CAlculus",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/pietromandracci/pysica",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3',
)
