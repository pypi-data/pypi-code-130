"""
Brambox annotation parsers module |br|
These parsers can be used to parse and generate annotation files.
"""
from ._base import AnnotationParser

from ._coco import *
from ._cvc import *
from ._darknet import *
from ._dollar import *
from ._kitti import *
from ._mot import *
from ._pascalvoc import *
from ._vatic import *
from ._yaml import *

__all__ = ['AnnotationParser', 'annotation_formats']
annotation_formats = {
    'coco': CocoParser,
    'cvc': CvcParser,
    'darknet': DarknetParser,
    'dollar': DollarParser,
    'kitti': KittiParser,
    'mot': MotParser,
    'pascalvoc': PascalVocParser,
    'vatic': VaticParser,
    'yaml': YamlParser,
}
