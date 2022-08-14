import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stutterbuddy",
    version="0.1.0",
    author="Jonas Briguet",
    author_email="briguetjo@yahoo.de",
    description="Automate video editing with Stutterbuddy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://stutterbuddy.ch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests',
        'requests-toolbelt',
        'urllib3',
    ],
    keywords='stutterbuddy video editing automation auto-editor ai machine-learning',
    project_urls={
        'Homepage': 'https://stutterbuddy.ch',
    }
)
