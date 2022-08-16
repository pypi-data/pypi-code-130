import os
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

base_dir = os.getcwd()

lib_extensions = []
q = [
    'lib_compute',
    'lib_dsa',
    'lib_py_parse',
    'lib_typ_parse',
]

while len(q) > 0:
    fspath = q.pop()
    target_dir = f'{base_dir}/{fspath}'
    submodule = False
    for f in os.listdir(target_dir):
        if f == '__init__.py':
            submodule = True
            continue
        path_v = f'{target_dir}/{f}'
        if os.path.isdir(path_v):
            q.append( f'{fspath}/{f}' )
            continue
    if not submodule:
        continue

    K1 = fspath.replace('/', '.')
    mod_base = f'{K1}.*'
    mod_L1 = [ f'{fspath}/*.py' ]
    lib_extensions.append( Extension( mod_base, mod_L1 ) )

setup(
    name="lib_V1",
    # explicity enumerate subpackage structure
    ext_modules=cythonize(
        lib_extensions,
        build_dir="build",
        compiler_directives=dict(
            always_allow_keywords=True,
            language_level=3.6,
        ),
    ),

    version='0.0.1',
    author="Algorithms Path",
    author_email="support@algorithmspath.com",
    url='http://pypi.python.org/pypi/lib_V1/',
    license="MIT",

    cmdclass=dict(
        build_ext=build_ext,
    ),
    # packages=["lib_compute", "lib_dsa", "lib_typ_parse", "lib_py_parse"],
    install_requires=[
        "bs4",
        "plyvel",
        "duckduckgo-search",
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
