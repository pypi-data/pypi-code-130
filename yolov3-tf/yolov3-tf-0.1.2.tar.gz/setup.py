# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yolov3_tf']

package_data = \
{'': ['*']}

install_requires = \
['opencv-python>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'yolov3-tf',
    'version': '0.1.2',
    'description': 'YOLOv3 implementation in TensorFlow 2.x',
    'long_description': '![CI](https://github.com/prp0x80/yolov3-tf2/actions/workflows/ci.yml/badge.svg?branch=develop?event=push)\n\n# YOLOv3-TF\n\nYOLOv3 implementation in TensorFlow 2.x\n\n## Installation\n\n```\npip install yolov3-tf\n```\n\n> Depends on tensorflow >=2.3.0 <=2.9.1\n\n## Usage\n\nThe package consists of three core modules -\n\n- dataset\n- models\n- utils\n\n### Dataset\n\nThe `dataset.py` module is for loading and transforming the tfrecords for object detection. The examples in the input tfrecords must match the parsing schema.\n\n```python\nimport yolov3_tf.dataset as dataset\ntrain_dataset = dataset.load_tfrecord_dataset(tfrecords_path)\ntrain_dataset = train_dataset.batch(batch_size)\ntrain_dataset = train_dataset.map(\n    lambda x, y: (\n        dataset.transform_images(x, image_dim),\n        dataset.transform_targets(y, anchors, anchor_masks, image_dim),\n    )\n)\n```\n\n### Models\n\nThe `models.py` module consists of implementation of two YOLOv3 and YOLOv3 tiny in Tesnsorflow.\n\n```python\nfrom yolov3_tf.models import YoloV3, YoloV3Tiny\nmodel = YoloV3(image_dim = 416, training=True, classes=10)\n```\n\n### Utils\n\nThe `utils.py` module provides some common functions for training YOLOv3 model, viz., loading weights, freezing layers, drawing boxes on images, compute iou\n\n```python\n# convert weights \nfrom yolov3_tf.models import YoloV3, YoloV3Tiny\nfrom yolov3_tf import utils\n\nyolo = YoloV3()\nutils.load_darknet_weights(yolo, weights_path, is_tiny=False)\nyolo.save_weights(converted_weights_path)\n```',
    'author': 'Prashant Patel',
    'author_email': 'prashant.patel@kainos.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/prp0x80/yolov3-tf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
