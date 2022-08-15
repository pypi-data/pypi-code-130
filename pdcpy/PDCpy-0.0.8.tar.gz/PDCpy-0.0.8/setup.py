from setuptools import Extension, setup, find_packages
import os
import sys
import os.path
from Cython.Build import cythonize

def get_env_or_exit(name):
    try:
        value = os.environ[name]
    except KeyError:
        sys.exit('Environment variable %s not set. Aborting' % name)
    return value

PDC_DIR = os.path.join(*os.path.split(get_env_or_exit("PDC_DIR"))[:-1])
MERCURY_DIR = get_env_or_exit("MERCURY_DIR")

#TODO: use MPICC environment variable to let user choose compiler
mpi_build_args = os.popen('mpicc -compile_info').read().strip().split()[1:]
mpi_link_args = os.popen('mpicc -link_info').read().strip().split()[1:]

extension = Extension(
    "*",
    ["pdc/*.pyx"],
    libraries=["pdc"],
    library_dirs=[os.path.join(PDC_DIR, "install", "lib")],
    include_dirs=[
        os.path.join(PDC_DIR, "install", "include"),
        os.path.join(MERCURY_DIR, "include"),
        os.path.join(PDC_DIR, "utils", "include"), #for pdc_id_pkg.h
        os.path.join(PDC_DIR, "api", "pdc_obj", "include") #for pdc_(obj/cont/prop)_pkg.h
    ],
    extra_compile_args=mpi_build_args,
    extra_link_args=mpi_link_args
)

#extension.cython_directives = {'language_level': "3"}

setup(
    name='PDCpy',
    version='0.0.8',
    include_package_data=True,
    ext_modules=cythonize(extension, language_level=3),
    zip_safe=False,
)
