#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
import logging
import numpy as np
from ._base import AnnotationParser, ParserType

__all__ = ['CvcParser']
log = logging.getLogger(__name__)


class CvcParser(AnnotationParser):
    """ This parser is designed to parse the `CVC <cvc_>`_ pedestrian dataset collection.
    The CVC format has one .txt file for every image of the dataset where each line within a file represents a bounding box.
    Each line is a space separated list of values structured as follows:

        <x> <y> <w> <h> <mandatory> <unknown> <unknown> <unknown> <unknown> <track_id> <unknown>

    =========  ===========
    Name       Description
    =========  ===========
    x          center x coordinate of the bounding box in pixels (integer)
    y          center y coordinate of the bounding box in pixels (integer)
    w          width of the bounding box in pixels (integer)
    h          height of the bounding box in pixels (integer)
    mandatory  1 if the pedestrian is mandatory for training and testing, 0 for optional
    track_id   identifier of the track this object is following (integer)
    =========  ===========

    Example:
        >>> image_000.txt
            97 101 18 52 1 0 0 0 0 1 0
            121 105 15 46 1 0 0 0 0 2 0
            505 99 14 41 1 0 0 0 0 3 0

    Note:
        The `mandatory` field is (de)serialized as the `ignore` column in the brambox dataframe. |br|
        If you serialize a dataframe without valid `id` values, they will be set to -1.

    Warning:
        This parser has only been tested to parse the CVC-08 and CVC-14 pedestrian datasets. |br|
        It will generate files according to the CVC-14 spec.
    """
    parser_type = ParserType.MULTI_FILE
    serialize_group = 'image'
    extension = '.txt'

    def __init__(self, class_label=''):
        super().__init__()
        self.add_column('class_label', class_label)
        if class_label == '':
            log.debug("No 'class_label' argument given, setting labels to empty string.")

    def pre_serialize(self, df):
        if df.class_label.nunique() > 1:
            log.error('This parser is meant for single-class problems and as such does not have the means to store class labels. All objects will be stored as the same class.')
        return df

    def serialize(self, df):
        result = ''

        for row in df.itertuples():
            if not np.isnan(row.id):
                idval = int(row.id)
            else:
                idval = -1
            result += f'{int(row.x_top_left)} {int(row.y_top_left)} {int(row.width)} {int(row.height)} {int(not row.ignore)} 0 0 0 0 {idval} 0\n'

        return result

    def deserialize(self, rawdata, file_id=None):
        self.append_image(file_id)

        for line in rawdata.splitlines():
            elements = line.split()

            data = {
                'x_top_left': float(elements[0]),
                'y_top_left': float(elements[1]),
                'width': float(elements[2]),
                'height': float(elements[3]),
                'ignore': (elements[4] == '0'),
            }

            try:
                idval = float(elements[9])
                if idval >= 0:
                    data['id'] = idval
            except IndexError:
                pass

            self.append(file_id, **data)
