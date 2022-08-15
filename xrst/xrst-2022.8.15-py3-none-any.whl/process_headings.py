# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin heading_links user}
{xrst_spell
    underbars
}

Heading Cross Reference Links
#############################

Index
*****
For each word in a heading,
a link is included in the index from the word to the heading.
In addition, each word is added to the html keyword meta data
next to the section heading.

Labels
******
A cross reference label is defined for linking
from anywhere to a heading. The details of how to use
these labels are described below.

First Level
===========
Each :ref:`section<begin_cmd@section>` can have only one header at
the first level which is a title for the section.
The :ref:`section_name<begin_cmd@section_name>`
is automatically used as a label for a link that displays the
section name or section title. To be specific,
the first input below will display the section name as the linking text,
the second will display the section title as the linking text.

1.  ``:ref:``\ \` *section_name*\ \`
2.  ``:ref:``\ \` ``@``\ *section_name*\ \`

You can also explicitly choose the linking text; e.g.

3.  ``:ref:``\ \`*linking_text*\ ``<``\ *section_name*\ ``>``\ \`


Other Levels
============
The label for linking a heading that is not at the first level is the label
for the heading directly above it plus an at sign character :code:`@`,
plus the conversion for this heading.
These labels do not begin with ``@``.

Conversion
==========
The conversion of a heading to a label does the following:

1.  Letters are converted to lower case.
2.  The following characters are converted to underbars ``_`` :
    space ,  at signs ``@``, and colon ``:`` .

For example, the label for the heading above is

|tab| ``heading_links@labels@conversion``


Discussion
==========
1.  Note that at the first level one uses the *section_name*
    ( ``run_xrst`` in example above)
    and not the title ( ``extract_sphinx_rst`` in example above ).
2.  The ``@`` and not ``.`` character is used to separate levels
    because the ``.`` character is often used in titles and
    section names; e.g. :ref:`auto_file@conf.py`.
3.  Specifying all the levels for a heading may seem verbose,
    but it avoids ambiguity when the same heading appears twice in one section;
    e.g the heading Example might appears multiple times in different context.
4.  Specifying all the levels also helps keep the links up to date.
    If a heading changes, all the links to that heading, and all the
    headings below it,  will break.  This identifies the links that should be
    checked to make sure they are still valid.

Example
*******
:ref:`heading_example`

{xrst_end heading_links}
"""
import xrst
#
# Add labels and indices for headings
#
# data_in:
# contains the data for a section before the headings are processed.
#
# file_name:
# name of the file that contains the input data for this section.
# This is only used for error reporting.
#
# keyword_list:
# is a list of compiled reglar expressions. If pattern is an entry in this list,
# and word is a lower case verison of a word in the heading text, if
# pattern.fullmatch(word) returns a match, a cross-reference index will not
# be generated for word.
#
# section_name:
# is the name of this section.
#
# data_out:
# is a copy of data_in with the following extra command added directly before
# its corresponding heading: The command {xrst_section_number}\n
# is placed directly before the the first heading for this section.
# This is makes it easy to add the section number to the heading text.
#
# section_title:
# This is the heading text in the first heading for this section.
# There can only be one heading at this level.
#
# pseudo_heading:
# This is an automatically generated heading for this section. It is intended
# to come before the section_title heading.
# It has three lines each termnated by a newline;
# 1) an overline line, 2) a heading text line containig the section,
# 3) and an underline line.
#
#
# data_out, section_title, pseudo_heading =
def process_headings(
        data_in, file_name, section_name, keyword_list
) :
    assert type(data_in) == str
    assert type(file_name) == str
    assert type(section_name) == str
    assert type(keyword_list) == list
    #
    # data_out
    data_out = data_in
    #
    # punctuation
    punctuation      = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    assert len(punctuation) == 34 - 2 # two escape sequences
    #
    # overline_used
    overline_used = set()
    #
    # heading_list, heading_index, heading_text, underline_text
    heading_list     = list()
    data_index       = 0
    heading_index, heading_text, underline_text = \
        xrst.next_heading(data_out, data_index)
    #
    while 0 <= heading_index :
        if 0 < heading_index :
            assert data_out[heading_index-1] == '\n'
        # overline
        m_obj = xrst.pattern['line'].search(data_out, heading_index)
        index = m_obj.start()
        overline = underline_text == data_out[heading_index : index]
        #
        # character
        character = underline_text[0]
        #
        # heading
        heading   = {
            'overline' : overline,
            'character': character,
            'text':      heading_text
        }
        #
        # underline_end
        underline_end = data_out.find('\n', heading_index)
        underline_end = data_out.find('\n', underline_end+1)
        if overline :
            underline_end = data_out.find('\n', underline_end+1)
        assert data_out[underline_end] == '\n'
        #
        # overline_used
        if overline :
            overline_used.add(character)
        #
        # heading_list
        if len( heading_list ) == 0 :
            # first heading in this section
            heading_list.append( heading )
        else :
            # level_zero
            level_zero = overline == heading_list[0]['overline']
            if level_zero :
                level_zero = character == heading_list[0]['character']
            if level_zero :
                m_obj = \
                    xrst.pattern['line'].search(data_out, heading_index)
                msg = 'There are multiple titles for this section'
                xrst.system_exit(
                    msg,
                    file_name=file_name,
                    section_name=section_name,
                    m_obj=m_obj,
                    data=data_out
                )
            #
            # found_level
            found_level = False
            level       = 1
            while level < len(heading_list) and not found_level :
                found_level = overline == heading_list[level]['overline']
                if found_level :
                    found_level = character == heading_list[level]['character']
                if found_level :
                    #
                    # heading_list
                    heading_list = heading_list[: level ]
                    heading_list.append(heading)
                else :
                    level += 1
            #
            # heading_list
            if not found_level :
                # this heading at a deeper level
                heading_list.append( heading )

        #
        # label
        label = ''
        for level in range( len(heading_list) ) :
            if level == 0 :
                label = section_name.lower()
                label = label.replace(' ', '_')
                label = label.replace('@', '_')
                label = label.replace(':', '_')
                assert label == section_name
                # label for link that displays the title
                if len(heading_list) == 1 :
                    label = '@' + section_name
                else :
                    label = section_name
            else :
                heading     = heading_list[level]
                conversion  = heading['text'].lower()
                conversion  = conversion.replace(' ', '_')
                conversion  = conversion.replace('@', '_')
                conversion  = conversion.replace(':', '_')
                label += '@' + conversion
        #
        # index_entries
        if len(heading_list) == 1 :
            index_entries = section_name
        else :
            index_entries = ''
        for word in heading_list[-1]['text'].lower().split() :
            skip = False
            for pattern in keyword_list :
                m_obj = pattern.fullmatch(word)
                if m_obj :
                    skip = True
            if not skip :
                if index_entries == '' :
                    index_entries = word
                else :
                    index_entries += ', ' + word
        #
        # data_tmp
        # data that comes before this heading
        data_tmp   = data_out[: heading_index]
        #
        # data_tmp
        # add sphnix keyword, index, and label commnds
        cmd  = ''
        if index_entries != '' :
                cmd += '.. meta::\n'
                cmd += 3 * ' ' + ':keywords: ' + index_entries + '\n\n'
                cmd += '.. index:: '           + index_entries + '\n\n'
        cmd += '.. _' + label + ':\n\n'
        data_tmp  += cmd
        #
        # data_tmp
        # If level zero, put section number command just before heading
        if len(heading_list) == 1 :
            data_tmp += '{xrst_section_number}\n'
        #
        # data_tmp
        # add data from stat to end of heading
        data_tmp  += data_out[heading_index : underline_end]
        #
        # data_tmp
        # If level zero, put jump table command just after heading
        if len(heading_list) == 1 :
            data_tmp += '\n.. contents::\n'
            data_tmp += 3 * ' ' + ':local:\n\n'
        #
        # data_out
        data_right = data_out[underline_end : ]
        data_out   = data_tmp + data_right
        #
        # next heading
        data_index = len(data_tmp) + 1
        heading_index, heading_text, underline_text = \
            xrst.next_heading(data_out, data_index)
    #
    if len(heading_list) == 0 :
        msg = 'There are no headings in this section'
        xrst.system_exit(msg, file_name=file_name, section_name=section_name)
    #
    # pseudo_heading
    i = 0
    while punctuation[i] in overline_used :
        i += 1
        if i == len(punctuation) :
            msg  = 'more than ' + len(punctuation) - 1
            msg += ' overlined heading levels'
            xrst.system_exit(
                msg, file_name=file_name, section_name=section_name
            )
    line           = len(section_name) * punctuation[i] + '\n'
    pseudo_heading = line + section_name + '\n' + line + '\n'
    #
    # section_title
    section_title = heading_list[0]['text']
    #
    return data_out, section_title, pseudo_heading
