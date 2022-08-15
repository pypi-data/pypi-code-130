# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin child_example_one}

First Child
###########
This section is the first child in this file.
This file does not contain a begin parent command,
so all its sections are children of the section that includes this file.

Link to Second Child
********************
:ref:`child_example_two`

This Example File
*****************
{xrst_file}

{xrst_end child_example_one}
"""
# ----------------------------------------------------------------------------
"""
{xrst_begin child_example_two}

Section Child
#############
This section is the second child in this file.

Link to First Child
*******************
:ref:`child_example_one`

{xrst_end child_example_two}
"""
