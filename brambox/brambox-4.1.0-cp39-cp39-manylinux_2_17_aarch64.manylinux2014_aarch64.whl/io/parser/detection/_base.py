#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base detection parser class
#
from .._base import Parser, ParserType

__all__ = ['ParserType', 'DetectionParser']


class DetectionParser(Parser):
    """ This is a generic detections parser class.
    Custom parsers should inherit from this class and overwrite the :func:`~brambox.io.parser.Parser.serialize` and
    :func:`~brambox.io.parser.Parser.deserialize` functions, as well as the necessary parameters.

    Detection data contains at least the following columns:
        - image (categorical): Image identifier
        - class_label (string): Class label
        - id (number, optional): unique id of the bounding box; Default **np.nan**
        - x_top_left (number): X pixel coordinate of the top left corner of the bounding box
        - y_top_left (number): Y pixel coordinate of the top left corner of the bounding box
        - width (number): Width of the bounding box in pixels
        - height (number): Height of the bounding box in pixels
        - confidence (number): Confidence value of the detection
    """
    def __init__(self):
        super().__init__()
        self.add_column('confidence')
