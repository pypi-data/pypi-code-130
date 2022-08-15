# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
# Replace {xrst_section_number} by it section number or empty string.
#
# data_in:
# data before replacement. This must contain \n{xrst_section_number}
# which is referred to as the command below. There must be a
# section title after the command (starting with a newline).
# This section title may have an rst overline directly before the heading text
# and must have an underline directly after it.
# If both an overline and underline follow, they must be equal.
#
# section_number:
# This is a section number that is placed infront of the heading text.
# This may be empty; i.e., the replacement text is the empty string.
# The underline (and overline if present) are exended to by the number of
# characters added to the heading text.
#
# data_out:
# the return data_out is the data after replacement. The section number is
# added (see above) and he command is removed.
#
# data_out =
def replace_section_number(data_in, section_number) :
    assert type(data_in) == str
    assert type(section_number) == str
    #
    # pattern
    pattern   = '\n{xrst_section_number}'
    if section_number == '' :
        # data_out
        return data_in.replace(pattern,'')
    #
    # punctuation
    # Headings uses repeated copies of one of these characters
    punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    #
    # start_cmd
    start_cmd = data_in.find(pattern)
    assert 0 <= start_cmd
    #
    # first_newline
    first_newline = start_cmd + len(pattern)
    assert data_in[first_newline] == '\n'
    #
    # second_newline
    second_newline = data_in.index('\n', first_newline + 1)
    #
    # third_newline
    third_newline  = data_in.index('\n', second_newline + 1)
    #
    # first_line, second_line
    first_line   = data_in[first_newline + 1 : second_newline ]
    second_line  = data_in[second_newline + 1 : third_newline ]
    #
    # overline
    # check for an overline directly after the command
    overline = False
    if first_line[0] * len(first_line) == first_line :
        if first_line[0] in punctuation :
            overline = True
    #
    if not overline :
        # If no overline the section title follows the command and then
        # an underline after the title.
        assert second_line[0] in punctuation
        #
        # new version of first and second lines
        if section_number != '' :
            first_line   = section_number + ' ' + first_line
            second_line += second_line[0] * ( len(section_number) + 1 )
        #
    else :
        # fourth_newline
        fourth_newline = data_in.index('\n', third_newline + 1)
        #
        # third_line
        third_line   = data_in[third_newline + 1 : fourth_newline]
        assert first_line == third_line
        #
        # new version of first, second, and third lines
        if section_number != '' :
            first_line += first_line[0] * ( len(section_number) + 1 )
            second_line = section_number + ' ' + second_line
            third_line  = first_line
    #
    # data_out
    data_out  = data_in[: start_cmd] + '\n'
    data_out += first_line + '\n'
    data_out += second_line + '\n'
    if overline :
        data_out += third_line + '\n'
        data_out += data_in[fourth_newline :]
    else :
        data_out += data_in[third_newline :]
    #
    return data_out
