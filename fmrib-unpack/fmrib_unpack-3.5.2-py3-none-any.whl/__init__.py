#!/usr/bin/env python
#
# __init__.py - funpack package
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


__version__ = '3.5.2'
"""The ``funpack`` versioning scheme roughly follows Semantic Versioning
conventions.
"""


from .util      import (findConfigDir,  # noqa
                        findConfigDirs)
from .custom    import (loader,         # noqa
                        sniffer,
                        formatter,
                        exporter,
                        processor,
                        metaproc,
                        cleaner)
from .datatable import (DataTable,      # noqa
                        Column)


def version():
    """Return the FUNPACK version string. If running from an installed
    copy, simply returns :attr:`__version__`. Otherwise, returns the
    result of calling ``git describe --dirty --tags``.
    """
    import               shlex
    import os.path    as op
    import subprocess as sp

    rootdir = op.join(op.dirname(__file__), '..')
    cmd     = shlex.split('git describe --dirty --tags')

    try:
        result  = sp.run(cmd, capture_output=True, check=True, cwd=rootdir)
        return result.stdout.decode().strip()
    except Exception:
        # assume that we're running from an install
        return __version__
