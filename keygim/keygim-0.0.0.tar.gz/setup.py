import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()
setuptools.setup(
	name="keygim",
	version="0.0.0",
	author="Keyywind",
	author_email="kevinwater127@gmail.com",
	description="A simple library with image utilities.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/keyywind/keygim",
	project_urls={
		"Bug Tracker": "https://github.com/keyywind/keygim/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	package_dir={"": "src"},
	packages=setuptools.find_packages(where="src"),
	python_requires=">=3.7",
	
	install_requires=[
		'markdown'
	]
	
)