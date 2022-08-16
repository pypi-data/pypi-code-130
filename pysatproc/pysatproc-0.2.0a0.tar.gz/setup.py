# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['satproc', 'satproc.console', 'satproc.postprocess']

package_data = \
{'': ['*']}

install_requires = \
['Fiona>=1.8.21,<2.0.0',
 'Rtree>=0.9.7,<0.10.0',
 'Shapely>=1.8.1,<2.0.0',
 'numpy>=1.22.2,<2.0.0',
 'opencv-python>=4.5.5,<5.0.0',
 'packaging>=21.3,<22.0',
 'pyproj>=3.3.0,<4.0.0',
 'rasterio==1.3b1',
 'scikit-image>=0.19.2,<0.20.0',
 'scipy>=1.8.0,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['satproc_extract_chips = '
                     'satproc.console.extract_chips:run',
                     'satproc_filter = satproc.console.filter:run',
                     'satproc_generalize = satproc.console.generalize:run',
                     'satproc_make_masks = satproc.console.make_masks:run',
                     'satproc_match_histograms = '
                     'satproc.console.match_histograms:run',
                     'satproc_polygonize = satproc.console.polygonize:run',
                     'satproc_scale = satproc.console.scale:run',
                     'satproc_smooth_stitch = '
                     'satproc.console.smooth_stitch:run',
                     'satproc_spatial_filter = '
                     'satproc.console.spatial_filter:run']}

setup_kwargs = {
    'name': 'pysatproc',
    'version': '0.2.0a0',
    'description': 'Python library and CLI tools for processing geospatial imagery for ML',
    'long_description': None,
    'author': 'Damián Silvani',
    'author_email': 'munshkr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
