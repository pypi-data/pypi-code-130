try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="alphaui",
    version="3.1.4.1",
    include_package_data=True,
    description="Python library for easily interacting with trained machine learning models",
    packages=["alphaui"],
    license="Apache License 2.0",
    keywords=["machine learning", "visualization", "reproducibility"],
    install_requires=[
        "analytics-python",
        "aiohttp",
        "fastapi",
        "ffmpy",
        "markdown-it-py[linkify,plugins]",
        "matplotlib",
        "numpy",
        "orjson",
        "pandas",
        "paramiko",
        "pillow",
        "pycryptodome",
        "python-multipart",
        "pydub",
        "requests",
        "uvicorn",
        "jinja2",
        "httpx",
        "ffspec"

    ],
)
