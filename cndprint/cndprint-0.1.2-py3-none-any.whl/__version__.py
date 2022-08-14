import pkg_resources


path = pkg_resources.resource_filename('cndprint', 'VERSION')
__version__ = open(path).read()
