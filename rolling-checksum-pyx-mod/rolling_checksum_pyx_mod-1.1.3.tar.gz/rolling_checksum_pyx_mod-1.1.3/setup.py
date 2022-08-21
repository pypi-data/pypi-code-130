
"""
Package up the Cython version of rolling_checksum_mod.

This code wants the pure python also installed.
"""

import os
import sys
import subprocess

from setuptools import setup, Extension
from Cython.Build import cythonize
# from distutils.extension import Extension

version = '1.1.3'


def is_newer(filename1, filename2):
    """Return True if filename1 is newer than filename2."""
    time1 = os.stat(filename1).st_mtime
    time2 = os.stat(filename2).st_mtime

    if time1 > time2:
        return True
    else:
        return False


def m4_it(infilename, outfilename, define):
    """
    Create outfilename from infilename in a make-like manner.

    If outfilename doesn't exit, create it using m4.
    If outfilename exists but is older than infilename, recreate it using m4.
    """
    build_it = False

    if os.path.exists(outfilename):
        if is_newer(infilename, outfilename):
            # outfilename exists, but is older than infilename, build it
            build_it = True
    else:
        # outfilename does not exist, build it
        build_it = True

    if build_it:
        try:
            subprocess.check_call('m4 -D"%s"=1 < "%s" > "%s"' % (define, infilename, outfilename), shell=True)
        except subprocess.CalledProcessError:
            sys.stderr.write('You need m4 on your path to build this code\n')
            sys.exit(1)


if os.path.exists('../rolling_checksum_mod.m4'):
    m4_it('../rolling_checksum_mod.m4', 'rolling_checksum_pyx_mod.pyx', 'pyx')

extensions = [
    Extension("rolling_checksum_pyx_mod", ["rolling_checksum_pyx_mod.pyx"]),
    ]

setup(
    name='rolling_checksum_pyx_mod',
    ext_modules=cythonize(extensions),
    version=version,
    description='Cython-augmented Python module providing a variable-length, content-based blocking algorithm',
    long_description="""
Chop a file into variable-length, content-based chunks.

Example use:
.. code-block:: python

    >>> import rolling_checksum_mod
    >>> # If you have both rolling_checksum_pyx_mod and rolling_checksum_py_mod installed, the software will
    >>> # automatically prefer the pyx version.  Both py and pyx versions require rolling_checksum_py_mod, but
    >>> # only the pyx version requires rolling_checksum_pyx_mod.
    >>> with open('/tmp/big-file.bin', 'rb') as file_:
    >>>     for chunk in rolling_checksum_mod.min_max_chunker(file_):
    >>>         # chunk is now a piece of the data from file_, and it will not always have the same length.
    >>>         # Instead, it has the property that if you insert a byte at the beginning of /tmp/big-file.bin,
    >>>         # most of the chunks of the file will remain the same.  This can be nice for a deduplicating
    >>>         # backup program.
    >>>         print(len(chunk))
""",
    author='Daniel Richard Stromberg',
    author_email='strombrg@gmail.com',
    url='http://stromberg.dnsalias.org/~dstromberg/rolling-checksum-mod/',
    platforms='Cross platform',
    license='GPLv3',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        ],
    install_requires=[
        "rolling_checksum_py_mod",
        "cython",
        ],
    )
