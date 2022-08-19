#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base annotation parser class
#
from .._base import Parser, ParserType

__all__ = ['ParserType', 'AnnotationParser']


class AnnotationParser(Parser):
    """ This is a generic annotations parser class.
    Custom parsers should inherit from this class and overwrite the :func:`~brambox.io.parser.Parser.serialize` and
    :func:`~brambox.io.parser.Parser.deserialize` functions, as well as the necessary parameters.

    Annotation data contains at least the following columns:
        - image (categorical): Image identifier
        - class_label (string): Class label
        - id (number, optional): unique id of the bounding box; Default **np.nan**
        - x_top_left (number): X pixel coordinate of the top left corner of the bounding box
        - y_top_left (number): Y pixel coordinate of the top left corner of the bounding box
        - width (number): Width of the bounding box in pixels
        - height (number): Height of the bounding box in pixels
        - occluded (number, optional): occlusion fraction; Default **0.0**
        - truncated (number, optional): truncation fraction; Default **0.0**
        - lost (boolean, optional): Whether the annotation is considered to be lost; Default **False**
        - difficult (boolean, optional): Whether the annotation is considered to be difficult; Default **False**
        - ignore (boolean, optional): Whether to ignore this annotation in certain metrics and statistics; Default **False**
    """
    def __init__(self):
        super().__init__()
        self.add_column('occluded', 0.0)
        self.add_column('truncated', 0.0)
        self.add_column('lost', False)
        self.add_column('difficult', False)
        self.add_column('ignore', False)
