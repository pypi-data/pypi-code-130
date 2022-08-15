# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin suspend_example}
{xrst_spell
    iterable
}

Suspend Command Example
#######################

Factorial
*********
*f* = ``factorial(`` *positive_integer* ``)``
{xrst_suspend}
"""
def factorial(n) :
    if n == 1 :
        return 1
    return n * factorial(n-1)
"""
{xrst_resume}

Product
*******
*p* = ``product(`` *iterable* ``)``
{xrst_suspend}
"""
def product(itr) :
    p = 1.0
    for v in itr :
        p *= v
    return p
"""
{xrst_resume}

xrst_suspend
************
The file below demonstrates the use of ``xrst_suspend`` .

xrst_resume
***********
The file below demonstrates the use of ``xrst_resume`` .

This Example File
*****************
{xrst_file}

{xrst_end suspend_example}
"""
