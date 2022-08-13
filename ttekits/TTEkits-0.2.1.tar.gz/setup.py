from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="TTEkits",
    version='0.2.1',
    description="This is a travel time estimation Python Library!",
    py_modules=["TTEkits/model"],
    package_dir={'': 'TTEkits'},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["gurobipy>=9.5.0","networkx>=2.6.3","matplotlib>=3.3.4","shapely>=1.8.0","geopandas>=0.10.2","osmnx>=1.1.2","pandas>=1.4.2"],
    extras_require = {"dev":[],},
    url="https://github.com/Elon-Lau/TTEkits",
    author="Elon Lau",
    author_email="weitinglau1999@gmail.com",
    setup_requires=['wheel']
)