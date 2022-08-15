# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin suspend_cmd user}

Suspend and Resume Commands
###########################

Syntax
******
- ``{xrst_suspend}``
- ``{xrst_resume}``

Purpose
*******
It is possible to suspend (resume) the xrst extraction during a section.
One begins (ends) the suspension with a line that only contains spaces,
tabs and a suspend command (resume command).
Note that this will also suspend all other xrst processing; e.g.,
spell checking.

Example
*******
:ref:`suspend_example`

{xrst_end suspend_cmd}
"""
# ----------------------------------------------------------------------------
import re
import xrst
#
# pattern_suspend, pattern_resume
pattern_suspend = re.compile(
    r'\n[ \t]*\{xrst_suspend\}[ \t]*\{xrst_line [0-9]+@'
)
pattern_resume  = re.compile(
    r'\n[ \t]*\{xrst_resume\}[ \t]*\{xrst_line [0-9]+@'
)
#
# Remove text specified by suspend / resume pairs.
#
# data_in
# is the data for this section.
#
# file_name
# is the input file corresponding to this section.
#
# section_name
# is the name of this section.
#
# data_out
# The return data_out is a copy of data_in except that the text between
# and including each suspend / resume pair has been removed.
#
# data_out =
def suspend_command(data_in, file_name, section_name) :
    assert type(data_in) == str
    assert type(file_name) == str
    assert type(section_name) == str
    #
    # data_out
    data_out = data_in
    #
    # m_suspend
    m_suspend  = pattern_suspend.search(data_out)
    while m_suspend != None :
        #
        # suspend_stat, suspend_end
        suspend_start = m_suspend.start()
        suspend_end   = m_suspend.end()
        #
        # m_resume
        m_resume      = pattern_resume.search(data_out, suspend_end)
        if m_resume == None :
            msg  = 'There is a suspend command without a '
            msg += 'corresponding resume commannd.'
            xrst.system_exit(msg,
                file_name=file_name,
                section_name=section_name,
                m_obj=m_suspend,
                data=data_out
            )
        # resume_start, resume_end
        resume_start = m_resume.start()
        resume_end   = m_resume.end()
        #
        # m_obj
        m_obj = pattern_suspend.search(data_out, suspend_end)
        if m_obj != None :
            if m_obj.start() < resume_end :
                msg  = 'There are two suspend commands without a '
                msg += 'resume command between them.'
                xrst.system_exit(msg,
                    file_name=file_name,
                    section_name=section_name,
                    m_obj=m_obj,
                    data=data_rest
                )
        #
        # data_out
        data_tmp  = data_out[: suspend_start]
        data_tmp += data_out[resume_end : ]
        data_out  = data_tmp
        #
        # m_suspend
        m_suspend = pattern_suspend.search(data_out)
    return data_out
