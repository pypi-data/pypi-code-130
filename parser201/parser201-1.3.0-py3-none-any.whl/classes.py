"""LogParser Class."""

import datetime as dt
import re
import time
from enum import Enum
from enum import auto


class TZ(Enum):
    """Timestamp adjustment enum.

    Enum to determine the timezone adjustment of the timestamp property
    of a `LogParser` object.
    """

    original = auto()
    local = auto()
    utc = auto()

    def __eq__(self, other):
        """Compare the values of two TZ Enums.

        Parameters
        ----------
        other : Any
            The right-hand side of the equality comparison.

        Returns
        -------
        bool
            True if two TZ Enums are equal, False otherwise.
        """
        return self.value == other.value


class FMT(Enum):
    """Format enum.

    Enum to determine the format for the timestamp attribute of a
    `LogParser` object.
    """

    string = auto()
    date_obj = auto()

    def __eq__(self, other):
        """Compare the values of two FMT Enums.

        Parameters
        ----------
        other : Any
            The right-hand side of the equality comparison.

        Returns
        -------
        bool
            True if two FMT Enums are equal, False otherwise.
        """
        return self.value == other.value


class LogParser:
    """The `LogParser` Class.

    The class initializer takes a single line (as a string) from an
    Apache access log file and extracts the individual fields into
    attributes within an object.

    Arguments
    ---------
    line : str
        A single line from an Apache access log.
    timezone : TZ, optional
        During parsing, adjust the timestamp of the `LogParser` object
        to match a particular timezone. Default is *TZ.original* (no
        adjustment). *TZ.local* adjusts the timestamp to the timezone
        currently selected on the machine running the code. *TZ.utc*
        adjusts the timestamp to [UTC](https:\
        //en.wikipedia.org/wiki/Coordinated_Universal_Time), default is
        TZ.original.
    dts_format : FMT, optional
        Set the format of the date timestamp attribute of the
        `LogParser` object. Default is *FMT.string*. Using
        *FMT.date_obj* will store the timestamp attribute as a Python
        [datetime object](https:\
        //docs.python.org/3/library/datetime.html), default is
        FMT.string.

    Attributes
    ----------
    datasize : int
        The size of the response to the client (in bytes).
    ipaddress : str
        The remote host (the client IP).
    referrer : str
        The referrer header of the HTTP request containing the URL of
        the page from which this request was initiated. If none is
        present, this attribute is set to `-`.
    requestline : str
        The request line from the client. (e.g. `"GET / HTTP/1.0"`).
    statuscode : int
        The status code sent from the server to the client (`200`,
        `404`, etc.).
    timestamp : str | dt.datetime
        The date and time of the request in the following format:

        `dd/MMM/YYYY:HH:MM:SS –hhmm`

        NOTE: `-hhmm` is the time offset from Greenwich Mean Time (GMT).
        Usually (but not always) `mm == 00`. Negative offsets (`-hhmm`)
        are west of Greenwich; positive offsets (`+hhmm`) are east of
        Greenwich.
    useragent : str
        The browser identification string if any is present, and `-`
        otherwise.
    userid : str
        The identity of the user determined by `identd` (not usually
        used since not reliable). If `identd` is not present, this
        attribute is set to `-`.
    username : str
        The user name determined by HTTP authentication. If no username
        is present, this attribute is set to `-`.

    Examples
    --------
    Creating a `LogParser` object with default options. The timestamp
    attribute will not be adjusted and will be stored as a string.
    >>> from parser201 import LogParser
    >>> line = # a line from an Apache access log
    >>> lp = LogParser(line)

    Creating a `LogParser` object with custom options. The timestamp
    attribute will be adjusted to the timezone on the local machine and
    will be stored as a Python [datetime object](https:\
    //docs.python.org/3/library/datetime.html).
    >>> from parser201 import LogParser, TZ, FMT
    >>> line = # a line from an Apache access log
    >>> lp = LogParser(line, timezone=TZ.local, dts_format=FMT.date_obj)
    """

    def __init__(self, line, timezone=TZ.original, dts_format=FMT.string):

        # Establish attributes
        self.ipaddress = ''
        self.userid = ''
        self.username = ''
        self.timestamp = ''
        self.requestline = ''
        self.referrer = ''
        self.useragent = ''
        self.statuscode = 0
        self.datasize = 0

        # Initial check. If the line passed to the initializer is not a string
        # (type == str), then return an empty LogParser object.
        if type(line) != str:
            self.__none_fields()
            return

        # If a valid string is entered, then perform pre-processing. For some
        # lines, an empty field is represented as two quotes back-to-back, like
        # this: "". The regex to pull out agent strings between quotes will
        # incorrectly ignore that field, rather than returning an empty string.
        # Replace "" with "-" to prevent that.
        clean = line.replace('\"\"', '\"-\"')

        # agent_strings: This part of the regex:(?<!\\)\" is a negative
        # lookbehind assertion. It says, "end with a quote mark, unless that
        # quote mark is preceded by an escape character '\'"
        agent_strings = re.findall(r'\"(.+?)(?<!\\)\"', clean)

        # The next one's tricky. We're looking to extract the statuscode and
        # datasize fields. For some entires, the datasize field is '-', but for
        # all entries the returncode field is a reliable integer. If we split
        # the log line on space, then the first purely isnumeric() item in the
        # resulting list should be the returncode. If we capture the index of
        # that code, and take that code and the one next to it from the list,
        # we should have both fields. If the fields are valid integers, then
        # cast to them int; else set them to 0. If any of this fails, then
        # consider that we have a malformed log line and set all the properties
        # to None.
        try:
            L = clean.split(' ')
            i = [j for j in range(len(L)) if L[j].isnumeric()][0]
            code_and_size = [int(n) if n.isnumeric() else 0 for n in L[i:i+2]]
            # Splitting on '[' returns a list where item [0] contains the first
            # three fields (ipaddress; userid; username), each separated by
            # space.
            first3 = clean.split('[')[0].split()
        except Exception:
            self.__none_fields()
            return

        # Set properties. If any of these fail, then consider that we have a
        # malformed log line and set all the properties to None.
        try:
            self.ipaddress = first3[0]
            self.userid = first3[1]
            self.username = first3[2]
            self.timestamp = re.search(
                r'\[(.+?)\]', clean).group().strip('[]')
            self.requestline = agent_strings[0]
            self.referrer = agent_strings[1]
            self.useragent = agent_strings[2]
            self.statuscode = code_and_size[0]
            self.datasize = code_and_size[1]
        except Exception:
            self.__none_fields()
            return

        # Process date/time stamp and adjust timezone/dts_format as indicated
        if timezone == TZ.original and dts_format == FMT.string:
            return

        try:
            date_obj = dt.datetime.strptime(self.timestamp,
                                            '%d/%b/%Y:%H:%M:%S %z')
        except ValueError:
            self.__none_fields()
            return

        sign, hh, mm = self.__decomposeTZ(self.timestamp)

        if timezone == TZ.original:
            pass
        elif timezone == TZ.local:
            zone_str = time.strftime('%z')
            # First convert to GMT
            date_obj = date_obj + (-1*sign*dt.timedelta(hours=hh, minutes=mm))
            # Now convert to local time and replace tzinfo
            sign, hh, mm = self.__decomposeTZ(zone_str)
            zone_obj = dt.timezone(dt.timedelta(hours=hh*sign, minutes=mm))
            date_obj = date_obj + (sign*dt.timedelta(hours=hh, minutes=mm))
            date_obj = date_obj.replace(tzinfo=zone_obj)
        else:  # TZ == utc
            date_obj = date_obj + (-1*sign*dt.timedelta(hours=hh, minutes=mm))
            sign, hh, mm = self.__decomposeTZ('+0000')
            zone_obj = dt.timezone(dt.timedelta(hours=0, minutes=0))
            date_obj = date_obj.replace(tzinfo=zone_obj)

        if dts_format == FMT.string:
            self.timestamp = date_obj.strftime('%d/%b/%Y:%H:%M:%S %z')
        else:  # dts_format == FMT.date_obj
            self.timestamp = date_obj

        return

    def __none_fields(self):
        """Set all properties to None."""
        for prop in [p for p in dir(self) if not p.startswith('_')]:
            setattr(self, prop, None)
        return

    def __str__(self):
        """`LogParser` class str method.

        The class provides a `__str__` method which renders a
        `LogParser` object as string suitable for display.

        Examples
        --------
        Create a `LogParser` object like this:

        >>> from parser201 import LogParser
        >>> line = # a line from an Apache access log
        >>> lp = LogParser(line)

        When you print it, the following is displayed:

        >>> print(lp)
          ipaddress: 81.48.51.130
             userid: -
           username: -
          timestamp: 24/Mar/2009:18:07:16 +0100
        requestline: GET /images/puce.gif HTTP/1.1
         statuscode: 304
           datasize: 2454
           referrer: -
          useragent: Mozilla/4.0 compatible; MSIE 7.0; Windows NT 5.1;
        """
        labels = ['ipaddress', 'userid', 'username', 'timestamp',
                  'requestline', 'statuscode', 'datasize', 'referrer',
                  'useragent']
        pad = len(max(labels, key=len))
        L = []

        # Build the string in the same order as the labels.
        for label in labels:
            L.append(f'{label:>{pad}}: {getattr(self, label)}')
        return '\n'.join(L)

    def __eq__(self, other):
        """Determine if two `LogParser` objects are equal.

        The class provides a `__eq__` method to test for equality
        between two `LogParser` objects.

        Parameters
        ----------
        other : Any
            An object used for comparison (the right-hand side of ==).

        Returns
        -------
        bool
            True it two `LogParser` objects are equal, False otherwise.
        """
        if type(self) != type(other):
            return False
        for prop in [p for p in dir(self) if not p.startswith('_')]:
            if getattr(self, prop) != getattr(other, prop):
                return False
        return True

    def __decomposeTZ(self, zone):
        """Decompose a time zone into +/-, hrs, and mins."""
        leader, hrs, mins = zone[-5], zone[-4:-2], zone[-2:]
        sign = -1 if leader == '-' else 1
        return sign, int(hrs), int(mins)


if __name__ == '__main__':  # pragma no cover
    pass
