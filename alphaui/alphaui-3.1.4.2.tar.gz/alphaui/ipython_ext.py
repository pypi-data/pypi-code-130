try:
    from IPython.core.magic import needs_local_scope, register_cell_magic
except ImportError:
    pass

import alphaui


def load_ipython_extension(ipython):
    __demo = alphaui.Blocks()

    @register_cell_magic
    @needs_local_scope
    def blocks(line, cell, local_ns=None):
        with __demo.clear():
            exec(cell, None, local_ns)
            __demo.launch(quiet=True)
