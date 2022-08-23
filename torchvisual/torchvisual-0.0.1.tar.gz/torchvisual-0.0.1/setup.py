import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="torchvisual",
  version="0.0.1",
  author="kamilu",
  author_email="luzhixing12345@163.com",
  description="my implementation of pytorch",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/luzhixing12345/Torchvisual",
  package_dir={'': 'src'},
  packages=setuptools.find_packages(where='src'),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)