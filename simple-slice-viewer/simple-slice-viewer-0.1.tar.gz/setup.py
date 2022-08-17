#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:56:47 2017

@author: M. Segbers
"""

from setuptools import setup, find_packages

README = 'README.md'
VERSION = 0.1
DESCRIPTION = 'Simple slice viewer for Simple ITK images'
NAME = 'simple-slice-viewer'


from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Intended Audience :: Science/Research',
        'Natural Language :: English'
      ],
      keywords='ImageViewer DICOM, SimpleITK',
      author='M. Segbers',
      author_email='m.segbers@gmail.com',
      python_requires='>=3.6, <3.10',
      license='MIT',
      include_package_data=True,
      package_data = {'': ['*.yml']},
      install_requires=['SimpleITK', 'numpy', 'matplotlib', 'pyqtgraph', 'pyqt5',
                        'pyyaml'],
      zip_safe=False,
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'simple-slice-viewer = simple_slice_viewer.console:run_from_cmd',
            'ssv = simple_slice_viewer.console:run_from_cmd']})
