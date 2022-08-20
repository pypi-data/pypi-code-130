import setuptools
from weesocket import __version__

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="weesocket",
	version=__version__,
	author="Patrik Katrenak",
	author_email="patrik@katryapps.com",
	description="Tiny socket wrapper",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://gitlab.com/katry/weesocket",
	packages=["weesocket"],
	install_requires=["rsa"],
	extras_require={
		"orjson": ["orjson"],
		"ujson": ["ujson"],
		"dev": ["orjson", "pytest", "wheel", "twine"]
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
		"Operating System :: OS Independent",
	],
	platforms=["any"],
	python_requires=">=3.9",
)
