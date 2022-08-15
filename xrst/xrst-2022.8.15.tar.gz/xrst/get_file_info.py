# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin begin_cmd user}
{xrst_spell
    underbar
    dir
}

Begin and End Commands
######################

Syntax
******
- ``{xrst_begin_parent`` *section_name* *group_name* :code:`}`
- ``{xrst_begin``        *section_name* *group_name* :code:`}`
- ``{xrst_end``          *section_name* :code:`}`

Section
*******
The start (end) of a section of the input file is indicated by a
begin (end) command.
The line containing the command
can only have spaces and tabs before the command.

section_name
************
The *section_name* is a non-empty sequence of the following characters:
period ``.``, underbar ``_``, the letters a-z, and decimal digits 0-9.
It can not begin with the characters ``xrst_``.
A link is included in the index under the section name
to the first heading the section.
The section name is also added to the html keyword meta data.

group_name
**********
This is the group that this section belongs to; see
:ref:`run_xrst@group_list`.
If *group_name* is empty, this section is part of the empty group.
Note that it is the group name and not the group that is empty.

Output File
***********
The output file corresponding to *section_name* is

| |tab| *sphinx_dir*\ ``/xrst/``\ *section_name*\ ``.rst``

see :ref:`sphinx_dir<run_xrst@sphinx_dir>`

Parent Section
**************
The following conditions hold for each *group_name*:

#.  There can be at most one begin parent command in an input file.
#.  If there is a begin parent command, it must be the first begin command
    in the file and there must be other sections in the file.
#.  The other sections are children of the parent section.
#.  The parent section is a child
    of the section that included this file using a
    :ref:`child command<child_cmd>`.
#.  If there is no begin parent command in an input file,
    all the sections in the file are children
    of the section that included this file using a
    :ref:`child command<child_cmd>`.

Note that there can be more than one begin parent command in a file if
they have different group names. Also note that sections are only children
of sections that have the same group name.

{xrst_end begin_cmd}
"""
# ---------------------------------------------------------------------------
import xrst
import re
pattern_group_name  = re.compile( r'[^ \t]+' )
pattern_group_valid = re.compile( r'[a-z]+' )
# ---------------------------------------------------------------------------
#
# Get all the information for a file.
#
# section_info:
# a list of the information for sections that came before this file.
# We use infor below for one eleemnt of this list:
#
#   info['section_name']
#   is an str containing the name of a seciton that came before this file.
#
# group_name:
# We are only retrieving information for sections in this group.
#
# parent_file:
# name of the file that included file_in.
#
# file_in:
# is the name of the file we are getting all the information for.
#
# file_info:
# The value file_info is a list is a dictionary contianing the information
# for one section in this file. We use info below for one element of this list:
#
#   info['section_name']:
#   is an str containing the name of a seciton in this file.
#
#   info['section_data']:
#   is an str containing the data for this seciton.
#   1. Line numbers have been added using add_line_numbers.
#   2. If present in this file, the comment character and possilbe space
#      after have been removed.
#   3. The begin and end commands are not include in this data.
#   4. The suspend / resume comands and data between such pairs
#      have been removed.
#   5. If there is a common indentation for the entire section,
#      it is removed.
#
#   info['is_parent']:
#   is true (false) if this is (is not) the parent section for the other
#   sections in this file. The parent section must be the first, and hence
#   have index zero in file_info. In addition, if there is a parent section,
#   there must be at least one other section; i.e., len(file_info) >= 2.
#
#   info['is_child']:
#   is true (false) if this is (is not) a child of the first section in
#   this file.
#
# file_info =
def get_file_info(
        section_info,
        group_name,
        parent_file,
        file_in,
) :
    assert type(section_info) == list
    assert type(group_name) == str
    assert type(file_in) == str
    #
    # file_data
    file_ptr   = open(file_in, 'r')
    file_data  = file_ptr.read()
    file_ptr.close()
    #
    # file_data
    file_data = xrst.add_line_numbers(file_data)
    file_data = xrst.remove_comment_ch(file_data, file_in)
    #
    # file_info
    file_info = list()
    #
    # parent_section_name
    parent_section_name = None
    #
    # data_index
    # index to start search for next pattern in file_data
    data_index  = 0
    #
    # found_group_name
    found_group_name = False
    #
    # for each section in this file
    while data_index < len(file_data) :
        #
        # m_begin
        data_rest   = file_data[data_index : ]
        m_begin = xrst.pattern['begin'].search(data_rest)
        #
        # this_group_name
        if m_begin != None :
            #
            this_group_name = m_begin.group(4)
            m_group         = pattern_group_name.search(this_group_name)
            if m_group == None :
                this_group_name = ''
            else :
                this_group_name = m_group.group(0)
                m_group    = pattern_group_valid.search(this_group_name)
                if this_group_name != m_group.group(0) :
                    msg = f'"{this_group_name}" is not a valid group name'
                    xrst.system_exit(msg,
                        file_name = file_in,
                        m_obj     = m_begin,
                        data      = data_rest,
                    )
        if m_begin == None :
            if not found_group_name :
                msg  = 'can not find a begin command at start of a line\n'
                msg += f'with group_name = {group_name}\n'
                msg += f'parent file = {parent_file}'
                xrst.system_exit(msg, file_name=file_in)
            #
            # data_index
            # set so that the section loop for this file terminates
            data_index = len(file_data)
        elif this_group_name != group_name :
            #
            # data_index
            # place to start search for next section
            data_index += m_begin.end()
        else :
            #
            # found_group_name
            found_group_name = True
            #
            # section_name, is_parent
            section_name = m_begin.group(3)
            is_parent    = m_begin.group(2) == 'begin_parent'
            #
            # check_section_name
            xrst.check_section_name(
                section_name,
                file_name     = file_in,
                m_obj         = m_begin,
                data          = data_rest
            )
            #
            # check if section_name appears multiple times in this file
            for info in file_info :
                if section_name == info['section_name'] :
                    msg  = 'xrst_begin: section appears multiple times'
                    xrst.system_exit(msg,
                        file_name      = file_in,
                        section_name   = section_name,
                        m_obj          = m_begin,
                        data           = data_rest
                    )
            #
            # check if section_name appears in another file
            for info in section_info :
                if section_name == info['section_name'] :
                    msg  = f'section_name = "{section_name}", '
                    msg += f'group_name = {group_name} appears twice\n'
                    msg += 'Once  in file ' + file_in + '\n'
                    msg += 'Again in file ' + info['file_in'] + '\n'
                    xrst.system_exit(msg)
            #
            # check if parent sections is the first seciton in this file
            if is_parent :
                if len(file_info) != 0 :
                    msg  = 'xrst_begin_parent'
                    msg += ' is not the first begin command in this file'
                    xrst.system_exit(msg,
                        file_name     = file_in,
                        section_name  = section_name,
                        m_obj         = m_begin,
                        data          = data_rest
                    )
                #
                # parent_section_name
                parent_section_name = section_name
            #
            # is_child
            is_child = (not is_parent) and (parent_section_name != None)
            #
            # data_index
            data_index += m_begin.end()
            #
            # m_end
            data_rest = file_data[data_index : ]
            m_end     = xrst.pattern['end'].search(data_rest)
            #
            if m_end == None :
                msg  = 'Expected the followig text at start of a line:\n'
                msg += '    {xrst_end section_name}'
                xrst.system_exit(
                    msg, file_name=file_in, section_name=section_name
                )
            if m_end.group(1) != section_name :
                msg = 'begin and end section names do not match\n'
                msg += 'begin name = ' + section_name + '\n'
                msg += 'end name   = ' + m_end.group(1)
                xrst.system_exit(msg,
                    file_name = file_in,
                    m_obj     = m_end,
                    data      = data_rest
                )
            #
            # section_data
            section_start = data_index
            section_end   = data_index + m_end.start() + 1
            section_data  = file_data[ section_start : section_end ]
            #
            # section_data
            section_data  = xrst.suspend_command(
                section_data, file_in, section_name
            )
            section_data = xrst.remove_indent(
                section_data, file_in, section_name
            )
            #
            # file_info
            file_info.append( {
                'section_name' : section_name,
                'section_data' : section_data,
                'is_parent'    : is_parent,
                'is_child'     : is_child,
            } )
            #
            # data_index
            # place to start search for next section
            data_index += m_end.end()
    #
    if parent_section_name != None and len(file_info) < 2 :
        msg  = 'begin_parent command appears with '
        if group_name == '' :
            msg += 'the empty group name\n'
        else :
            msg += f'group_name = {group_name}\n'
        msg += 'and this file only has one section with that group name.'
        xrst.system_exit(
            msg, file_name=file_in, section_name=parent_section_name
        )

    return file_info
