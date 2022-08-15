# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
import xrst
# ----------------------------------------------------------------------------
# section_index =
def section_name2index(sinfo_list, section_name) :
    for (section_index, info) in enumerate(sinfo_list) :
        if info['section_name'] == section_name :
            return section_index
    return None

# ----------------------------------------------------------------------------
# Create the table of contents and replace the '{xrst_section_number}'
# for this section and all its child sections.
#
# tmp_dir
# is the temporary directory whre the rst files are written.
#
# target:
# is either 'html' or 'pdf'. If target is 'pdf',  in the file
# tmp_dir/section_name.rst the text {xrst_section_number}
# is replaced by the section number which includes the counter for each level.
# If target is 'html', {xrst_section_number} is removed with not replacement.
#
# count:
# is a list where each element is a non-negative int.
# count[-1] is the number of sections before this section.
# count[-1] is the number of sections before this secions parent.
# ...
# If this list is empty, this section is the root of the table of
# contents tree.
#
# section_index:
# is the index of this section in sinfo_list
#
# sinfo_list:
# is a list with length equal to the number of sections.
# The value section[section_index] is a dictionary for this seciton
# with the following key, value pairs (all the keys are strings:
# key            value
# section_name   a str continaing the name of this section.
# section_title  a str containing the title for this section.
# parent_section an int index in section_info for the parent of this section.
# in_parent_file True if this section in same input file as its parent.
#
# content:
# The return content is the table of contents entries for this section
# and all the sections below this section.
#
# content =
def section_table_of_contents(
    tmp_dir, target, count, sinfo_list, section_index
) :
    assert type(tmp_dir) == str
    assert type(target) == str
    assert type(count) == list
    assert type(sinfo_list) == list
    assert type(section_index) == int
    #
    assert target in [ 'html', 'pdf' ]
    #
    # section_name, section_title
    section_name   = sinfo_list[section_index]['section_name']
    section_title  = sinfo_list[section_index]['section_title']
    #
    # section_number, content
    section_number = ''
    if 0 == len(count) :
        content = ''
    else :
        content = '| '
    if 0 < len(count) :
        assert type( count[-1] ) == int
        for i in range( len(count) - 1 ) :
            content += ' |space| '
        for (i, c) in enumerate(count) :
            section_number += str(c)
            if i + 1 < len(count) :
                section_number += '.'
    #
    # content
    if len(count) == 0 :
        content  += f':ref:`@{section_name}`' '\n\n'
    else :
        content  += f':ref:`{section_number}<{section_name}>` '
        content  += section_title + '\n'
    #
    # file_name
    # temporary file corresponding to this section name
    if section_name.endswith('.rst') :
        file_name = tmp_dir + '/' + section_name
    else :
        file_name = tmp_dir + '/' + section_name + '.rst'
    #
    # file_data
    file_ptr  = open(file_name, 'r')
    file_data = file_ptr.read()
    file_ptr.close()
    if target == 'pdf' :
        file_data = xrst.replace_section_number(file_data, section_number)
    else :
        file_data = xrst.replace_section_number(file_data, '')
    #
    # file_name
    file_ptr  = open(file_name, 'w')
    file_ptr.write(file_data)
    file_ptr.close()
    #
    # in_parent_file_list, in_child_cmd_list
    in_parent_file_list = list()
    in_child_cmd_list   = list()
    for child_index in range( len( sinfo_list ) ) :
        if sinfo_list[child_index]['parent_section'] == section_index :
            if sinfo_list[child_index]['in_parent_file'] :
                in_parent_file_list.append(child_index)
            else :
                in_child_cmd_list.append(child_index)
    #
    #
    # child_count, child_content
    child_count   = count + [0]
    child_content = ''
    #
    # child_count, child_content
    for child_index in in_child_cmd_list + in_parent_file_list :
        #
        # child_count
        child_count[-1] += 1
        child_content += section_table_of_contents(
            tmp_dir, target, child_count, sinfo_list, child_index
        )
    #
    # child_content
    # if the number of children greater than one, put a blank line before
    # and after the child table of contents
    if 1 < child_count[-1] :
        if not child_content.startswith('|\n') :
            child_content = '|\n' + child_content
        if not child_content.endswith('|\n') :
            child_content = child_content + '|\n'
    #
    # content
    content += child_content
    #
    return content
# ----------------------------------------------------------------------------
# Create the table of contents and replace the '{xrst_section_number}'
# for all sections in sinfo_list.
#
# tmp_dir
# is the temporary directory whre the rst files are written.
#
# target:
# is either 'html' or 'pdf'. If target is 'pdf',  in the file
# tmp_dir/section_name.rst the text {xrst_section_number}
# is replaced by the section number which includes the counter for each level.
# If target is 'html', {xrst_section_number} is removed with not replacement.
#
# sinfo_list:
# is a list with length equal to the number of sections.
# The value section[section_index] is a dictionary for this seciton
# with the following key, value pairs (all the keys are strings:
# key            value
# section_name   a str continaing the name of this section.
# section_title  a str containing the title for this section.
# parent_section an int index in sinfo_list for the parent of this section.
# in_parent_file is this section in same input file as its parent.
#
# content:
# The return content is the table of contents entries for all the sections.
# The title Table of Contents and the label xrst_tble_of_contents
# are placed at the beginning of the of content.
#
# content =
def table_of_contents(
    tmp_dir, target, sinfo_list, root_section_list
) :
    assert type(tmp_dir) == str
    assert type(target) == str
    assert type(root_section_list) == list
    assert type(root_section_list[0]) == str
    #
    assert target in [ 'html', 'pdf']
    #
    # content
    content  = '\n.. _@xrst_table_of_contents:\n\n'
    content += 'Table of Contents\n'
    content += '*****************\n'
    #
    # content
    if len(root_section_list) == 1 :
        count = []
        section_name  = root_section_list[0]
        section_index = section_name2index(sinfo_list, section_name)
        content += section_table_of_contents(
            tmp_dir, target, count, sinfo_list, section_index
        )
    else :
        count = [0]
        for section_name in  root_section_list :
            section_index = section_name2index(sinfo_list, section_name)
            count[0]     += 1
            content      += section_table_of_contents(
                tmp_dir, target, count, sinfo_list, section_index
            )
    #
    return content
