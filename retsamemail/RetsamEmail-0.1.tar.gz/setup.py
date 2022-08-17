import setuptools

with open("README.md") as file:
    read_me_description = file.read()

setuptools.setup(
    name="RetsamEmail",
    version="0.1",
    author="Retsam",
    author_email="ruslan69623@gmail.com",
    description="This is a test package.",
    long_description=read_me_description,
    #long_description_content_type="text/markdown",
    #url="package_github_page",
    packages=['RetsamEmail'],
    install_requires=[
          'Django==3.2.13',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False
)