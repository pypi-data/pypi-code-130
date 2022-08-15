# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import re
#
# pattern
# This dictionary contains compiled regular expressions.
# It does not change after its initial setting when this file is imported.
pattern = dict()
#
# pattern['begin']
# Pattern for the begin command.
# group(0): preceeding newline + spaces and tabs + the command.
# group(2): begin or begin_parent
# group(3): the section name (without leading or trailing spaces or tabs)
# group(4): the group name (with leading and trailing spaces and tabs)
pattern['begin'] = re.compile(
    r'(^|\n)[ \t]*\{xrst_(begin|begin_parent)[ \t]+([^ \t}]*)([^}]*)\}'
)
#
# pattern['child']
# Patterns for the children, child_list, and child_table commands.
# group(0): preceeding newline + white space + the command.
# group(1): command name; i.e., children, child_list, or child_table
# group(2): the rest of the command that comes after the command name.
#           This is a list of file names with one name per line.
#           The } at the end of the command is not included.
#           This pattern may be empty.
pattern['child']   = re.compile(
    r'\n[ \t]*\{xrst_(children|child_list|child_table)([^}]*)\}'
)
#
# pattern['code']
# Pattern for code command.
# group(0): the entire line for the command (newline at front).
# group(1): the characters before the language argument including white space
# group(2): the language argument which is emtpy (just white space)
#           for the second code command in each pair.
# group(3): the line number for this line; see pattern['line'] above.
pattern['code'] = re.compile(
    r'(\n[^\n`]*\{xrst_code *)([^}]*)\}[^\n`]*(\{xrst_line [0-9]+@)'
)
#
# pattern['end']
# Pattern for end command
# group(0): preceeding newline + white space + the command.
# group(1): the section name.
pattern['end'] = re.compile( r'\n[ \t]*\{xrst_end\s+([^}]*)\}' )
#
# pattern['file_0']
# xrst_file with no arguments
# group(0): preceeding newline + white space + the command.
# group(1): line number where } at end of command appears
#
# pattern['file_1']
# xrst_file wth display_file
# group(0): preceeding newline + white space + the command.
# group(1): the line number where this command starts
# group(2): the display file
# group(3): line number where display file appears
# group(4): line number where } at end of command appears
#
# pattern['file_2']
# xrst_file with start, stop
# group(0): preceeding newline + white space + the command.
# group(1): the line number where this command starts
# group(2): the start text + surrounding white space
# group(3): line number where start text appears
# group(4): the stop text + surrounding white space
# group(5): the line number where stop text appears
# group(6): line number where } at end of command appears
#
# pattern['file_3']
# xrst_file with start, stop, display_file
# group(0): preceeding newline + white space + the command.
# group(1): the line number where this command starts
# group(2): the start text + surrounding white space
# group(3): line number where start text appears
# group(4): the stop text + surrounding white space
# group(5): the line number where stop text appears
# group(6): the display file
# group(7): line number where display file appears
# group(8): line number where } at end of command appears
#
arg = r'([^{]*)\{xrst_line ([0-9]+)@\n'
lin = r'[ \t]*\{xrst_line ([0-9]+)@\n'
pattern['file_0'] = re.compile(
    r'\n[ \t]*\{xrst_file\}' + lin
)
pattern['file_1']  = re.compile(
    r'\n[ \t]*\{xrst_file' + lin + arg + r'[ \t]*\}' + lin
)
pattern['file_2']  = re.compile(
    r'\n[ \t]*\{xrst_file' + lin + arg + arg + r'[ \t]*\}' + lin
)
pattern['file_3']  = re.compile(
    r'\n[ \t]*\{xrst_file' + lin + arg + arg + arg + r'[ \t]*\}' + lin
)
#
#
# pattern['line']
# Pattern for line numbers are added to the input by add_line_number
# group(0): the line command.
# group(1): the line_number.
pattern['line'] = re.compile( r'\{xrst_line ([0-9]+)@' )
