import setuptools

with open("README.md", "r") as readme_file:
	long_description = readme_file.read()

requirements = ["requests>=2.21.0"]

setuptools.setup(
	name="l33tapi",
	version="1.0.3",
	author="requestsn",
	description="A l33t Api Wrapper",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/lol-1-afk/l33t-API-Wrapper",
	packages=setuptools.find_packages(),
	install_requires=requirements,
	classifiers=[
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)