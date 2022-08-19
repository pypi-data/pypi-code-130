#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base parser class
#
from enum import Enum
import numpy as np
import pandas as pd
from ... import util

__all__ = ['ParserType', 'Parser']


class ParserType(Enum):
    """ Enum for differentiating between different parser types. """
    UNDEFINED = 0       #: Undefined parsertype. Do not use this!
    SINGLE_FILE = 1     #: One single file contains all annotations
    MULTI_FILE = 2      #: One annotation file per :any:`brambox.io.parser.Parser.serialize_group`
    EXTERNAL = 3        #: External type that takes care of its own IO. Use this type sparingly as it is harder to test!


class Parser:
    """ This is a generic parser class.
    Custom parsers should inherit from this class and overwrite the :func:`~brambox.io.parser.Parser.serialize` and
    :func:`~brambox.io.parser.Parser.deserialize` functions, as well as the necessary parameters.

    Base data contains at least the following columns:
        - image (categorical): Image identifier
        - class_label (string): Class label
        - id (number, optional): unique id of the bounding box; Default **np.nan**
        - x_top_left (number): X pixel coordinate of the top left corner of the bounding box
        - y_top_left (number): Y pixel coordinate of the top left corner of the bounding box
        - width (number): Width of the bounding box in pixels
        - height (number): Height of the bounding box in pixels
    """
    parser_type = ParserType.UNDEFINED  #: Type of parser. Derived classes should set the correct value.
    extension = '.txt'                  #: Extension of the files this parser parses or creates. Derived classes should set the correct extension.
    read_mode = 'r'                     #: Reading mode this parser uses when it parses a file. Derived classes should set the correct mode.
    write_mode = 'w'                    #: Writing mode this parser uses when it generates a file. Derived classes should set the correct mode.
    pre_serialize = None                #: Function that runs before serialization and can modify the dataframe (takes a copy of the df as argument and must return a df)
    post_deserialize = None             #: Function that runs after deserialization and can modify the dataframe (takes a copy of the df as argument and must return a df)
    serialize_group = None              #: Controls on what column the dataframe gets grouped for serialization. If it is set to **None**, the dataframe does not get grouped, and the deserialize function receives each row seperately.
    serialize_group_separator = ''      #: Only for ParserType.SINGLE_FILE! Controls what character to place in between the different groups of text (usually images)
    header = ''                         #: Header string to put at the beginning of each file
    footer = ''                         #: Footer string to put at the end of each file

    def __init__(self):
        self.images = set()
        self.data = {
            'image': [],
            'class_label': [],
            'id': [],
            'x_top_left': [],
            'y_top_left': [],
            'width': [],
            'height': [],
        }
        self._default_values = {
            'id': np.nan,
        }

    def add_column(self, name, default=None):
        """ Add a new column to the data to be deserialized.

        Args:
            name (string): Name for the new column
            default (optional): Default value to be used if no value is given to :func:`~brambox.io.parser.Parser.append`; Default **no default, crash if no value given**

        Note:
            If you pass the name of an already existing column, you can overwrite its default value.
        """
        if default is not None:
            self._default_values[name] = default
        elif name in self._default_values:
            del self._default_values[name]

        cur_len = len(self.data['image'])
        if cur_len > 0:
            if default is None:
                raise ValueError('Data dictionary is not empty and no default value for new column given!')
            self.data[name] = [default] * cur_len
        else:
            self.data[name] = []

    def append_image(self, image):
        """ Call this function if there are no bounding boxes for a certain image.
        If you added a bounding box of an image with the :func:`~brambox.io.parser.Parser.append` method, it is not necessary to call this function,
        but doing so does not hurt either.
        """
        self.images.add(image)

    def append(self, image, **kwargs):
        """ Append a new bounding box to the dataframe.

        Args:
            image (string): image name the box belongs to
            kwargs: keyword arguments containing the values of this bounding box for all necessary columns
        """
        self.images.add(image)

        for col in self.data.keys():
            if col == 'image':
                self.data[col].append(image)
            elif col in kwargs:
                self.data[col].append(kwargs[col])
            elif col in self._default_values:
                self.data[col].append(self._default_values[col])
            else:
                raise KeyError(f'{col} not found in keyword arguments and has no default value')

    def get_df(self):
        """ This function generates a pandas dataframe from the dictionary in `self.data`,
        after the deserialize function generated that dictionary.
        """
        if isinstance(self.data, pd.DataFrame):
            return self.data

        df = util.from_dict(self.data, self.images)

        if self.post_deserialize is not None:
            df = self.post_deserialize(df)

        return df

    def serialize(self, df):
        """ This function needs to be implemented by the custom parser.
        Its goal is to return the rawdata (eg. string) from the bounding boxes of one `self.serialize_group`.
        """
        raise NotImplementedError('This function should be implemented in the custom parser')

    def deserialize(self, rawdata, file_id=None):
        """ This function needs to be implemented by the custom parser.
        It gets the rawdata from the file (eg. string) and needs to fill in the `self.data` dictionary
        with the correct values.
        """
        raise NotImplementedError('This function should be implemented in the custom parser')
