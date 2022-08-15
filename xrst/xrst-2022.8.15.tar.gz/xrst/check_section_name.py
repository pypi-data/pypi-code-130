# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import re
import xrst
#
# Check that a section name abides by its rules. If not, report error and exit.
#
# section_name:
# The string section_name appears at the begnning of a line, not counting
# white space, in one of the following cases:
# 1. {xrst_begin_parent section_name user}
# 2. {xrst_begin section_name user}
# 3. {xrst_end section_name}
# The valid characters in a seciton name are [a-z], [0-9], and underbar.
# A section name cannot begin with xrst_. If seciton_name does not follow the
# rules in the previous sentence, a message is printed and the program exits.
#
# file_name:
# is the name of the original input file that data appears in.
#
# m_obj:
# is the match object correpsonding to finding the section name
#
# data:
# is that data that was searched to detect the match object.
#
def check_section_name(section_name, file_name, m_obj, data) :
    assert type(section_name) == str
    assert type(file_name) == str
    assert m_obj
    assert type(data) == str
    #
    m_obj = re.search('[._a-z0-9]+', section_name)
    if m_obj.group(0) != section_name :
        msg  = f'in begin comamnd section_name = "{section_name}"'
        msg += '\nIt must be non-empty and only contain the following'
        msg += ' characters: ., _, a-z, 0-9'
        xrst.system_exit(msg,
            file_name=file_name, m_obj=m_obj, data=data
        )
    if section_name.startswith('xrst_') :
        msg = 'section_name cannot start with xrst_'
        xrst.system_exit(msg,
            file_name=file_name, m_obj=m_obj, data=data
        )
