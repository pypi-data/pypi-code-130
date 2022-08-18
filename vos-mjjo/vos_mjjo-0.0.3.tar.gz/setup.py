import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vos_mjjo", # Replace with your own username
    version="0.0.3",
    author="mjjo",
    author_email="mj.jo@valueofspace.com",
    description="vos-mjjo package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jomujin/vos-mjjo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["symspellpy"],
    entry_points={
        'console_scripts': [
            'shortcut1 = package.module:func',
        ],
        'gui_scripts': [
            'shortcut2 = package.module:func',
        ]
    },
    test_suite='tests.test_cordate'
)
