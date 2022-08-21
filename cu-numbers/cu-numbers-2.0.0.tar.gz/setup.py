from setuptools import setup, find_packages

setup(
    name="cu-numbers",
    version="2.0.0",
    author="Andrei Shur",
    author_email="amshoor@gmail.com",
    description="Cyrillic numeral system numbers conversion",
    long_description_content_type="text/markdown",
    url="https://github.com/endrain/omninumeric",
    keywords=[
        "church slavonic",
        "conversion",
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Religion",
        "Intended Audience :: Science/Research",
    ],
    packages=find_packages(),
    python_requires=">=3.4",
    install_requires=[
        "omninumeric",
    ],
)
