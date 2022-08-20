import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='l3ns-dev',
    version='0.0.2',
    license='MIT',
    description='Simple Docker based Network Simulator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daniil Malevanniy and others',
    author_email='oleg.Jakushkin@gmail.com',
    url='https://github.com/OlegJakushkin/l3ns',
    packages=setuptools.find_packages(),
    install_requires=[
          'docker',
          'hashids',
          'pydoc-markdown'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
    ],
)
