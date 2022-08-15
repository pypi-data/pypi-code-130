# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin heading_example}

Title Heading for This Section
##############################
The label for the section title is the ``@``
character followed by the section name; i.e., ``@heading_example``.
The label ``heading_example`` displays ``heading_example``
instead of the section title.

Second Level
************
The label for this heading is ``heading_example.second_level``.

Third Level
===========
The label for this heading is ``heading_example.second_level.third_level``.

Another Second Level
********************
The label for this heading is ``heading_example.another_second_level``.

Third Level
===========
The label for this heading is
``heading_example.another_second_level.third_level``.

Links
*****
These links would also work from any other section because the section name
(``heading_example`` in this case)
is included at the beginning of the target for the link:

1. :ref:`@heading_example`
2. :ref:`heading_example@second_level`
3. :ref:`heading_example@second_level@third_level`
4. :ref:`heading_example@another_second_level`
5. :ref:`heading_example@another_second_level@third_level`

Linking Headings Using :ref:
****************************
The file below demonstrates linking to headings using ``:ref:`` .

This Example File
*****************
{xrst_file}

{xrst_end heading_example}
"""
