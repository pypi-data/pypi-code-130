# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import xrst
#
# data:
# is the data that we are searching for a heading in. The heading text must
# have at least two character and be followed by an underline of at least the
# same length. The heading text may be proceeded by an overline.
#
# data_index:
# is the index in the data where the search starts. This must be zero
# or directly after a newline.
#
# heading_index:
# If there is an overline, this is the index in data of the beginning of the
# overline. Otherwise, it is the index of the beginning of the heading text.
# If 0 < heading_index, there is a newline just before heading_index; i.e.,
# data[heading_index]=='\n'.  If heading_index is -1, there is no heading
# in data that begins at or after data_index.
#
# heading_text:
# if 0 <= heading_index, this is the heading text.
#
# underline_text:
# if 0 <= heading_index, this is the underline text.
# If there is an overline present, it is the same as the underline text.
#
# heading_index, heading_text, underline_text =
def next_heading(data, data_index) :
    assert type(data) == str
    assert type(data_index) == int
    if data_index != 0 :
        assert data[data_index-1] == '\n'
    #
    # punctuation
    punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    assert len(punctuation) == 34 - 2 # two escape sequences
    #
    # next_start, next_newline
    next_start       = data_index
    next_newline     = data.find('\n', next_start)
    #
    # state
    state  = 'before_overline'
    #
    while 0 <= next_newline :
        #
        # next_line
        next_line = data[next_start : next_newline]
        next_line = xrst.pattern['line'].sub('', next_line)
        next_line = next_line.rstrip(' \t')
        #
        # next_len
        next_len  = len(next_line)
        #
        if next_len < 2 :
            # next_line cannot be an overline, heading, or underline
            state = 'before_overline'
        #
        elif state == 'before_overline' :
            #
            # heading_index
            heading_index = next_start
            #
            ch = next_line[0]
            if ch in punctuation and next_line == ch * next_len :
                # next_line can be an overline but not an underline
                state         = 'before_heading'
                overline_text = next_line
            else :
                # next_line can be a heading, but not overline or underline
                state         = 'before_underline'
                overline_text = None
                heading_text  = next_line
        #
        elif state == 'before_heading' :
            # next_line can be a heading
            state = 'before_underline'
            heading_text    = next_line
        #
        elif state == 'before_underline' :
            underline_ch = next_line[0]
            if len(next_line) < len(heading_text) :
                state = 'before_overline'
            elif overline_text is not None and overline_text != next_line:
                state = 'before_overline'
            elif underline_ch not in punctuation :
                state = 'before_overline'
            elif next_line != underline_ch * next_len :
                state = 'before_overline'
            else :
                underline_text = next_line
                return heading_index, heading_text, underline_text
        #
        # next_start, next_newline
        next_start   = next_newline + 1
        next_newline = data.find('\n', next_start)
    #
    # heading_index, heading_text, underline_text
    heading_index = -1
    heading_text  = ''
    underline_text  = ''
    return heading_index, heading_text, underline_text
