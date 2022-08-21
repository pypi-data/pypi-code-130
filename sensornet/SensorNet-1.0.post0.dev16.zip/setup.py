"""Setup configuration. Nothing here, refer to setup.cfg file."""
import setuptools

import versioneer

try:
    import pypandoc
    pypandoc.download_pandoc()
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError, ModuleNotFoundError):
    long_description = open('README.md').read()

setuptools.setup(
    version=versioneer.get_versions(),
    cmdclass=versioneer.get_cmdclass(),
    long_description=long_description,
)
