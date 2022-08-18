import os
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext


pkg_name = 'lib_V2'
version = '0.0.0'
setup_stnd = True

if not setup_stnd:
    lib_extensions = []
    setup(
        name=pkg_name,
        # explicity enumerate subpackage structure
        # ext_modules=cythonize(
        #     lib_extensions,
        #     build_dir="build",
        #     compiler_directives=dict(
        #         always_allow_keywords=True,
        #         language_level=3.6,
        #     ),
        # ),

        version=version,
        author="Algorithms Path",
        author_email="support@algorithmspath.com",
        url= f'http://pypi.python.org/pypi/lib_V1/{version}',
        license="MIT",

        cmdclass=dict(
            build_ext=build_ext,
        ),
        # packages=["lib_compute", "lib_dsa", "lib_typ_parse", "lib_py_parse"],
        install_requires=[
            "bs4",
            "plyvel",
            "selenium",
        ],
        packages=[],
    )
    exit(0)

lib_extensions = [
    Extension( 'lib_typ_parse.*', ['lib_typ_parse/*.py'] ),
    Extension( 'lib_typ_parse.helper.*', ['lib_typ_parse/helper/*.py'] ),
    Extension( 'lib_typ_parse.utils.*', ['lib_typ_parse/utils/*.py'] ),
    Extension( 'lib_py_parse.*', ['lib_py_parse/*.py'] ),
    Extension( 'lib_py_parse.helper.*', ['lib_py_parse/helper/*.py'] ),
    Extension( 'lib_py_parse.utils.*', ['lib_py_parse/utils/*.py'] ),
    Extension( 'lib_dsa.*', ['lib_dsa/*.py'] ),
    Extension( 'lib_compute.*', ['lib_compute/*.py'] ),
    Extension( 'lib_compute.M3.*', ['lib_compute/M3/*.py'] ),
]

setup(
    name=pkg_name,
    # explicity enumerate subpackage structure
    ext_modules=cythonize(
        lib_extensions,
        build_dir="build",
        compiler_directives=dict(
            always_allow_keywords=True,
            language_level=3.6,
        ),
    ),

    version=version,
    author="Algorithms Path",
    author_email="support@algorithmspath.com",
    url= f'http://pypi.python.org/pypi/lib_V1/{version}',
    license="MIT",

    cmdclass=dict(
        build_ext=build_ext,
    ),
    # packages=["lib_compute", "lib_dsa", "lib_typ_parse", "lib_py_parse"],
    install_requires=[
        "bs4",
        "plyvel",
        "selenium",
    ],
    packages=[],
)

# package generation:
# python3 -m cython_setup1 sdist bdist_wheel
# python3 -m cython_setup1 sdist build_ext
# python3 -m cython_setup1 bdist_wheel build_ext
# twine upload dist/*
# PW = EC3 + Succ
