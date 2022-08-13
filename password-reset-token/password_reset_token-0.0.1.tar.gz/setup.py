import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="password_reset_token",
    version="0.0.1",
    author="Valtteri Remes",
    description="Simple and easy to use Python 3 module to generate password reset tokens, based on JWT.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    py_modules=["password_reset_token"],
    install_requires=[]
)
