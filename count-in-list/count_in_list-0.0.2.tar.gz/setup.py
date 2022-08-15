import setuptools

with open("README.md", "r") as fh:
	description = fh.read()

setuptools.setup(
	name="count_in_list",
	version="0.0.2",
	author="Khalid Shaikh",
	author_email="k@ruby.run",
	packages=["count_in_list"],
	description="A sample test package",
	long_description=description,
	long_description_content_type="text/markdown",
	url="https://github.com/khalidjshaikh/test-package",
	license='MIT',
	python_requires='>=3.8',
	install_requires=[]
)