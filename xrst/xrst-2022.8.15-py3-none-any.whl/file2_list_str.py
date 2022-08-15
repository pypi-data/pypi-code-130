# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
# Convert lines in a file to a list of strings.
#
# file_name:
# is the name of the file that we are converting.
#
# list_str:
# the return value is a list of str, one for each line of the file.
# 1. Lines that begin with the # character are not included.
# 2. Leading and traiiling spaces ' ', tabs '\t', and the newline '\n'
#    are not included.
# 3. Empty lines, after step 2, are not included.
#
# list_str =
def file2_list_str(file_name) :
    file_ptr  = open(file_name, 'r')
    list_str  = list()
    for line in file_ptr :
        if not line.startswith('#') :
            line = line.strip(' \t\n')
            if not line == '' :
                list_str.append(line)
    file_ptr.close()
    return list_str
