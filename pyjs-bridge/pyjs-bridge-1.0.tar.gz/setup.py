try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyjs-bridge",
    version="1.0",
    author="Chatavut Viriyasuthee",
    author_email="chatavut@lab.ai",
    description="Vulcan's python-javascript api bridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vulcan-coalition/pyjs.git",
    packages=["pyjs", "pyjs.transport"],
    package_data={'pyjs.transport': ['*.js']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'fastapi',
        'aiofiles',
        'python-jose[cryptography]',
        'python-multipart',
        'jsmin',
        'uvicorn',
        'websockets'
    ]
)
