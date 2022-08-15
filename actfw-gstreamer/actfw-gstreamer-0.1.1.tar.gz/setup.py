# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['actfw_gstreamer', 'actfw_gstreamer.gstreamer']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=5,<6',
 'PyGObject>=3,<4',
 'actfw-core>=2.0.0,<3.0.0',
 'result>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'actfw-gstreamer',
    'version': '0.1.1',
    'description': "actfw's additional components using GStreamer",
    'long_description': '# actfw-gstreamer\n\nactfw\'s components using GStreamer for implementation.\nactfw is a framework for Actcast Application written in Python.\n\n## Installation\n\n```console\nsudo apt-get update\nsudo apt-get install -y python3-pip python3-pil \nsudo apt-get install libgstreamer1.0-dev libgirepository1.0-dev ibgstreamer-plugins-base1.0-dev libglib2.0-dev\npip3 install actfw-gstreamer\n```\n\n## Document\n\n- [API References](https://idein.github.io/actfw-gstreamer/latest/)\n\n## Usage\n\nSee [actfw-core](https://github.com/Idein/actfw-core) for basic usage of `actfw` framework.\n\n### Initalization\n\nAn application using `actfw-gstreamer` have to initialize GStreamer library before using `actfw-gstreamer`\'s components.\n\n```python\nif __name__ == \'__main__\':\n    import gi\n\n    gi.require_version(\'Gst\', \'1.0\')\n    from gi.repository import Gst\n    Gst.init(None)\n\n    main()\n```\n\n### `videotestsrc`\n\nYou can learn basic usage of `actfw-gstreamer` by using `videotestsrc`.\n\n```python\nfrom actfw_gstreamer.capture import GstreamerCapture\nfrom actfw_gstreamer.gstreamer.converter import ConverterPIL\nfrom actfw_gstreamer.gstreamer.stream import GstStreamBuilder\nfrom actfw_gstreamer.restart_handler import SimpleRestartHandler\n\n\ndef videotestsrc_capture() -> GstreamerCapture:\n    pipeline_generator = preconfigured_pipeline.videotestsrc()\n    builder = GstStreamBuilder(pipeline_generator, ConverterPIL())\n    restart_handler = SimpleRestartHandler(10, 5)\n    return GstreamerCapture(builder, restart_handler)\n\n\ndef main():\n    app = actfw_core.Application()\n\n    capture = videotestsrc_capture()\n    app.register_task(capture)\n\n    consumer = YourConsumer()\n    app.register_task(consumer)\n\n    capture.connect(consumer)\n\n    app.run()\n```\n\nThis generates [`Frame`](https://idein.github.io/actfw-core/latest/actfw_core.html#actfw_core.capture.Frame)s using [videotestsrc](https://gstreamer.freedesktop.org/documentation/videotestsrc/index.html).\n\n- `GstreamerCapture` is a [`Producer`](https://idein.github.io/actfw-core/latest/actfw_core.task.html#actfw_core.task.producer.Producer).\n  - It generates `Frame`s consists of an output of `ConverterBase`.  In this case, converter class is `ConverterPIL` and output is `PIL.Image.Image`.\n- `GstStreamBuilder` and `PipelineGenerator` determines how to build gstreamer pipelines.\n- `preconfigured_pipeline` provides preconfigured `PipelineGenerator`s.\n- `SimpleRestartHandler` is a simple implementation of `RestartHandlerBase`, which determines "restart strategy".\n\nFor more details, see [tests](tests/intergation_test/test_gstreamer_output.py).\n\n### `rtspsrc`\n\nYou can use [rtspsrc](https://gstreamer.freedesktop.org/documentation/rtsp/rtspsrc.html) using `preconfigured_pipeline.rtsp_h264()`.\n\nNote that, as of now (2021-04), [Actcast application](https://actcast.io/docs/ForVendor/ApplicationDevelopment/) cannot use multicast UDP with dynamic address and unicast UDP.\n(RTSP client communicates with RTSP server in RTP and determines adderss of mulitcast UDP.)\nTherefore, you can use only the option `protocols = "tcp"`.\nSee also https://gstreamer.freedesktop.org/documentation/rtsp/rtspsrc.html#rtspsrc:protocols .\n\nYou should also pay attention to decoders. Available decoders are below:\n\n| decoder (package) \\ device                                     | Raspberry Pi 3 | Raspberry Pi 4 | Jetson Nano |\n| -------------------------------------------------------------- | -------------- | -------------- | ----------- |\n| `omxh264` (from `gstreamer1.0-omx` and `gstreamer1.0-omx-rpi`) | o              | x              | ?           |\n| `v4l2h264dec` (from `gstreamer1.0-plugins-good`)               | very slow      | o              | ?           |\n\nIf your application supports various devices, you should branch by hardware types and select appropriate `decoder_type`.\nFor example, it is recommended to use `decoder_type` `omx` for Raspberry Pi 3 and `v4l2` for Raspberry Pi 4.\nCurrently, this library does not provide auto determination.\n\n## Development Guide\n\n### Installation of dev requirements\n\n```console\npip3 install poetry\npoetry install\n```\n\n### Running tests\n\n```console\npoetry run nose2 -v\n```\n\n### Releasing package & API doc\n\nCI will automatically do.\nFollow the following branch/tag rules.\n\n1. Make changes for next version in `master` branch (via pull-requests).\n2. Make a PR that updates version in `pyproject.toml` and merge it to `master` branch.\n3. Create GitHub release from `master` branch\'s HEAD.\n    1. [Draft a new release](https://github.com/Idein/actfw-gstreamer/releases/new).\n    2. Create new tag named `release-<New version>` (e.g. `release-1.4.0`) from `Choose a tag` pull down menu.\n    3. Write title and description.\n    4. Publish release.\n4. Then CI will build/upload package to PyPI & API doc to GitHub Pages.\n',
    'author': 'Idein Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Idein/actfw-gstreamer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
