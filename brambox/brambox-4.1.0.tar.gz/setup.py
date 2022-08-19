import os
import glob
import setuptools as setup
import versioneer
from setuptools.extension import Extension
from pkg_resources import get_distribution, DistributionNotFound

# Cython
try:
    from Cython.Build import cythonize
    import numpy
except ImportError:
    CYTHON = False
    CDEBUG = False
    include_dirs = []
else:
    CYTHON = os.getenv('CYTHON', '0').strip() != '0'    # Generate .c from .pyx with cython
    CDEBUG = os.getenv('CDEBUG', '0').strip() != '0'    # Enable profiling and linetrace in cython files for debugging
    include_dirs = [numpy.get_include()]


def get_dist(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None


def find_packages():
    return ['brambox'] + ['brambox.'+p for p in setup.find_packages('brambox')]


def find_extensions():
    ext = '.pyx' if CYTHON else '.cpp'
    files = list(glob.glob('brambox/**/*'+ext, recursive=True))
    if os.name == 'nt':
        names = [os.path.splitext(f)[0].replace('\\', '.') for f in files]
        base_compile_args = ['/std:c++14', '/wd4018']
        debug_compile_args = ['/Od']
        build_compile_args = ['/O2']

    else:
        names = [os.path.splitext(f)[0].replace('/', '.') for f in files]
        base_compile_args = ['-std=c++14', '-Wno-sign-compare']
        debug_compile_args = ['-O0']
        build_compile_args = ['-O3']

    if CYTHON and CDEBUG:
        extensions = [
            Extension(
                n,
                [f],
                extra_compile_args=[*base_compile_args, *debug_compile_args],
                define_macros=[('CYTHON_TRACE', '1'), ('CYTHON_TRACE_NOGIL', '1')]
            )
            for n, f in zip(names, files)
        ]
    else:
        extensions = [
            Extension(
                n,
                [f],
                extra_compile_args=[*base_compile_args, *build_compile_args],
            )
            for n, f in zip(names, files)
        ]

    if CYTHON:
        if CDEBUG:
            extensions = cythonize(
                extensions,
                gdb_debug=True,
                compiler_directives={'linetrace': True, 'binding': True},
            )
        else:
            extensions = cythonize(
                extensions,
            )

    return extensions


requirements = [
    'numpy',
    'pandas>=1.1',
    'scipy',
    'tqdm>=4.27',
]


setup.setup(
    # Basic Information
    name='brambox',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='EAVISE',
    description='Basic Requisites for Algorithms on iMages toolBOX',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://gitlab.com/eavise/brambox',

    # Package data
    install_requires=requirements,
    extras_require={
        'segment': ['pgpd>=2.1'],
    },
    packages=find_packages(),
    scripts=setup.findall('scripts'),
    test_suite='test',
    include_dirs=include_dirs,
    ext_modules=find_extensions(),
    include_package_data=True,

    # Additional options
    zip_safe=False,
)
