# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yoloair',
 'yoloair.docs.attention_model',
 'yoloair.models',
 'yoloair.models.Detect',
 'yoloair.models.Models',
 'yoloair.models.Models.Attention',
 'yoloair.tools',
 'yoloair.utils',
 'yoloair.utils.aws',
 'yoloair.utils.flask_rest_api',
 'yoloair.utils.loggers',
 'yoloair.utils.loggers.wandb']

package_data = \
{'': ['*'],
 'yoloair': ['configs/PicoDet/*',
             'configs/attention/*',
             'configs/backbone/*',
             'configs/head-Improved/*',
             'configs/lightmodels/*',
             'configs/research/*',
             'configs/scaled_yolov4/*',
             'configs/transformer/*',
             'configs/yolo-FaceV2/*',
             'configs/yolo-lite/*',
             'configs/yolor/*',
             'configs/yolov3/*',
             'configs/yolov4/*',
             'configs/yolov5-Improved/*',
             'configs/yolov5-Improved/SPD-Conv/*',
             'configs/yolov5-standard/*',
             'configs/yolov5/*',
             'configs/yolov7/train/*',
             'configs/yolox-Improved/*',
             'configs/yolox/*',
             'data/*',
             'data/hyps/*',
             'data/images/*',
             'data/scripts/*',
             'docs/document/*',
             'docs/image/*'],
 'yoloair.docs.attention_model': ['img/*'],
 'yoloair.utils': ['google_app_engine/*']}

install_requires = \
['Pillow>=7.1.2',
 'PyYAML>=5.3.1',
 'computation',
 'flops>=0.1.4,<0.2.0',
 'matplotlib>=3.2.2',
 'numpy>=1.18.5',
 'opencv-python>=4.1.2',
 'pandas>=1.1.4',
 'requests>=2.23.0',
 'seaborn>=0.11.0',
 'tensorboard>=2.4.1',
 'thop>=0.1.1,<0.2.0',
 'timm>=0.6.7,<0.7.0',
 'torch>=1.12',
 'torchvision>=0.8.1',
 'tqdm>=4.41.0']

entry_points = \
{'console_scripts': ['yoloair_detect = yoloair.detect:entrypoint',
                     'yoloair_train = yoloair.train:entrypoint']}

setup_kwargs = {
    'name': 'yoloair',
    'version': '2022.8.20',
    'description': '',
    'long_description': None,
    'author': 'iscyy',
    'author_email': None,
    'maintainer': 'David Francos',
    'maintainer_email': 'me@davidfrancos.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
