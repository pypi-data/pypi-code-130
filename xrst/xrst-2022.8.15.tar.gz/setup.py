# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
# setup
xrst_version = "21.09.07"
package_name  = "xrst"
setup_result = setup(
    name         = 'xrst',
    version      = xrst_version,
    license      = 'GPL3',
    description  = 'Exract Sphinx RST Files',
    author       = 'Bradley M. Bell',
    author_email = 'bradbell@seanet.com',
    url          = 'https://github.com/bradbell/xrst',
    scripts      = [ 'xrst/run_xrst.py' ],
)
