# Copyright (c) 2018, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import copy
from collections import OrderedDict


class SmartFilenamePart:
    """ Represents a part of filename. """

    def __init__(self, arg, start=0, length=None, delimiter="_", pad="-", decoder=None, encoder=None, compact=False):
        """
        Constructor of SmartFilenamePart class.

        Parameters
        ----------
        arg: object
            Input argument, which can be a string or the decoded part of the filename.
        start: int, optional
            Start index of filename part (default is 0).
        length: int, optional
            Length of filename part.
        delimiter : str, optional
            Delimiter (default: '_')
        pad : str, optional
            Padding symbol (default: '-').
        decoder: function, optional
            Decodes a certain value (str -> object).
        encoder: function, optional
            Encodes a certain value (object -> str).
        """

        self.arg = arg
        self.start = start
        self.delimiter = delimiter
        self.pad = pad
        self.compact = compact
        self.decoder = (lambda x: x) if decoder is None else decoder
        self.encoder = (lambda x: x) if encoder is None else encoder
        length = 0 if compact else length
        self.length = length if length is not None and length != 0 else len(self.encoded)

        # check validity
        if not self.has_valid_len():
            err_msg = "Length does not comply with definition: {:} > {:}".format(len(self), self.length)
            raise ValueError(err_msg)

    def has_valid_len(self):
        """
        Checks if a SmartFilenamePart instance has a valid len.
        It is valid if the specified length is equal to the length of the SmartFilenamePart,
        or if len == 0, i.e accepting any length.

        Returns
        -------
        bool
            True if SmartFilenamePart instance is valid, else False.
        """

        # 0 for accepting any length
        if self.length == 0 or self.compact:
            check = True
        else:
            check = self.length == len(self)

        return check

    @property
    def encoded(self):
        """
        Converts filename part to an encoded (string) representation.

        Returns
        -------
        str
            Encoded (string) representation of a filename part.
        """
        return self.encoder(self.arg)

    @property
    def decoded(self):
        """
        Converts filename part to a decoded (object) representation.

        Returns
        -------
        object
            Decoded (object) representation of a filename part.
        """

        enc_wo_pad = self.encoded.strip(self.pad)
        if enc_wo_pad != '':
            return self.decoder(enc_wo_pad)
        else:
            return None

    def __str__(self):
        """
        Returns the string representation of the field.

        Returns
        -------
        str
            String representation of the class.
        """
        if self.compact and self.arg == "":
            return ''
        return self.encoded.ljust(self.length, self.pad)

    def __repr__(self):
        """
        Returns the class representation, which is the field + delimiter.

        Returns
        -------
        str
            String representation of the class.
        """
        return str(self) + self.delimiter

    def __len__(self):
        """
        Returns length of the filename part.

        Returns
        -------
        int
            Length of the filename part.
        """

        return len(str(self))

    def __add__(self, other):
        """
        Defines summation rule for two SmartFilenamePart/str instances.

        Parameters
        ----------
        other: SmartFilenamePart, str
            Second summand.

        Returns
        -------
        str
            Concatenated strings separated by a delimiter.
        """

        return repr(self) + str(other)


class SmartFilename(object):

    """
    SmartFilename class handles file names with pre-defined field names
    and field length.
    """

    def __init__(self, fields, fields_def, ext=None, pad='-', delimiter='_', convert=False, compact=False):
        """
        Define name of fields, length, pad and delimiter symbol.

        Parameters
        ----------
        fields : dict
            Name of fields (keys) and (values).
        fields_def : OrderedDict
            Name of fields (keys) in right order and length (values). It must contain:
                - "len": int
                    Length of filename part (must be given).
                    "0" to allow any length.
                - "start": int, optional
                    Start index of filename part (default is 0).
                - "delim": str, optional
                    Delimiter between this and the following filename part (default is the one from the parent class).
                - "pad": str,
                    Padding for filename part (default is the one from the parent class).
        ext : str, optional
            File name extension (default: None).
        pad : str, optional
            Padding symbol (default: '-').
        delimiter : str, optional
            Delimiter (default: '_')
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).
        compact: bool, optional
            If true, empty fields are replaced by a single pad character instead of the whole length.
        """
        self.ext = ext
        self.delimiter = delimiter
        self.pad = pad
        self.convert = convert
        self.compact = compact
        self._fn_map = self.__build_map(fields, fields_def)
        self.obj = self.__init_filename_obj()

    @classmethod
    def from_filename(cls, filename_str, fields_def, pad="-", delimiter="_", convert=False, compact=False):
        """
        Converts a filename given as a string into a SmartFilename class object.

        Parameters
        ----------
        filename_str : str
            Filename without any paths (e.g., "M20170725_test.tif").
        fields_def : OrderedDict
            Name of fields (keys) in right order and length (values). It must contain:
                - "len": int
                    Length (positive number) of filename part (must be given).
                    0 to allow any length.
                - "start": int, optional
                    Start index of filename part (default is 0).
                - "delim": str, optional
                    Delimiter between this and the following filename part (default is the one from the parent class).
                - "pad": str,
                    Padding for filename part (default is the one from the parent class).
        pad : str, optional
            Padding symbol (default: '-').
        delimiter : str, optional
            Delimiter (default: '_')
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).

        Returns
        -------
        SmartFilename
            Class representing a filename.
        """

        # get extensions from filename
        ext = os.path.splitext(filename_str)[1]

        fields = dict()
        pos = 0
        for name, value in fields_def.items():
            start = value.get('start')
            length = value.get('len')
            delim = value.get('delim')

            if length is not None and length < 0:
                err_msg = "The length of the attribute '{}' must be a positive number".format(name)
                raise ValueError(err_msg)

            # parse part of filename via start and end position
            if start is not None and length is not None:
                fields[name] = filename_str[start:(start + length)]
            elif length is not None:
                start = pos
                if compact:
                    length = 0
                    if delim is None and delimiter is None:
                        raise Exception('The compact filename design requires a delimiter for each field!')

                if length == 0:  # handle variable length
                    end = filename_str.find(delimiter, start) if delimiter in filename_str[start:] \
                        else filename_str.find('.', start)
                    length = end - start
                # if length is not 0, i.e. an entry is available, then add the field. Otherwise skip it.
                if length > 0:
                    fields[name] = filename_str[start:(start + length)]
            else:
                length = 0

            pos += length

            if delim is not None:
                pos += len(delim)
            else:
                pos += len(delimiter)

        if cls.__name__ == "SmartFilename":
            return cls(fields, fields_def, ext=ext, convert=convert, pad=pad, delimiter=delimiter)
        else:
            return cls(fields, ext=ext, convert=convert)

    def __init_filename_obj(self):
        """
        Initialises the class 'FilenameObj' to set all filename attributes as class variables.
        This enables an easier access to filename properties.

        Returns
        -------
        FilenameObj

        """

        class FilenameObj(object):
            def __init__(self):
                pass

        filename_obj = FilenameObj()
        for name, fn_part in self._fn_map.items():
            if self.convert:
                setattr(filename_obj, name, fn_part.decoded)
            else:
                setattr(filename_obj, name, fn_part.encoded)

        return filename_obj

    def __build_map(self, fields, fields_def):
        """
        Creates a dictionary/map between filename part names and SmartFilenamePart instances.

        Paramaters
        ----------
        fields : dict
            Name of fields (keys) and (values).
        fields_def : OrderedDict
            Name of fields (keys) in right order and length (values). It must contain:
                - "len": int
                    Length (positive number) of filename part (must be given).
                    0 to allow any length.
                - "start": int, optional
                    Start index of filename part (default is 0).
                - "delim": str, optional
                    Delimiter between this and the following filename part (default is the one from the parent class).
                - "pad": str,
                    Padding for filename part (default is the one from the parent class).

        Returns
        -------
        dict
            Contains SmartFilenamePart instances representing each part of the filename.
        """

        # check fields consistency
        for key in fields.keys():
            if key not in fields_def.keys():
                raise KeyError("Field name undefined: {:}".format(key))

        fn_map = OrderedDict()
        last_key_name = list(fields_def.keys())[-1]
        for name, keys in fields_def.items():
            if name not in fields:
                elem = ""
            else:
                elem = fields[name]

            fn_part_kwargs = dict()
            if 'delim' not in keys:
                fn_part_kwargs['delimiter'] = self.delimiter
            else:
                fn_part_kwargs['delimiter'] = keys['delim']

            if 'len' in keys:
                # check delimiter in case of zero length
                if keys['len'] == 0 and fn_part_kwargs['delimiter'] == '':
                    err_msg = 'A variable field length (length = 0) requires a delimiter!'
                    raise ValueError(err_msg)

                if keys['len'] < 0:
                    err_msg = "The length of the attribute '{}' must be a positive number".format(name)
                    raise ValueError(err_msg)

                fn_part_kwargs['length'] = keys['len']

            if 'decoder' in keys:
                fn_part_kwargs['decoder'] = keys['decoder']
            if 'encoder' in keys:
                fn_part_kwargs['encoder'] = keys['encoder']
            fn_part_kwargs['compact'] = self.compact

            if name == last_key_name:  # set empty delimiter for last field
                fn_part_kwargs['delimiter'] = ''

            # reset delimiter of last element to be empty
            smart_fn_part = SmartFilenamePart(elem, **fn_part_kwargs)
            fn_map[name] = smart_fn_part

        return fn_map

    def _build_fn(self):
        """
        Build file name based on fields, padding and length.

        Returns
        -------
        filename : str
            Filled file name.

        """

        fn_parts = list(self._fn_map.values())

        filename = ''.join([repr(fn_part) for fn_part in fn_parts])

        # handle case if last field is not defined (skip the last delimeter then)
        if filename.endswith(self.delimiter):
            filename = filename[:-1]

        if self.ext is not None:
            filename += self.ext

        return filename

    def _get_field(self, name):
        """
        Returns the value of the field with a given key.

        Parameters
        ----------
        name : str
            Name of the field.

        Returns
        -------
        str, object
            Part of the filename associated with given key. Depending on the chosen flag 'convert', it is either a str
            (convert=False) or an object.
        """

        # check and reset the attribute of the object variable
        field_from_obj = self._fn_map[name].encoder(getattr(self.obj, name))
        if field_from_obj and (field_from_obj != self._fn_map[name].encoded):
            fn_part = copy.deepcopy(self._fn_map[name])
            fn_part.arg = field_from_obj
            if fn_part.has_valid_len():
                self._fn_map[name] = fn_part

        if self.convert:
            return self._fn_map[name].decoded
        else:
            return self._fn_map[name].encoded.strip(self._fn_map[name].pad)

    def __getitem__(self, name):
        """
        Returns the value of the field with a given key.

        Parameters
        ----------
        name : str
            Name of the field.

        Returns
        -------
        str, object
            Part of the filename associated with given key. Depending on the chosen flag 'convert', it is either a str
            (convert=False) or an object. If the key can't be found in the fields definition, the method tries to return
            a property of an inherited class.
        """

        if name in self._fn_map:
            return self._get_field(name)
        elif hasattr(self, name):
            return getattr(self, name)
        else:
            raise KeyError('"{}" is neither a class variable nor a file attribute.'.format(name))

    def __setitem__(self, name, value):
        """
        Sets the value of a filename field corresponding to the given key.

        Parameters
        ----------
        name : str
            Name of the field.
        value: object
            Value of the field.

        """

        if name in self._fn_map:
            fn_part = copy.deepcopy(self._fn_map[name])
            fn_part.arg = value
            if self.compact:
                fn_part.length = 0
            if not fn_part.has_valid_len():
                err_msg = "Length does not comply with definition: {:} > {:}".format(len(fn_part.encoded),
                                                                                     fn_part.length)
                raise ValueError(err_msg)
            else:
                self._fn_map[name] = fn_part
                value = fn_part.encoded.replace(self.pad, '')
                if self.convert:
                    setattr(self.obj, name, fn_part.decoded)
                else:
                    setattr(self.obj, name, value)
        else:
            raise KeyError("Field name undefined: {:}".format(name))

    def __repr__(self):
        """
        Returns the string representation of the class.

        Returns
        -------
        str
            String representation of the class.
        """

        return self._build_fn()
