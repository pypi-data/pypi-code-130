import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Retica",
    version="1.1.0",
    author="CyroCoders",
    author_email="pypi@cyrocoders.ml",
    description="Retica Is A Performant, Easy To Use Web Server Based On Python With HTTPS & Plugins Support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CyroCoders/Retica",
    project_urls={
        "Bug Tracker": "https://github.com/CyroCoders/Retica/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    entry_points ={
        'console_scripts': [
            'retica = Retica.cli:main'
        ]
    },
    python_requires=">=3",
    install_requires=[
        'Jinja2==2.11.2',
        'Brotli==1.0.9',
        'parse==1.19.0',
        'pyCLI==2.0.3',
    ]
)