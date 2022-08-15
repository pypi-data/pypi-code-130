# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin code_example}

Code Command Example
####################

Factorial
*********
{xrst_code py}"""
def factorial(n) :
    if n == 1 :
        return 1
    return n * factorial(n-1)
"""{xrst_code}

xrst_code
*********
The file below demonstrates the use of ``xrst_code`` .

This Example File
*****************
{xrst_file}

{xrst_end code_example}
"""
