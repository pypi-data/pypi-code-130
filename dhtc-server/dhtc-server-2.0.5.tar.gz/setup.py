from setuptools import setup, find_packages

setup(
    long_description=open("README.md", "r").read(),
    name="dhtc-server",
    version="2.0.5",
    description="distributed hash table crawler ui and api server",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/nbdy/dhtc-server",
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License'
    ],
    keywords="dhtc server",
    packages=find_packages(),
    install_requires=[
        "fastapi~=0.79.0",
        "pytelegrambotapi",
        "beanie~=1.11.6",
        "pydantic~=1.9.1",
        "motor~=3.0.0",
        "uvicorn~=0.18.2",
        "fastapi-users[beanie]",
        "hurry.filesize",
        "python-multipart",
        "pymongo~=4.1.1",
        "starlette~=0.19.1",
    ],
    entry_points={
        'console_scripts': [
            'dhtc_server = dhtc_server.__main__:main'
        ]
    },
    include_package_data=True,
    long_description_content_type="text/markdown",
)
