import os, subprocess, sys, re, shutil, platform, colorama
from pkg_resources import Requirement, resource_filename
from enum import Enum

from .version import __version__

TEMPLATE_PATH = resource_filename(Requirement.parse("tdbuild"), os.path.join("tdbuild", "tdfile.template"))

help_message = '''
    tdbuild, version {}
    a simple build tool for c/c++ projects
    usage:
        tdbuild new, to initialize a new project
        tdbuild setup, to run project setup
        tdbuild prebuild, to run prebuild
        tdbuild build, to run prebuild + build
        tdbuild run, to run the executable
'''.format(__version__)

colorama.init()

class binary_type(Enum):
    EXECUTABLE = 'EXECUTABLE'
    SHARED_LIB = 'SHARED_LIB'
    STATIC_LIB = 'STATIC_LIB'
