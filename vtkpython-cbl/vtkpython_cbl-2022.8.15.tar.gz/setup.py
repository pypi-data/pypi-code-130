import datetime
import os
import setuptools

name = "vtkpython_cbl"

# version = os.environ['CI_COMMIT_TAG']
version = datetime.date.today().strftime("%Y.%m.%d")

setuptools.setup(
    name=name,
    version=version,
    author="Martin Genet",
    author_email="martin.genet@polytechnique.edu",
    description=open("README.md", "r").readlines()[1][:-1],
    long_description = open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.inria.fr/mgenet/"+name,
    packages=[name],
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    scripts=[name+"/"+filename for filename in os.listdir(name) if os.path.isfile(name+"/"+filename) and os.access(name+"/"+filename, os.X_OK)],
    install_requires=["numpy", "vtk", "myPythonLibrary", "myVTKPythonLibrary"],
)

# keyring set https://upload.pypi.org/legacy martin.genet
# keyring set https://upload.pypi.org martin.genet

# python setup.py sdist bdist_wheel

# twine upload dist/*
