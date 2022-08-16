from setuptools import setup, find_packages
exec(open("src/myloguru/_resources.py").read())
setup(
    name='myloguru-deskent',
    version=__version__,
    author=__author__,
    author_email='battenetciz@gmail.com',
    description='My loguru config',
    install_requires=[
        'loguru==0.5.3',
    ],
    scripts=['src/myloguru/my_loguru.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/Deskent/my_loguru",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
)
