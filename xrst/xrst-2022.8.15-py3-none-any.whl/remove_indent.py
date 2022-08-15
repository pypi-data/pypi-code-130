# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin indent user}

Indentation
###########
If there are a number of spaces (or tabs) before
all of the xrst documentation for a section,
those characters are not included in the xrst output.
This enables one to indent the
xrst so it is grouped with the proper code block in the source.
An error message will result if
you use mix tabs and spaces for the indentation.

Example
*******
:ref:`indent_example`

{xrst_end indent}
"""
import re
import xrst
#
# Remove indentation that is at the front of all lines for a section
#
# data_in:
# is the data for this section. This includes line numbers added by
# add_line_numbers.
#
# file_name:
# is the input that this section appears in (used for error reporting).
#
# section_name:
# is the name of this section (used for error reporting).
#
# data_out:
# is a copy of data_in with the indentation for this seciton removed.
#
# data_out =
def remove_indent(data_in, file_name, section_name) :
    assert type(data_in) == str
    assert type(file_name) == str
    assert type(section_name) == str
    #
    # len_data
    len_data   = len(data_in)
    #
    # newline_list
    newline_list = xrst.newline_indices(data_in)
    #
    # num_remove
    num_remove = len(data_in)
    for newline in newline_list :
        next_ = newline + 1
        if next_ < len_data and 0 < num_remove :
            ch = data_in[next_]
            while ch in ' \t' and next_ + 1 < len_data :
                next_ += 1
                ch     = data_in[next_]
            if ch not in ' \t\n' :
                num_remove = min(num_remove, next_ - newline - 1)
    #
    # check if there is no indent to remove
    if num_remove == 0 :
        return data_in
    #
    # indent_ch
    line      = 0
    indent_ch = data_in[ newline_list[line] + 1 ]
    while indent_ch == '\n' :
        line += 1
        indent_ch = data_in[ newline_list[line] + 1 ]
    #
    # check for mixing spaces and tabs
    check_ch  = indent_ch + '\n'
    for newline in newline_list :
        next_ = newline + 1
        end   = min( len_data, next_ + num_remove )
        while next_ < end :
            if data_in[next_] not in check_ch :
                msg  = 'mixing both spaces and tabs for '
                msg += 'white space that indents this section.'
                xrst.system_exit(
                    msg, file_name=file_name, section_name=section_name
                )
            next_ += 1
    #
    # data_out
    pattern  = re.compile( r'\n' + num_remove * indent_ch )
    data_out = pattern.sub('\n', data_in)
    #
    return data_out
