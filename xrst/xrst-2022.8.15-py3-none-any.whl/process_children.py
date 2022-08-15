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
# pattern_child
pattern_child = re.compile(
    r'\n{xrst_(children|child_list|child_table)}\n'
)
#
# patttern_rst_extension
pattern_rst_extension = re.compile( r'\.rst$' )
# ----------------------------------------------------------------------------
# Add child information to this section
#
# data_in
# is the data for this section after the child_command funcion has processed
# the child commands.
#
# list_children
# is a list of the section names for the children of this section.
# If this list is empty, data_out is equal to data_in.
#
# data_out
# The return value data_out has the child information added.
# This includes a hidden table of contents (toctree) for the children at the
# end of data_out. If the child command in data_in is {xrst_child_list} or
# {xrst_child_table} of table with the corresponding links will replace the
# comand. If the child comamnd is {xrst_children}, the command is removed,
# but no table of links is added.
# If there is no child command and list_children is non-empty,
# the child_table style is used for the links to the children which is placed
# at the end of the data_out (before the toctree).
#
# data_out =
def process_children(
    section_name,
    data_in,
    list_children,
) :
    #
    if len(list_children) == 0 :
        m_child = pattern_child.search(data_in)
        assert m_child is None
        return data_in
    #
    # data_out
    data_out = data_in
    #
    # m_child
    m_child = pattern_child.search(data_out)
    #
    # section_has_child_command
    section_has_child_command =  m_child != None
    if section_has_child_command :
        #
        # type of child command
        child_type = m_child.group(1)
        #
        # There chould be at most one child command per section created by
        # the xrst.child_command routine
        m_tmp = pattern_child.search(data_in, m_child.end())
        assert m_tmp == None
        #
        # cmd
        if child_type ==  'child_list' :
            cmd = '\n\n'
            for child in list_children :
                cmd += '-  :ref:`@' + child + '`\n'
            cmd += '\n\n'
        elif child_type == 'child_table' :
            cmd  = '\n\n'
            cmd += '.. csv-table::\n'
            cmd += '    :header:  "Child", "Title"\n'
            cmd += '    :widths: 20, 80\n\n'
            for child in list_children :
                cmd += '    "' + child + '"'
                cmd += ', :ref:`@' + child + '`\n'
        else :
            assert child_type == 'children'
            cmd = ''
        #
        # data_out
        data_tmp = data_out[: m_child.start()]
        data_tmp += cmd
        data_tmp += data_out[m_child.end() :]
        data_out  = data_tmp
    #
    # -----------------------------------------------------------------------
    if data_out[-1] != '\n' :
        data_out += '\n'
    #
    # data_out
    # If there is no child command in this section, automatically generate
    # links to the child sections at the end of the section.
    if not section_has_child_command :
        data_out += '.. csv-table::\n'
        data_out += '    :header: "Child", "Title"\n'
        data_out += '    :widths: 20, 80\n\n'
        for child in list_children :
            data_out += '    "' + child + '"'
            data_out += ', :ref:`@' + child + '`\n'
        data_out += '\n'
    #
    # data_out
    # put hidden toctree at end of section
    toctree  = '.. toctree::\n'
    toctree += '   :maxdepth: 1\n'
    toctree += '   :hidden:\n\n'
    for child in list_children :
        entry    = pattern_rst_extension.sub('', child)
        toctree += '   ' + entry + '\n'
    data_out = data_out + toctree
    #
    return data_out
