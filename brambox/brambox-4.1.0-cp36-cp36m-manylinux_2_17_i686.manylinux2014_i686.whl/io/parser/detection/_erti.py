#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
import logging
from ._base import DetectionParser, ParserType

__all__ = ['ErtiParser']
log = logging.getLogger(__name__)


class ErtiParser(DetectionParser):
    """ This parser is designed to parse the detection format of the ERTI_ challenge.

    Keyword Args:
        class_label (string, optional): class label name of the detections (this format only supports single object class detections)

    One text file per image:
    Each line is a comma separated list of values structured as follows:

        <x>,<y>,<width>,<height>,<score>

    =========  ===========
    Name       Description
    =========  ===========
    x          top left x coordinate of the bounding box in pixels (integer)
    y          top left y coordinate of the bounding box in pixels (integer)
    w          width of the bounding box in pixels (integer)
    h          height of the bounding box in pixels (integer)
    score      detection score between 0 and 1 (float)
    =========  ===========

    Example:
        >>> 000.txt
            503.75,213,20.5,50,74.8391

        >>> 001.txt
            540.8,166.4,37.4857,91.4286,56.4761
            519.034,186.602,31.6574,77.2131,51.2428
    """
    parser_type = ParserType.MULTI_FILE
    serialize_group = 'image'
    extension = '.txt'

    def __init__(self, class_label=''):
        super().__init__()
        self.add_column('class_label', class_label)

    def pre_serialize(self, df):
        if df.class_label.nunique() > 1:
            log.error('This parser is meant for single-class problems and as such does not have the means to store class labels. All objects will be stored as the same class.')
        return df

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            result += f'{round(row.x_top_left)},{round(row.y_top_left)},{round(row.width)},{round(row.height)},{row.confidence}\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)
        for line in rawdata.splitlines():
            elements = line.split(',')
            self.append(
                file_id,
                x_top_left=float(elements[0]),
                y_top_left=float(elements[1]),
                width=float(elements[2]),
                height=float(elements[3]),
                confidence=float(elements[4]),
            )
