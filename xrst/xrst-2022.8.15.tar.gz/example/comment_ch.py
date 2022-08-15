# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
# {xrst_comment_ch #}
#
# {xrst_begin comment_ch_example}
# {xrst_spell
#   ch
# }
#
# Comment Character Command Example
# #################################
#
# Discussion
# **********
# The ``#`` at the beginning of a line,
# and space directly after it, are removed.
# The remaining text lines up with the first line in the
# function definition below:
#
# {xrst_code py}
def factorial(n) :
    if n == 1 :
        return 1
    return n * factorial(n-1)
# {xrst_code}
#
# xrst_comment_ch
# ***************
# The file below demonstrates the use of ``xrst_comment_ch`` .
#
# This Example File
# *****************
# {xrst_file}
#
# {xrst_end comment_ch_example}
