#!/usr/bin/env python

from os import path, walk

import sys
from setuptools import setup, find_packages

try:
    # need recommonmark for build_htmlhelp command
    import recommonmark
except ImportError:
    pass



NAME = "Orange3-Finecon"

VERSION = "0.5.9"
# 0.3.x 增加调用R的方式，但是图形貌似会有一些问题？
## 0.3.7 修正R脚本中含有时间的对象转换失败。


AUTHOR = 'He Ray'
AUTHOR_EMAIL = 'hcmray@qq.com'

URL = 'http://orange.biolab.si/download'
DESCRIPTION = "Add-on containing 金融及经济 widgets"
LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.pypi'),
                        'r', encoding='utf-8').read()

LICENSE = "MIT"

KEYWORDS = (
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'FinEcon',
    '金融计量分析',
    '金融数据分析'
)

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.finecon': ['tutorials/*.ows'],
    'orangecontrib.finecon.widgets': ['icons/*'],
}

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(path.join(path.dirname(__file__), 'requirements.txt'))
) - {''})

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'FinEcon = orangecontrib.finecon',
    ),
    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'exampletutorials = orangecontrib.finecon.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/FinEcon/widgets/__init__.py
        'FinEcon = orangecontrib.finecon.widgets',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.finecon.widgets:WIDGET_HELP_PATH',)
}

NAMESPACE_PACKAGES = ["orangecontrib"]

TEST_SUITE = "orangecontrib.finecon.tests.suite"


def include_documentation(local_dir, install_dir):
    global DATA_FILES

    doc_files = []
    for dirpath, _, files in walk(local_dir):
        doc_files.append(
            (
                dirpath.replace(local_dir, install_dir),
                [path.join(dirpath, f) for f in files],
            )
        )
    DATA_FILES.extend(doc_files)


if __name__ == '__main__':
    include_documentation('doc/_build/html', 'help/orange3-FinEcon')
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=NAMESPACE_PACKAGES,
        zip_safe=False,
    )
