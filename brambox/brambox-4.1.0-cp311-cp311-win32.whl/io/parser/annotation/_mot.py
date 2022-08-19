#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
import logging
import numpy as np
from ._base import AnnotationParser, ParserType

__all__ = ['MotParser']
log = logging.getLogger(__name__)


class MotParser(AnnotationParser):
    """ This parser is designed to parse the standard MOT_ multi object tracking dataset text files (https://arxiv.org/pdf/1906.04567.pdf).
    The MOT format contains all annotation from multiple video frames into one file.
    Each line of the file represents one bounding box from one image and is a spaces separated
    list of values structured as follows:

        <frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <valid>, <class_id>, <visibility>

    =========  ===========
    Name       Description
    =========  ===========
    frame      frame number that starts with 1 (integer)
    id         track id that starts with 1 (integer)
    bb_left    top left x coordinate of the bounding box (integer)
    bb_top     top left y coordinate of the bounding box (integer)
    bb_width   width of the bounding box (integer)
    bb_height  height of the bounding box (integer)
    valid      1 if the bounding box should be considered, 0 otherwise
    class_id   identifier of the object class (integer)
    visibility value between 0 and 1 that indicates how much of the object is visible (1 is fully visible, 0 is not visible)
    =========  ===========

    Note:
        Fields `valid` and `visibility` are currently ignored by brambox

    Example:
        >>> gt.txt
            1, 1, 794.2, 47.5, 71.2, 174.8, 1, 1, 0.8
            1, 2, 164.1, 19.6, 66.5, 163.2, 1, 1, 0.5
            2, 4, 781.7, 25.1, 69.2, 170.2, 0, 12, 1.

    Args:
        class_label_map (list):     list of class labels to translate a label to a class label index (the index in the list) and visa versa
        seq_length (int, optional): Number of images in the video sequence. If given, frames without annotations will also be registered.
    """
    parser_type = ParserType.SINGLE_FILE
    serialize_group_separator = '\n'
    extension = '.txt'

    def __init__(self, class_label_map=None, seq_length=None):
        super().__init__()

        self.class_label_map = class_label_map
        self.seq_length = seq_length
        if self.class_label_map is None:
            raise ValueError('MOT parser requires class_label_map argument')
        if self.seq_length is None:
            log.warning('Parameter `seq_length` not provided so I cannot register frames without annotations')

    def serialize(self, row):
        frame_id = int(row.image) + 1   # MOT id is base-1

        if not np.isnan(row.id):
            idval = int(row.id) + 1  # MOT id is base-1
        else:
            idval = -1

        class_label_index = self.class_label_map.index(row.class_label) + 1  # MOT id is base-1

        return f'{frame_id},{idval},{row.x_top_left:.1f},{row.y_top_left:.1f},{row.width:.1f},{row.height:.1f},1,{class_label_index},1.0'

    def deserialize(self, rawdata, file_id=None):
        # register all image ids up front if requested to avoid missing images
        if self.seq_length is not None:
            self.images = {f'{frame_nr:08}' for frame_nr in range(self.seq_length)}     # set comprehension

        for line in rawdata.splitlines():
            elements = line.split(',')
            frame_nr = int(elements[0]) - 1  # MOT frame nr is base-1

            class_label = self.class_label_map[int(elements[7]) - 1]    # MOT id is base-1
            data = {
                'class_label': class_label,
                'x_top_left': float(elements[2]),
                'y_top_left': float(elements[3]),
                'width': float(elements[4]),
                'height': float(elements[5]),
            }

            idval = float(elements[1]) - 1    # MOT id is base-1
            if idval >= 0:
                data['id'] = idval

            frame_id = f'{frame_nr:08}'
            self.append(frame_id, **data)
