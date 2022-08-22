from setuptools import find_packages, setup

setup(
	name = 'cpsample',
	packages = find_packages(),
	package_dir = {'': 'src'},
	version = '1.1.1',
	description = "sample library",
	long_description = "Nothing much",
	long_description_content_type = 'text/markdown',
	install_requires = ['pandas'],
	author = 'Cullen')