from setuptools import setup, find_packages

setup(
	name="gstlal_tesla",

	version="1.0.0",

	author="Alvin K.Y. Li, Juno C.L. Chan",
	
	author_email="kli7@caltech.edu, clchan@link.cuhk.edu.hk",

	packages=['gstlal_tesla', 'gstlal_tesla/dags', 'gstlal_tesla/config', 'gstlal_tesla/dags/layers'],

	scripts=['bin/tesla_workflow', 
		'bin/tesla_generate_and_replace_injections', 
		'bin/tesla_generate_reduced_bank',
		],

	url='https://git.ligo.org/chun-lung.chan/tesla/',

	description="GstLAL-based sub-threshold lensed gravitational waves search pipeline",

	long_description="Insert long description here.",

	classifiers=[
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Operating System :: MacOS :: MacOS X",
		"Operating System :: POSIX",
		],

	python_requires='>=3.6',
)
