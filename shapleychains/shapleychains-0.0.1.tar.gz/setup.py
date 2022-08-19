
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='shapleychains',
    version='0.0.1',
    description='',
    url= 'https://github.com/cwayad/shapleychains.git',
    long_description=long_description,
    long_description_content_type= "text/markdown",
    author='Célia Wafa AYAD',
    author_email='celiane.ayad@gmail.com',
    packages=find_packages('src'), 
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'numpy',
        'sklearn',
        'shap',
        'matplotlib',
    ],
    extras_requere = {
        "dev": [
            "pytest>=3.7"
        ]
    }
)