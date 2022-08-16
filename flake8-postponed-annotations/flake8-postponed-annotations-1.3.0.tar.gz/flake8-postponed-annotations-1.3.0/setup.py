"""Define PyPI package."""

import setuptools


with open('README.md', 'r') as readme_file:
	long_description = readme_file.read()

setuptools.setup(
	name='flake8-postponed-annotations',
	version='1.3.0',
	author='Peter Linss',
	author_email='pypi@linss.com',
	description='Flake8 postponed annotations validation',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/plinss/flake8-postponed-annotations/',

	packages=['flake8_postponed_annotations'],
	package_data={'flake8_postponed_annotations': ['py.typed']},

	install_requires=[
		'flake8-modern-annotations',
	],
	classifiers=[
		'Framework :: Flake8',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Software Development :: Quality Assurance',
	],
	python_requires='>=3.7',
)
