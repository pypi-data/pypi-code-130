import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kymoknot-py",
    version="0.9",
    author="Giovanni Tarter",
    author_email="giovanni.tarter@unitn.it",
    description="Kymoknot python bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.physics.unitn.it/giovanni.tarter/kymoknot_py",
    #project_urls={
    #    "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    #},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={
        "kymoknot": "kymoknot",
        "lib": "lib",
        },

    packages=["kymoknot"],
    python_requires=">=3.6",

    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["kymoknot/build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "numpy>=1.18.5"],

)
