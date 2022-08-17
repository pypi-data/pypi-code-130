"""Jupyter Notebook initialization.

Usage:

1. Add the following to the first code cell of your notebook:

       import mmf_setup; mmf_setup.nbinit()
2. Execute and save the results.
3. Trust the notebook (File->Trust Notebook).

This module provides customization for Jupyter notebooks including
styling and some pre-defined MathJaX macros.
"""
import logging
import os.path
import warnings

try:
    import IPython
    from IPython.display import HTML, Javascript, display, clear_output
except (ImportError, KeyError):
    IPython = None
    HTML = Javascript = display = clear_output = None

__all__ = ["nbinit"]

_HERE = os.path.abspath(os.path.dirname(__file__))
_DATA = os.path.join(_HERE, "_data")
_NBTHEMES = os.path.join(_DATA, "nbthemes")

_MESSAGE = r"""
<i>
<p>This cell contains some definitions
for equations and some CSS for styling the notebook.
If things look a bit strange, please try the following:
<ul>
  <li>Choose "Trust Notebook" from the "File" menu.</li>
  <li>Re-execute this cell.</li>
  <li>Reload the notebook.</li>
</ul>
</p>
</i>
"""

_TOGGLE_CODE = r"""<script>
code_show=true;
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
}
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit"
    value="Click here to toggle on/off the raw code."></form>
"""


def log(msg, level=logging.INFO):
    logging.getLogger(__name__).log(level=level, msg=msg)


class MyFormatter(logging.Formatter):
    """Custom logging formatter for sending info to Jupyter console."""

    def __init__(self):
        logging.Formatter.__init__(
            self,
            fmt="[%(levelname)s %(asctime)s %(name)s] %(message)s",
            datefmt="%H:%M:%S",
        )

    def format(self, record):
        record.levelname = record.levelname[0]
        msg = logging.Formatter.format(self, record)
        if record.levelno >= logging.WARNING:
            msg += "\n{}{}:{}".format(" " * 14, record.filename, record.lineno)
        return msg


def nbinit(
    theme="default",
    set_path=True,
    toggle_code=False,
    debug=False,
    console_logging=True,
    quiet=False,
):
    """Initialize a notebook.

    This function displays a set of CSS and javascript code to customize the
    notebook, for example, defining some MathJaX latex commands.  Saving the
    notebook with this output should allow the notebook to render correctly on
    nbviewer.org etc.

    Arguments
    ---------
    theme : str
       Choose a theme.
    set_path : bool
       If `True`, then call `mmf_setup.set_path()` to add the root directory to
       the path so that top-level packages can be imported without installation.
    toggle_code : bool
       If `True`, then provide a function to toggle the visibility of input
       code.  (This should be replaced by an extension.)
    debug : bool
       If `True`, then return the list of CSS etc. code displayed to the
       notebook.
    console_logging : bool
       If `True`, then add an error handler that logs messages to the console.
    quiet : bool
       If `True`, then do not display message about reloading and trusting notebook.
    """
    ####################
    # Logging to jupyter console.
    # Not exactly sure why this works, but here we add a handler
    # to send output to the main console.
    # https://stackoverflow.com/a/39331977/1088938
    if console_logging:
        logger = logging.getLogger()
        handler = None
        for h in logger.handlers:
            try:
                if h.stream.fileno() == 1:
                    handler = h
                    break
            except Exception:
                pass

        if not handler:
            handler = logging.StreamHandler(open(1, "w", encoding="utf-8"))
            logger.addHandler(handler)

        handler.setFormatter(MyFormatter())
        handler.setLevel("DEBUG")
        logger.setLevel("DEBUG")

        # Suppress messages from matplotlib though.
        logging.getLogger("matplotlib").setLevel(logging.WARNING)

    ####################
    # Accumulate output for notebook to setup MathJaX etc.
    if not IPython:
        warnings.warn("IPython could not be imported... no config will be displayed.")
    else:
        clear_output()

    res = []

    def _display(val, wrapper=HTML):
        res.append((val, wrapper))
        if display:
            display(wrapper(val))

    def _load(ext, theme=theme):
        """Try loading resource from theme, fallback to default"""
        for _theme in [theme, "default"]:
            _file = os.path.join(
                _NBTHEMES, "{theme}{ext}".format(theme=_theme, ext=ext)
            )
            if os.path.exists(_file):
                with open(_file) as _f:
                    return _f.read()
        return ""

    # CSS
    _display(r"<style>{}</style>".format(_load(".css")))

    # Javascript
    _display(_load(".js"), wrapper=Javascript)

    # LaTeX commands
    _template = r'<script id="MathJax-Element-48" type="math/tex">{}</script>'
    _display(_template.format(_load(".tex").strip()))

    # Remaining HTML
    _display(_load(".html"))

    message = _MESSAGE

    if set_path:
        from .set_path import set_path

        path = set_path()
        if path:

            message = message.replace(
                "This cell", f"This cell adds {path} to your path, and"
            )

    # Message
    if not quiet:
        _display(message)

    if toggle_code:
        _display(_TOGGLE_CODE)

    if debug:
        return res
