# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import re
import xrst
pattern_line_number = re.compile( r'\n[ \t]*\{xrst_line [0-9]+@' )
pattern_newline_3   = re.compile( r'(\n[ \t]*){2,}\n' )
# ----------------------------------------------------------------------------
# Write the temporary RST file for a section.
#
# error_line:
# is an int version of the error_line arguemnt to the xrst program
# (with None replaced by zero).
#
# pseudo_heading:
# is the pseudoc heading for this section. This is the section name
# surrounded by headding indicators. `It is placed before
# all the other headings in this section.
# A label is added just before the pseudo heading that
# links to it using the section name.
#
# file_in:
# is the name of the xrst input file for this section.
#
# tmp_dir
# is the directory where the output file will be saved.
#
# section_name
# is the name of this section.  The output file is tmp_dir/section_name.rst.
#
# data_in
# is the data for this section with all the xrst commands coverted to
# their sphinx RST values, except the {xrst_section_number} command.
# The following is added to this deta before writing it to the output file:
# #. The preamble is included at the beginning.
# #. The pseudo heading and its label are added next.
# #. The name of the input file file_in is dispalyed next.
# #. More than 2 lines with only tabs or space are converted to 2 empty lines.
# #. Empty lines at the end are removed
# #. The line numbers are removed.
# #. if error_lne > 0, a mapping from RST line numbers to file_in line numbers
#    is included at the end.
#
def temporary_file(
    error_line,
    pseudo_heading,
    file_in,
    tmp_dir,
    section_name,
    data_in,
) :
    assert type(error_line) == int
    assert type(pseudo_heading) == str
    assert type(file_in) == str
    assert type(section_name) == str
    assert type(data_in) == str
    #
    # label
    # label that displays section name (which is text in pseudo heading)
    label = f'.. _{section_name}:\n\n'
    #
    # before
    # start output by including preamble and then pesudo_heading
    before  = '.. include:: xrst_preamble.rst\n\n'
    before += label
    before += pseudo_heading
    before += f'xrst input file: ``{file_in}``\n\n'
    #
    # data_out
    data_out = before + data_in
    #
    # data_out
    # Convert three or more sequential emtpty lines to two empty lines.
    data_out = pattern_line_number.sub('\n', data_out)
    data_out = pattern_newline_3.sub('\n\n', data_out)
    #
    # data_out
    # remove empty lines at the end
    while data_out[-2 :] == '\n\n' :
        data_out = data_out[: -1]
    #
    # data_out
    # The last step removing line numbers. This is done last for two reasons:
    # 1. So mapping from output to input line number is correct.
    # 2. We are no longer able to give line numbers for errors after this.
    data_out, line_pair = xrst.remove_line_numbers(data_out)
    #
    # after
    # If line number increment is non-zero, include mapping from
    # rst file line number to xrst file line number
    if error_line > 0 :
        after  = '\n.. csv-table:: Line Number Mapping\n'
        after += 4 * ' ' + ':header: rst file, xrst input\n'
        after += 4 * ' ' + ':widths: 10, 10\n\n'
        previous_line = None
        for pair in line_pair :
            if previous_line is None :
                after        += f'    {pair[0]}, {pair[1]}\n'
                previous_line = pair[1]
            elif pair[1] - previous_line >= error_line :
                after         += f'    {pair[0]}, {pair[1]}\n'
                previous_line = pair[1]
        #
        data_out = data_out + after
    #
    # file_out
    if section_name.endswith('.rst') :
        file_out = tmp_dir + '/' + section_name
    else :
        file_out = tmp_dir + '/' + section_name + '.rst'
    file_ptr = open(file_out, 'w')
    file_ptr.write(data_out)
    file_ptr.close()
