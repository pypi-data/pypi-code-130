"""
Check a student-defined variable has expected value, and provide feedback
"""


def _exists(varname):
    """Check that main.varname exists (varname is string)"""
#    mod = importlib.import_module('main')
#    varstring = f"mod.{varname}"  # get variable from main code
    try:
        getattr(__import__('main', fromlist=[varname]), varname)
#        eval(varstring)
        return True
    except AttributeError:
        return False


def _get_var(varname):
    """import main.varname (varname is string)"""
    imported = getattr(__import__('main', fromlist=[varname]), varname)
    return imported


def _check_size(a, b):
    """check that variable a is the same size (and shape) as b"""
    if hasattr(b, "shape") and hasattr(a, "shape"):  # both ndarrays
        return a.shape == b.shape
    if hasattr(b, "__len__") and hasattr(a, "__len__"):  # both arrays
        return len(a) == len(b)  # size of arrays matches
    elif not (hasattr(b, "__len__") or hasattr(a, "__len__")):  # both scalars
        return True
    else:  # mismatch in type
        return False


def check_value(a, b):
    """check that variable a has the same value as b

    Note that this has been tested for strings, integers, floats, numpy arrays,
    lists, tuples and sympy objects. In the case of sympy objects, the
    expressions are simplified to make sure that they are compared correctly,
    so that x*x == x**2 for instance.
    """
    import numpy as np
    np.set_printoptions(threshold=10)

    if hasattr(b, "check_value") and callable(b.check_value):
        return b.check_value(a)

    # if check_value is invoked without first having called check_size,
    # incommensurate sizes can be missed
    try:
        if not _check_size(a, b):
            return False
    except Exception:
        return False

    try:
        import sympy as sp
        sym_installed = True
    except (ModuleNotFoundError, ImportError):
        sym_installed = False

    if (isinstance(a, str) and isinstance(b, str)) \
            or (isinstance(a, dict) and isinstance(b, dict)):
        return (a == b)
    elif (sym_installed and isinstance(a, sp.Basic) and
          isinstance(b, sp.Basic)):
        try:
            sp.simplify(a)
            sp.simplify(b)
            return (sp.simplify(a) == sp.simplify(b) or
                    (sp.factor(a) == sp.factor(b)))
        except Exception:
            return (a == b)
    else:
        try:  # treat inputs as ndarrays and compare with builtin
            return np.all(np.isclose(a, b))
        # if not ndarrays, treat as list (of strings) and compare elements
        except Exception:
            try:
                for x, y in zip(a, b):
                    if not (x == y):
                        return False
                return True
            except Exception:
                return False


def check_vars(varname, expected, output=True):
    """given information on a variable which the student has been asked to
    define, check whether it has been defined correctly, and provide feedback

    Parameters
    ==========
    varname : str
        name of the variable to be investigated
    expected : any
        expected value of varname
    output : bool
        if True, print output to screen. otherwise execute quietly

    Returns
    =======
    bool: True if function works as expected, False otherwise.
    """
    from AutoFeedback.variable_error_messages import print_error_message
    var = -999
    try:
        assert (_exists(varname)), "existence"
        var = _get_var(varname)
        assert (_check_size(var, expected)), "size"
        assert (check_value(var, expected)), "value"
        if output:
            print_error_message("success", varname, expected, var)
    except AssertionError as error:
        if output:
            print_error_message(error, varname, expected, var)
        return False
    return True


def check_output(expected):
    """Check that information printed to screen matches expected (str)"""
    from AutoFeedback.variable_error_messages import output_check
    return output_check(expected)
