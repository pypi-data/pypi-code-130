import sys

# from Cython.Distutils import build_ext
from setuptools import setup, find_packages
from setuptools.extension import Extension
# from Cython.Build import cythonize

if 'build_ext' in sys.argv:
    from Cython.Distutils import build_ext
    use_cython = True
else:
    use_cython = False

ext_pyx = '.pyx' if use_cython else '.c'
ext_py = '.py' if use_cython else '.c'

extensions_names = {
    'traceutils2.utils.utils': ['traceutils2/utils/utils' + ext_pyx],
    'traceutils2.utils.net': ['traceutils2/utils/net' + ext_pyx],
    'traceutils2.utils.dicts': ['traceutils2/utils/dicts' + ext_pyx],
    # 'traceutils2.file2.file2': ['traceutils2/file2/file2' + ext_pyx],
    'traceutils2.as2org.as2org': ['traceutils2/as2org/as2org' + ext_pyx],
    'traceutils2.bgp.bgp': ['traceutils2/bgp/bgp' + ext_pyx],
    # 'traceutils2.bgpreader.reader': ['traceutils2/bgpreader/reader' + ext_pyx],
    'traceutils2.radix.radix_prefix': ['traceutils2/radix/radix_prefix' + ext_pyx],
    'traceutils2.radix.radix_node': ['traceutils2/radix/radix_node' + ext_pyx],
    'traceutils2.radix.radix_tree': ['traceutils2/radix/radix_tree' + ext_pyx],
    'traceutils2.radix.radix': ['traceutils2/radix/radix' + ext_pyx],
    'traceutils2.radix.ip2as': ['traceutils2/radix/ip2as' + ext_pyx],
    'traceutils2.radix.ip2ases': ['traceutils2/radix/ip2ases' + ext_pyx],
    'traceutils2.radix.ip2data': ['traceutils2/radix/ip2data' + ext_pyx],
    'traceutils2.scamper.hop': ['traceutils2/scamper/hop' + ext_pyx],
    'traceutils2.scamper.atlas': ['traceutils2/scamper/atlas' + ext_pyx],
    'traceutils2.scamper.warts': ['traceutils2/scamper/warts' + ext_pyx],
    'traceutils2.scamper.utils': ['traceutils2/scamper/utils' + ext_pyx],
    'traceutils2.scamper.pyatlas': ['traceutils2/scamper/py_atlas' + ext_py],
    # 'traceutils2.progress.bar': ['traceutils2/progress/bar' + ext_py],
    # 'traceutils.traceparse': ['traceparse.py']
}

extensions = [Extension(k, v) for k, v in extensions_names.items()]
package_data = {k: ['*.pxd', '*pyx', '*.py'] for k in extensions_names}

if use_cython:
    from Cython.Build import cythonize
    extensions = cythonize(
        extensions,
        compiler_directives={'language_level': '3', 'embedsignature': True},
        annotate=True
    )

setup(
    name="traceutils2",
    version='1.0.8',
    author='Alex Marder',
    description="Various packages for traceroute analysis.",
    url="https://gitlab.com/alexander_marder/traceutils2",
    packages=find_packages(),
    install_requires=['ujson', 'orjson', 'cython', 'jsonschema'],
    # cmdclass={'build_ext': build_ext},
    # ext_modules=cythonize(
    #     extensions,
    #     compiler_directives={
    #         'language_level': '3',
    #         'embedsignature': True
    #     },
    #     annotate=True
    # ),
    entry_points={
        'console_scripts': [
            'tu2-addrs=traceutils2.scripts.tu_addrs:main',
            'tu2-adjs=traceutils2.scripts.tu_adjs:main',
            'tu2-pydig=traceutils2.scripts.tu_pydig:main'
        ],
    },
    ext_modules=extensions,
    zip_safe=False,
    package_data=package_data,
    include_package_data=True,
    python_requires='>3.6'
)
