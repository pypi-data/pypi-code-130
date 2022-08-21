# --------------------------------------------------------------------------- #
#   Proofscape Utilities                                                      #
#                                                                             #
#   Copyright (c) 2021-2022 Proofscape contributors                           #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# --------------------------------------------------------------------------- #


class StringAwareCodeScanner:
    """
    Scans strings which are to be understood as representing code in some
    language in which strings may be defined, using various delimiters.

    This class should be subclassed in order to make a custom scanner that
    does something useful, while being aware of whether it is inside a string
    definition or not.

    Subclasses should pass the desired string types to our __init__ method,
    and then define as many `state_NAME` methods as they want.

    The supported string types are:
        d1: "
        d3: "*3
        s1: '
        s3: '*3

    Each `state_NAME` method must:
        Accept two args, (c, i), the current char and current scanning index.
        Return two args, (next_state, di), where:
            next_state: if not None, we go to this state next
            di: if not None, we add this to the scanning index.

    Note that +1 is _always_ added to the scanning index, on every iteration,
    whether or not a subclass method returns `di` not `None`. Note also that
    when entering or exiting a triple-quoted string, another +2 is also added
    to the scanning index.

    The entire code string being scanned, and its length, are available under
    `self.code` and `self.N`. The state we will switch to next, if the
    subclass method does not override it, is under `self.planned_next_state`.
    (If `self.planned_next_state` is `None`, it means we plan to stay in the
    current state.)

    State 0 is the state in which we begin, and the only state in which we
    will detect the beginning of a string. Thus, this should be thought of
    as the basic "outside a string, but a string may begin at any moment"
    state.

    Subclasses therefore will generally want to define a `state_0` method.
    However, they probably should return `None` for both `next_state` and `di`
    when `c` is " or '.

    Subclasses _may_ define `state_d1`, `state_d3`, `state_s1`, `state_s3`,
    methods, but should be careful.

    The name "BREAK" cannot be used as a state name. If a state method returns
    "BREAK" as the next desired state, this will cause the scanning process to
    end immediately.

    Otherwise, any state names may be used.

    The `scan()` method scans a given code string. It does not return anything.
    Whatever a subclass may wish to build or learn by scanning, it is up to it
    to somehow record or do something with the results.
    """

    BREAK = "BREAK"

    def __init__(self, accepted_string_types, ignore_escapes=None):
        """
        @param accepted_string_types: iterable indicating which types of strings,
            i.e. which string delimiters, we are to be aware of. Allowed values
            are:
                d1: "
                s1: '
                d3: "*3
                s3: '*3
        @param ignore_escapes: optional iterable of string types in which we
            should ignore escapes, i.e. in which a backslash preceding a
            delimiter does _not_ make us ignore that delimiter.
        """
        self.accepted_string_types = set(accepted_string_types) & {'d1', 'd3', 's1', 's3'}
        self.ignore_escapes = set(ignore_escapes or []) & {'d1', 'd3', 's1', 's3'}
        self.code = None
        self.N = None
        self.planned_next_state = None

    def call_user_state_handler(self, state, c, i):
        handler = getattr(self, f'state_{state}', None)
        if callable(handler):
            return handler(c, i)
        return None, None

    def scan(self, code):
        self.code = code
        self.N = N = len(code)
        state = 0
        i = 0
        while i < N:
            c = code[i]
            # First decide if we have an opinion about the next state:
            next_state = None
            if state == 0:
                # Not inside a string
                if c == '"':
                    next_state = 'd'
                    if i < N - 2 and code[i + 1:i + 3] == '""':
                        next_state += '3'
                        i += 2
                    else:
                        next_state += '1'
                elif c == "'":
                    next_state = 's'
                    if i < N - 2 and code[i + 1:i + 3] == "''":
                        next_state += '3'
                        i += 2
                    else:
                        next_state += '1'
                if next_state not in self.accepted_string_types:
                    next_state = None
            elif state == 'd1':
                # Inside a string that started with one double-quote
                if c == '"':
                    if 'd1' in self.ignore_escapes or code[i - 1] != '\\':
                        next_state = 0
            elif state == 'd3':
                # Inside a string that started with three double-quotes
                if c == '"' and i < N - 2 and code[i + 1:i + 3] == '""':
                    if 'd3' in self.ignore_escapes or code[i - 1] != '\\':
                        next_state = 0
                        i += 2
            elif state == 's1':
                # Inside a string that started with one single-quote
                if c == "'":
                    if 's1' in self.ignore_escapes or code[i - 1] != '\\':
                        next_state = 0
            elif state == 's3':
                # Inside a string that started with three single-quotes
                if c == "'" and i < N - 2 and code[i + 1:i + 3] == "''":
                    if 's3' in self.ignore_escapes or code[i - 1] != '\\':
                        next_state = 0
                        i += 2
            self.planned_next_state = next_state
            # Now see if the user has an opinion about the next state, and/or
            # wants to add something to the index.
            user_next_state, di = self.call_user_state_handler(state, c, i)
            if di is not None:
                i += di
            # User's next state rules
            if user_next_state is not None:
                if user_next_state == self.BREAK:
                    break
                state = user_next_state
            elif next_state is not None:
                state = next_state
            i += 1


class PfscModuleStringAwareScanner(StringAwareCodeScanner):
    """
    Subclass of ``StringAwareCodeScanner`` making the settings that are
    appropriate for scanning in a .pfsc module; namely, we expect both single
    and triple quoted strings, but the triple quoted strings ignore escapes.
    """

    def __init__(self):
        super().__init__(['d1', 'd3', 's1', 's3'], ignore_escapes=['d3', 's3'])


class PythonModuleStringAwareScanner(StringAwareCodeScanner):
    """
    Subclass of ``StringAwareCodeScanner`` making the settings that are
    appropriate for scanning in a .py module; namely, we expect both single
    and triple quoted strings, and do not ignore escapes anywhere.
    """

    def __init__(self):
        super().__init__(['d1', 'd3', 's1', 's3'], ignore_escapes=[])
