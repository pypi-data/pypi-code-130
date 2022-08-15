# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import sys
import os
import xrst
#
# Add file name, section name, and line number to a message in a system exit
#
# msg:           error message
# file_name:     original input file that that data appeared in.
# section_name:  section name
# m_obj:         match object indicating where in data the error is detected
# data:          is the input data that was matched when m_obj is not None
# line:          is the error line number when m_obj is None
#
def system_exit(
    msg, file_name=None, section_name=None, m_obj=None, data=None, line=None
) :
    assert type(msg)   == str
    assert type(file_name) == str or file_name== None
    assert type(section_name) == str or section_name== None
    assert type(line)  in [ int, str ] or line == None
    #
    if m_obj :
        assert type(data) == str
    #
    #
    # extra
    root_directory = os.getcwd()
    extra          = f'\nroot_directory = {root_directory}\n'
    #
    if section_name :
        extra += f'section = {section_name}\n'
    if file_name :
        extra += f'file = {file_name}\n'
    if m_obj :
        assert file_name != None
        assert data != None
        assert line == None
        match_line  = xrst.pattern['line'].search( data[m_obj.start() :] )
        assert match_line
        line = match_line.group(1)
    if line != None :
        extra += f'line = {line}\n'
    #
    sys.exit('xrst: Error\n' + msg + extra)
