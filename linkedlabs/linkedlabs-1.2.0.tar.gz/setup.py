from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="linkedlabs",
    version="1.2.0",
    description="Get Similar customers (or rows) in data using DNA Matching Algorithms and Artificial Intelligence on your data!",
    py_modules=["linkedlabs","variables","welcome_page","import_funcs"],
    package_dir={"": "src"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
    url="http://www.linkedlabs.co",
    author="Nashit Babber",
    author_email="nashit@linkedlabs.co",

    install_requires = [
        "pandas",
        "numpy",
        "tqdm",
        "scikit-learn",
        "lightgbm",
        "statistics",
        "joblib"
    ],

    extras_require = {
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine",
        ],
    },
)