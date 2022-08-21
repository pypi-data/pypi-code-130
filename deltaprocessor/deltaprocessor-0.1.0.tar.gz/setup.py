from deltaprocessor import __version__

import os
import sys

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


dependencies = ['bleach', 'nvnc', 'setuptools']


def publish():
	os.system("python3 setup.py sdist upload")



if sys.argv[-1] == "publish":
	publish()
	sys.exit()


setup(
	name='deltaprocessor',
	version='.'.join(str(i) for i in __version__),
	description='Delta Processor',
	long_description="Delta Processor",
	author='Le Song Vi',
	author_email='lesongvi@gmail.com',
	license="GPLv3+",
	install_requires=dependencies,
	packages=['deltaprocessor'],
    py_modules=['deltaprocessor'],
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Programming Language :: Python',
	]
)


