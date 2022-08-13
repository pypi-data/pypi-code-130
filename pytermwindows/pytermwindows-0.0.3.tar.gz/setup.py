import setuptools

with open( "README.md", "r" ) as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytermwindows", 
    version="0.0.3",
    author="Noah H. Kleinschmidt",
    author_email="noah.kleinschmidt@students.unibe.ch",
    description="A terminal window library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NoahHenrikKleinschmidt/PyTermWindows",
    
    packages=setuptools.find_packages(),

    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)