# BASIC interpreter.
# Executes programs written in a subset of (1975) 8K Altair/Microsoft BASIC,
# plus a few generalisations and extensions. The subset is sufficient to run
# programs from Ahl and North's 'BASIC Computer Games' (1978), and 'More BASIC
# Computer Games' (1979). These include famous examples of early machine
# learning, natural language processing, and topological Wumpus hunting.
# Since the module is intended to run no more than one BASIC program at a time,
# it has been implemented without using classes. While a class could have been
# defined for the BASIC variables (strings, numbers), it seemed like overkill.
# MJL @ Titirangi, 12 August 2022.

###############################################################################
# Imports.                                                                    #
###############################################################################

import re
import sys

from datetime import datetime
from importlib.resources import files, read_text
from math import atan, cos, exp, floor, log, log10, sin, sqrt, tan
from os import access, R_OK
from os.path import isfile, exists
from random import random
from shutil import get_terminal_size
from string import ascii_uppercase
from time import sleep

# Function importlib.resources.files only exists in Python >= 3.9.
# Consider rolling-back to pkgutil or os.path.join.

###############################################################################
# Variables                                                                   #
###############################################################################

# Storage space for BASIC variables, functions, and arrays.
heap_memory = {}

# Storage space for one BASIC program and its run-state.
prog_memory = {}

# Program-memory object names (dictionary keys):
#   'basicProgram'        Raw program listing, as it appears in the file.
#   'basicStatements'     Program listing, deconstructed to statements.
#   'checkedStatements'   Logs which statements have successfully executed.
#   'cursorPosition'      Zero-indexed console column of the print cursor.
#   'dataIndex'           Index number of the next data item to read.
#   'dataLines'           BASIC line numbers upon which data items sit.
#   'dataQueue'           Tuple of all data items in the program.
#   'exitTrigger'         The first error or break condition to have occurred.
#   'fileLineNumbers'     Source-file line number of each program line.
#   'lastRandomNumber'    The last pseudo-random variate generated.
#   'lineIndex'           Index number of the current program line.
#   'lineNumbers'         The BASIC line number of each program line.
#   'loopPoints'          FOR-loop return points and conditions.
#   'printBuffer'         Character strings, ready to be printed.
#   'printedChars'        Characters already printed on the current line.
#   'reservedWords'       BASIC keywords, functions, and logical operators.
#   'returnPoints'        GOSUB return-point stack (for RETURN commands).
#   'statementIndex'      Index of the current statement on the current line.
#   'ttCharDelay'         Teletypewriter delay after printing each character.
#   'ttLineDelay'         Teletypewriter delay after printing each line.
#   'upperCase'           Whether or not to force upper-case printing.

###############################################################################
# Primary function.                                                           #
###############################################################################

def run(program = None, ttx = 0, tty = 0, up = False):
    """
    Loads and runs a BASIC program, with optional teletypewriter aesthetics.

    Args:
      program : The file path of a BASIC program listing,
                  or the name of a bundled program (see below),
                  or None, to re-run the last program.
      ttx     : A pause, in milliseconds, after printing each character.
      tty     : A pause, in milliseconds, after printing each line.
      up      : Whether or not to print exclusively in upper case.

    Returns:
      None. BASIC-program output is printed to standard output.

    Notes:
      - Requires a carriage return capable terminal (IDLE isn't).
      - Terminals that apply their own hard text-wrapping may result in spaces
        between lines of output when printing against the right-hand margin.
      - A negative value for ttx or tty applies no pause delay, but still
        flushes the terminal after each complete line of printed output.
      - In practice, the observed ttx pause will be the set value, plus the
        time taken by the operating system to perform the flush, plus overheads
        of the interpreter. System-level double-buffering may interfere with
        the effect at higher speeds. Depending on the model, a real teletype
        could manage around 10 characters per second.

    Programs:
      The following BASIC programs are bundled with the package:
        'Camel', 'Chase', 'Eliza', 'Flip', 'Inkblot', 'Life',
        'Maze', 'Seabattle', 'Super Star Trek', and 'Wumpus'.
      Their authors are listed when run. Names are case-insensitive.
    """
    if program is not None and len(program) > 0:
        load_program(program)
    set_aesthetics(ttx, tty, up)
    reset_heap_memory()
    go_to_first_datum()
    go_to_first_statement()
    while running() and within_program():
        enact(get_statement())
    print_exit_message()

###############################################################################
# BASIC program storage, state, and flow.                                     #
###############################################################################

###############################################################################
# Clear program memory.

def reset_program_memory():
    """
    Deletes the program and its state, leaving only the reserved words look-up
    table, and the initial random number, on an otherwise clean slate.
    """
    prog_memory.clear()
    set_reserved_words()
    get_new_random_number()

###############################################################################
# Low-level setter and getter for objects in program memory.

def del_pro(a):
    """
    Deletes the object named a from program memory, if it exists there.
    """
    if a in prog_memory:
        del prog_memory[a]

def get_pro(a, b):
    """
    Retrieves the object named a from program memory, returning default value
    b if a is not found there.
    """
    return prog_memory.get(a, b)

def set_pro(a, b):
    """
    Assigns value b to an object named a, stored within program memory.
    """
    prog_memory[a] = b
    return b

###############################################################################
# Load-time program pre-processing and inline data extraction.

def line_has_statement(p):
    """
    Returns the indices of those lines of program listing p that are neither
    blank nor a comment (and hence contain a program statement). Comments are
    lines having # as the first non-blank. (While REM remarks are loaded and
    interpreted, comments are not.)
    """
    return [i for i, s in enumerate(p) if not bool(re.match('[ \t]*(#|$)', s))]

def load_data():
    """
    Scans the stored program for inline DATA statements, and transcribes all
    such data to an immutable tuple in program-memory for run-time convenience.
    """
    # BASI does not detect DATA not at the very beginning of its statement (as
    # is the case for, say, 'IF 1=1 THEN DATA 1,2,3'). Note that 'DATA ,,' and
    # 'DATA' (with nothing after it) are both allowed. This is read as an empty
    # string (which becomes a zero if coerced to number-type).
    s = get_statements()
    n = get_line_numbers()
    m = -1
    d = []
    e = []
    for i in range(len(s)):
        m = max(m, n[i])
        for r in s[i]:
            if begins_with('DATA', r):
                a = scan_data(trim(r, 'DATA'))
                for j in range(len(a)):
                    d.append(a[j])
                    e.append(m)
    set_data_queue(tuple(d))
    set_data_lines(tuple(e))

def load_program(f):
    """
    Loads a BASIC program from file (named) f. This can either be supplied by
    the user as an external file, or else bundled within the Python package.
    """
    reset_line_index()
    p = read_external(f)
    if p is None:
        p = read_bundled(f)
    if p is None:
        return set_file_not_found_error()
    reset_program_memory()
    retain_program_verbatim(p)
    load_statements(p)
    load_data()

def load_statements(p):
    """
    Deconstructs BASIC program listing p to its constituent statements, and
    stores them, along with their BASIC line numbers and source-file line
    numbers, within program-memory space.
    """
    # Source-file line numbers (fl) and the text on each line (lt).
    fl = list(range(1, len(p) + 1))
    lt = [x.strip() for x in p]

    # Remove blank and comment lines, leaving only those containing statements.
    i = line_has_statement(lt)
    fl = [fl[j] for j in i]
    lt = [lt[j] for j in i]

    # Split BASIC line numbers (bl) from the line text (lt).
    bl = [-1 for i in range(len(lt))]
    for i in range(len(lt)):
        m = re.match('\d+', lt[i])
        if m is not None:
            bl[i] = int(substring(lt[i], 0, m.end() - 1))
            lt[i] = substring(lt[i], m.end()).strip()

    # Check BASIC line numbers are unique and monotonically increasing.
    i = [j for j in bl if j >= 0]
    j = set()
    for k in i:
        if k in j:
            return set_redefined_line_error()
        else:
            j.add(k)
    for j in range(len(i) - 1):
        if i[j] > i[j + 1]:
            return set_line_out_of_sequence_error()

    # Locate colons (statement separators), quotes (string delimiters), DATAs
    # (literal data markers), and REMs (remarks; comment markers). BASIC
    # keywords have precedence over everything else, so, unless a REM is a
    # string literal (within quotes or data), everything after it goes unseen.
    # Hence the line '100 LET A=XREMY:DATA 1,2,3' contains no data, while
    # '100 DATAREM,1:DATA2' contains three data items ('REM', 1, and 2).

    # Split each line into its constituent statements.
    ps = []
    for i in range(len(lt)):

        # Locate colons on this line.
        ic = [m.start() for m in re.finditer(':', lt[i])]
        if (len(ic) == 0):
            ps.append([lt[i]])
            continue

        # Locate quotes, REMs and DATAs on this line.
        iq = [m.start() for m in re.finditer('"', lt[i])]
        ir = [m.start() for m in re.finditer('REM', lt[i], re.IGNORECASE)]
        id = [m.start() for m in re.finditer('DATA', lt[i], re.IGNORECASE)]

        # Disregard markers in string literals, by the even/odd quotes rule.
        ic = [j for j in ic if len([1 for k in iq if k < j]) % 2 == 0]
        ir = [j for j in ir if len([1 for k in iq if k < j]) % 2 == 0]
        id = [j for j in id if len([1 for k in iq if k < j]) % 2 == 0]

        # Disregard REMs within DATA statements (treated as string literals).
        if (len(ic) > 0) and (len(ir) > 0) and (len(id) > 0):
            jc = [max([-1] + [y for y in ic if y < x]) for x in ir]
            jd = [max([-2] + [y for y in id if y < x]) for x in ir]
            ir = [j for j, x, y in zip(ir, jc, jd) if x > y]

        # Disregard colons within remarks (those after the first active REM).
        if (len(ic) > 0) and (len(ir) > 0):
            ic = [j for j in ic if j < ir[0]]

        # Split the line into statements.
        if len(ic) > 0:
            j = [0] + [j + 1 for j in ic]
            k = ic + [len(lt[i]) - 1]
            a = [substring(lt[i], x, y) for x, y in zip(j, k)]
            ps.append([re.sub('^:|:$', '', x).strip() for x in a])

        # Unless there was only one.
        else:
            ps.append([lt[i]])

    # Remove whitespace from each line, excepting that on the interior of
    # string literals and data items (quoted or not). Other than these, BASIC
    # pretty much ignores whitespace, and removing it before run-time makes
    # life easier. The necessity of treating DATA statements differently from
    # others, compels us to perform this action after, not before, reducing the
    # program to its constituent statements.
    for i in range(len(ps)):
        for j in range(len(ps[i])):
            k = re.match('D[ \t]*A[ \t]*T[ \t]*A', ps[i][j], re.IGNORECASE)
            if k is None:
                ps[i][j] = space_free_line(ps[i][j])
            else:
                ps[i][j] = space_free_data(ps[i][j], k.end())

    # Load the source-file line numbers (fl), the corresponding BASIC program
    # line numbers (bl), and the associated BASIC program statements (ps), into
    # program memory (the prog_memory dictionary). These are all immutable.
    set_file_line_numbers(tuple(fl))
    set_line_numbers(tuple(bl))
    set_statements(tuple([tuple(x) for x in ps]))

def program_listing():
    """
    Retrieves the BASIC program listing from memory.
    """
    # The original unmodified listing with comments and whitespace.
    # This only happens when the user calls list_program() to take a look.
    return get_pro('basicProgram', ())

def read_bundled(f):
    """
    Reads a packaged (bundled) BASIC program named f.
    """
    g = re.sub('[ \t]+', '_', f).lower() + '.bas'
    if files('brassica.BASIC').joinpath(g).is_file():
        return read_text('brassica.BASIC', g).splitlines()
    return None

def read_external(f):
    """
    Reads a BASIC program from text file f.
    """
    # If f is the name of a readable file, return its content as a tuple.
    # Otherwise, return None.
    if (type(f) is str) and exists(f) and isfile(f) and access(f, R_OK):
        with open(f) as x:
            t = x.read().splitlines()
        return tuple(t)
    return None

def retain_program_verbatim(p):
    """
    Keeps an unmodified copy of the original BASIC program listing.
    """
    # This copy is not used, except when the user calls list_program().
    return set_pro('basicProgram', p)

def set_aesthetics(ttx, tty, up):
    """
    Sets teletypewriter-effect control parameters: the delay after printing
    each character, the delay after printing each line (carriage return), and
    whether or not to convert all output to upper case. Delays are specified in
    milliseconds, case conversion as a Boolean.
    """
    set_teletype_char_delay(ttx)
    set_teletype_line_delay(tty)
    set_upper_case_out(up)

def set_data_lines(i):
    """
    Stores the tuple of inline BASIC-program DATA-statement line numbers, i.
    """
    set_pro('dataLines', tuple(i))

def set_data_queue(d):
    """
    Stores the tuple of inline BASIC-program DATA, d, in program-memory.
    """
    set_pro('dataQueue', tuple(d))

def set_file_line_numbers(n):
    """
    Stores the tuple of source-file line numbers, n, in program memory.
    """
    set_pro('fileLineNumbers', tuple(n))

def set_line_numbers(n):
    """
    Stores the tuple of BASIC line numbers, n, in program memory.
    """
    set_pro('lineNumbers', tuple(n))

def set_statements(s):
    """
    Stores a BASIC program as a tuple of its statements, s.
    """
    # Also marks each statement as unchecked (not yet successfully executed).
    set_pro('basicStatements', tuple(s))
    mark_statements_as_unchecked()

def space_free_data(s, n):
    """
    Removes unnecessary whitespace from character n onwards of BASIC DATA
    statement s.
    """
    # Unnecessary whitespace is all whitespace except that within a string
    # literal or strictly within a datum (whether quoted or not). Integer n
    # marks the next character position after the DATA keyword.
    a = re.sub('[ \t]+', '', substring(s, 0, n - 1))
    b = substring(s, n)
    u = uncontained(',', b, '"')
    i = [0] + [v + 1 for v in u]
    j = [v - 1 for v in u] + [len(b) - 1]
    b = [substring(b, x, y).strip() for x, y in zip(i, j)]
    return a + ','.join(b)

def space_free_line(s):
    """
    Removes unnecessary whitespace from any BASIC statement, s, besides a DATA
    statement.
    """
    # Unnecessary whitespace in this context is everything except that within
    # string literals. For DATA statements, use space_free_data().
    i = [-2, -1] + positions_of('"', s)
    i = i + list(range(len(s) + len(i) % 2, len(s) + 2))
    j = [i[h] + h % 2 for h in range(len(i))]
    k = [i[h] - (h + 1) % 2 for h in range(len(i))]
    s = [substring(s, x, y) for x, y in zip(j[:-1], k[1:])]
    s = [t if i % 2 == 0 else re.sub('[ \t]+', '', t) for i, t in enumerate(s)]
    return ''.join(s)

###############################################################################
# Reserved-word look-up table.

def set_reserved_words():
    """
    Builds an immutable look-up table of BASIC's reserved words, at load-time.
    """
    w = list(KEYWORDS) + list(FUNCTIONS) + list(LOGICALS)
    w = sorted(w, key = lambda x: (len(x), x))
    i = [re.search('[$]$', x) is not None for x in w]
    u = [x for x, h in zip(w, i) if not h]
    v = [x for x, h in zip(w, i) if h]
    j = [len(x) for x in u]
    k = [len(x) for x in v]
    m = max(max(j), max(k) - 1)
    r = []
    for i in range(m + 1):
        a = [x for x, h in zip(u, j) if h == i]
        b = [x for x, h in zip(v, k) if h == i + 1]
        r.append((tuple(a), tuple(b)))
    r[0] = (m, m)
    set_pro('reservedWords', tuple(r))

def get_reserved_words(n, s):
    """
    Returns a tuple of BASIC's reserved words containing precisely n letters.
    If s being True (or False) selects for words ending with '$' (or not).
    """
    # This is called at run-time. When s is True, the returned words have n + 1
    # characters in total. The special case of n = 0 returns the length of
    # the longest reserved word (7 characters, for RESTORE).
    w = get_pro('reservedWords', None)
    return w[min(n, len(w))][int(s)]

###############################################################################
# Run-time retrieval of BASIC DATA, for READ commands.

def advance_to_next_datum():
    """
    Increments the data index, ready to read the next datum from the list.
    """
    set_data_index(get_data_index() + 1)

def get_data_index():
    """
    Returns the value of the data index.
    """
    return get_pro('dataIndex', 0)

def get_data_lines():
    """
    Returns all data line numbers.
    """
    return get_pro('dataLines', ())

def get_data_queue():
    """
    Returns the entire data list.
    """
    return get_pro('dataQueue', ())

def get_datum():
    """
    Returns the current datum from the list, and advances to the next.
    """
    d = get_data_queue()
    i = get_data_index()
    if len(d) <= i:
        return set_out_of_data_error()
    advance_to_next_datum()
    return d[i]

def go_to_first_datum():
    """
    Resets the data index to the first datum in the list.
    """
    set_data_index(0)

def seek_data(n):
    """
    Moves the data index to the first datum on the first program line numbered
    not less than BASIC number n.
    """
    # Moves beyond the list when n is too large.
    m = pvalue(n)
    d = get_data_lines()
    i = 0
    while i < len(d):
        if d[i] >= m: break
        i = i + 1
    set_data_index(i)

def set_data_index(i):
    """
    Moves the data index to position number i (which can be beyond the list).
    """
    set_pro('dataIndex', i)

###############################################################################
# Program-counter line index.

def advance_to_start_of_next_line():
    """
    Advances the program counter to the first statement on the next line.
    """
    set_line_index(get_line_index() + 1)
    go_to_first_statement_on_line()

def count_program_lines():
    """
    Returns the total number of lines in the stored BASIC program.
    """
    return len(get_file_line_numbers())

def get_line_index():
    """
    Returns the sequential index number of the current program line.
    """
    return get_pro('lineIndex', -1)

def go_to_first_line():
    """
    Goes to the first line, without altering the statement index.
    """
    set_line_index(0)

def go_to_start_of_first_line():
    """
    Goes to the first statement of the first line (the start of the program).
    """
    # Does the same thing as go_to_first_statement().
    go_to_first_line()
    go_to_first_statement_on_line()

def go_to_start_of_line(i):
    """
    Goes to the first statement (the start) of the i-th line (by line index,
    not by BASIC line number).
    """
    set_line_index(i)
    go_to_first_statement_on_line()

def reset_line_index():
    """
    Moves the line index out-of-program.
    """
    # Prior to loading another program when one has been run previously.
    set_line_index(-1)

def set_line_index(i):
    """
    Moves to the i-th line (by index), without changing the statement index.
    """
    set_pro('lineIndex', i)

def within_program():
    """
    Returns True if the line index lies within the range of the stored BASIC
    program. Returns False otherwise (including when no program is loaded).
    """
    i = get_line_index()
    return (i >= 0) and (i < count_program_lines())

###############################################################################
# Program-counter statement index.

def advance_to_next_statement():
    """
    Advances the program counter to the next statement.
    """
    # This might be on the current line, or the next.
    i = set_statement_index(get_statement_index() + 1)
    if i >= count_statements_on_line():
        advance_to_start_of_next_line()

def count_statements_on_line():
    """
    Returns the number of statements on the current line of the program.
    """
    return len(get_statements_on_line())

def get_statement_index():
    """
    Returns the index of the current statement on the current line.
    """
    # This is zero-indexed and line relative; the third statement on line 100
    # has index 2, as does the third statement on line 5000.
    return get_pro('statementIndex', 0)

def go_to_first_statement():
    """
    Resets the program counter to the first statement of the first line.
    """
    # Goes to the beginning of the BASIC program.
    # Same as go_to_start_of_first_line().
    go_to_first_line()
    go_to_first_statement_on_line()

def go_to_first_statement_on_line():
    """
    Goes to the first statement on the current line (without changing lines).
    """
    set_statement_index(0)

def set_statement_index(i):
    """
    Moves to the i-th statement on the current line.
    """
    # That statement need not exist.
    # (There is no protection against overshooting, here).
    return set_pro('statementIndex', i)

###############################################################################
# Full program-counter setter and getter (for loops and subroutines).

def get_point():
    """
    Returns the program counter as a (line-index, statement-index) tuple.
    """
    # (Returns the current position in the program.)
    return (get_line_index(), get_statement_index())

def set_point(p):
    """
    Sets the program counter from a (line-index, statement-index) tuple.
    """
    # (Goes to that position in the program.)
    set_line_index(p[0])
    set_statement_index(p[1])

###############################################################################
# GOSUB (subroutine) return-point stack.

def get_return_points():
    """
    Retrieves the entire return-point stack.
    """
    return get_pro('returnPoints', [])

def go_to_first_statement_after(p):
    """
    Moves to the statement immediately following the GOSUB at point p.
    """
    set_point(p)
    advance_to_next_statement()

def pop_return_point():
    """
    Pops the last return-point (removes it from the stack, then returns it).
    """
    p = get_return_points()
    if len(p) < 1:
        return set_return_without_gosub_error()
    a = p.pop()
    set_return_points(p)
    return a

def push_return_point(p):
    """
    Pushes a return-point, p, onto the top of the stack.
    """
    set_return_points(get_return_points() + [p])

def set_return_points(p):
    """
    Saves p as the entire return-point stack, in program memory.
    """
    set_pro('returnPoints', p)

###############################################################################
# FOR (loop) return-point stack.

def find_loop(p):
    """
    Returns the index of loop p, or -1 if it does not exist.
    The special case of p = None returns the index of the innermost loop.
    """
    # Locates loop p within the loop-stack of the current subroutine scope, and
    # returns its index (or -1, if p does not appear within the loop-stack). A
    # special case is p = None, for which the most recent loop is returned.
    u = get_loops()
    if len(u) < 1:
        return -1
    if p is None:
        return len(u) - 1
    n = loop_name(p)
    i = [name_of_loop(x) == n for x in u]
    if not any(i):
        return -1
    return min([j for j, t in enumerate(i) if t])

def get_all_loops():
    """
    Returns the list of loop definitions across all subroutine levels.
    """
    return get_pro('loopPoints', [[]])

def get_loops():
    """
    Returns the list of loop definitions for the current subroutine level.
    """
    p = get_all_loops()
    return p[-1]

def loop_name(p):
    """
    Returns the name of loop p (by which it is identified in the loop stack).
    """
    return name_for_loop(p['variable'])

def named_loop(p):
    """
    Gives a loop a name, before appending to the loop stack.
    """
    p['name'] = loop_name(p)
    return p

def name_for_loop(v):
    """
    Returns the (loop stack) name of the loop over variable v.
    """
    # Presently, this is just the variable's Python storage-object's name.
    return name_for_object(v)

def name_of_loop(p):
    """
    Returns the identifying name of loop p.
    """
    return p['name']

def new_loop(v, g, s):
    """
    Creates a new FOR loop, iterating over variable v, in increments of step
    s, until exceeding goal g, at the current point in the program.
    """
    return {'point': get_point(), 'variable': v, 'goal': g, 'step': s}

def set_all_loops(p):
    """
    Sets the entire list of loop definitions, for all subroutine levels.
    """
    set_pro('loopPoints', p)

def set_loops(p):
    """
    Sets the list of loop definitions, for the current subroutine level.
    """
    a = get_all_loops()[:-1]
    a.append(p)
    set_all_loops(a)

###############################################################################
# FOR (loop) program flow controls.

def conclude_loop(p):
    """
    Terminates loop p.
    """
    # Removes loop p from the stack, after its termination condition has been
    # met, or on beginning a new loop over the same iterator. Concluding loop p
    # also concludes any nested (subsequently initiated) loops. No action is
    # performed when loop p does not appear in the stack.
    i = find_loop(p)
    if i >= 0:
        set_loops(get_loops()[:i])

def drop_subroutine_loop():
    """
    Terminates all loops within the current subroutine.
    """
    # On RETURNing from a subroutine, this concludes all loops created within
    # it and drops the scoping level, reverting to the loops of the previous
    # level.
    a = get_all_loops()
    set_all_loops(a[:-1])

def get_loop_parameters(v):
    """
    Returns the parameters of the (unique) loop over variable v.
    """
    # Returns the parameters (return-point, iterator variable, stopping
    # condition, and iteration increment) of the FOR loop associated with
    # variable v. If such a loop exists, it is unique. If v is None, the most
    # recent loop is returned.
    u = get_loops()
    if len(u) < 1:
        return set_next_without_for_error()
    if v is None:
        return u[-1]
    if not is_number_valued(v) or is_array(v):
        return set_next_without_for_error()
    n = name_for_loop(v)
    for i in range(len(u) - 1, -1, -1):
        if u[i]['name'] == n:
            return u[i]
    return set_next_without_for_error()

def initiate_loop(v, g, s):
    """
    Initiates a new loop, iterating over variable v, in increments of step s,
    until exceeding goal g, within the current subroutine (scoping level), at
    the current point in the program. If another loop over the same iterator
    already exists within the same scope, that pre-existing loop is concluded
    (terminated/dropped), along with any nested loops.
    """
    p = new_loop(v, g, s)
    conclude_loop(p)
    a = get_loops()
    a.append(named_loop(p))
    set_loops(a)

def loop_again(p):
    """
    Moves the program counter to the first statement after the top (the
    defining FOR statement) of loop p.
    """
    set_point(p['point'])
    advance_to_next_statement()

def scope_subroutine_loops():
    """
    Creates a new level of loop scoping, upon beginning a new subroutine.
    """
    # Although (GOSUB) subroutines use the same variables as the rest of the
    # program (all BASIC variables being global), a subroutine only sees the
    # loops that were created within it.
    a = get_all_loops()
    a.append([])
    set_all_loops(a)

###############################################################################
# Run-time retrieval of line numbers and BASIC program statements.

def get_file_line_number():
    """
    Returns the source file line number of the current BASIC line.
    """
    # For example, if the current BASIC line reads '100 print x', and appears
    # on line 5 of the source file, then this function returns the value 5.
    i = get_line_index()
    n = get_file_line_numbers()
    if (i < 0) or (i >= len(n)):
        return -1
    return n[i]

def get_file_line_numbers():
    """
    Returns a tuple of all source-file line numbers for those source-file
    lines containing an executable BASIC line (as opposed to a comment or
    whitespace).
    """
    return get_pro('fileLineNumbers', ())

def get_line_number():
    """
    Returns the BASIC line number of the current program line.
    """
    i = get_line_index()
    n = get_line_numbers()
    if (i < 0) or (i >= len(n)):
        return -1
    return n[i]

def get_line_numbers():
    """
    Returns the BASIC line numbers for every line of the entire program.
    """
    return get_pro('lineNumbers', ())

def get_statement():
    """
    Returns the current BASIC statement.
    """
    return get_statements_on_line()[get_statement_index()]

def get_statements():
    """
    Returns the complete program listing, deconstructed to statements.
    """
    return get_pro('basicStatements', ())

def get_statements_on_line():
    """
    Returns a tuple of all statements on the current line.
    """
    # This can be empty when the line index lies beyond the end of the program.
    i = get_line_index()
    s = get_statements()
    if (i < 0) or (i >= len(s)):
        return ()
    return s[i]

###############################################################################
# Low-level exit-message constructors.

def clear_exit_state():
    """
    Removes any exit trigger; be it an error, a break, or a normal exit.
    """
    del_pro('exitTrigger')

def construct_location_clause():
    """
    Constructs a location clause, to be appended to an error or break message,
    when that error or break occurred in run-time (on a specific program line).
    """
    if not within_program():
        return ''
    n = get_line_number()
    if n < 0:
        return ' on file line ' + str(get_file_line_number())
    return ' on line ' + str(n)

def embellish_break_message(m):
    """
    Formats message m as a break message with line number (if applicable).
    """
    return m + construct_location_clause()

def embellish_error_message(m):
    """
    Formats message m as an error message with line number (if applicable).
    """
    return '? ' + m + ' Error' + construct_location_clause()

def get_exit_message():
    """
    Returns the exit message as a character string.
    """
    return pvalue(get_exit_trigger())

def get_exit_trigger():
    """
    Returns the exit message as a BASIC break or error object (or as a BASIC
    string, if no exit has been triggered).
    """
    return get_pro('exitTrigger', as_string(''))

def set_exit_trigger(m):
    """
    Sets the exit trigger condition to BASIC (break or error) data object m.
    This will overwrite any pre-existing condition.
    """
    set_pro('exitTrigger', m)

def set_if_no_exit_triggered(m):
    """
    Sets the exit-trigger to BASIC (break or error) object m, unless some
    other exit message already exists (in which case, no action is taken).
    Returns the original exit trigger condition.
    """
    if (running()):
        set_exit_trigger(m)
    return get_exit_trigger()

###############################################################################
# High-level exit-message constructors.

def set_break_message():
    """
    Thrown by a BASIC STOP command. Will not replace any pre-existing message.
    Returns the original exit trigger condition.
    """
    return set_if_no_exit_triggered(as_break(embellish_break_message('Break')))

def set_end_message():
    """
    Thrown by a BASIC END command (for a silent exit). Will not replace any
    pre-existing message. Returns the original exit trigger condition.
    """
    return set_if_no_exit_triggered(as_break(''))

def set_error_message(m):
    """
    Sets the exit message to an error based on character string m, but will
    not overwrite an existing message. Returns the original exit trigger.
    """
    return set_if_no_exit_triggered(as_error(embellish_error_message(m)))

###############################################################################
# Higher-level error message constructors.

def set_bad_subscript_error():
    """
    Raised when an index to an array lies outside its allowed range.
    """
    return set_error_message('Bad Subscript')

def set_division_by_zero_error():
    """
    Raised when attempting to divide something by zero.
    """
    return set_error_message('Division By Zero')

def set_duplicated_parameter_error():
    """
    Raised when defining a function of the same parameter twice, e.g., f(x,x).
    """
    return set_error_message('Duplicated Parameter')

def set_file_not_found_error():
    """
    Raised when attempting to access a file that cannot be read.
    """
    return set_error_message('File Not Found')

def set_illegal_quantity_error():
    """
    Raised when a numerical argument to a function lies outside its permitted
    range (such as when attempting to take the logarithm of a negative value).
    """
    return set_error_message('Illegal Quantity')

def set_line_out_of_sequence_error():
    """
    Raised when the program listing contains BASIC line numbers that are not
    monotonically increasing.
    """
    return set_error_message('Line Out of Sequence')

def set_next_without_for_error():
    """
    Raised when the program encounters an end-of-loop (NEXT), without having
    begun the loop (without the corresponding FOR).
    """
    return set_error_message('Next Without For')

def set_out_of_data_error():
    """
    Raised on an attempt to READ inline DATA, without there being any left in
    the queue.
    """
    return set_error_message('Out Of Data')

def set_redefined_line_error():
    """
    Raised when the program listing contains a duplicated BASIC line number.
    """
    return set_error_message('Redefined Line')

def set_redimmed_array_error():
    """
    Raised when attempting to DIM an array that has already been DIMmed (even
    when the new and old dimensions are identical).
    """
    return set_error_message('Redimmed Array')

def set_return_without_gosub_error():
    """
    Raised upon meeting an end-of-subroutine (RETURN), without being in one
    (without the corresponding GOSUB).
    """
    return set_error_message('Return Without Gosub')

def set_syntax_error():
    """
    Raised when a program statement breaks some or other BASIC syntax rule.
    """
    return set_error_message('Syntax')

def set_type_mismatch_error():
    """
    Raised when a string (or number) was required, but a number (or string)
    was given.
    """
    return set_error_message('Type Mismatch')

def set_undefined_function_error():
    """
    Raised on attempting to call a user function (FN) without first having
    defined it (with DEF FN).
    """
    return set_error_message('Undefined Function')

def set_undefined_statement_error():
    """
    Raised on attempting to GOTO or GOSUB a BASIC line number that does not
    appear within the program. This includes when attempting to GOTO/GOSUB to
    a character string, variable, floating-point number, or any other token(s)
    besides an unquoted literal string of digits.
    """
    return set_error_message('Undefined Statement')

###############################################################################
# Statement checking (for development purposes, only).

def all_checked():
    """
    Returns True when every last statement of the BASIC program has been
    executed successfully at some point. Returns False otherwise.
    """
    return len(unchecked_line_indices()) == 0

def generate_unchecked_list():
    """
    Creates a list of 'unchecked' flags, one for each program statement.
    """
    return [[False] * len(x) for x in get_statements()]

def get_checks():
    """
    Returns the full list of statement check-state flags.
    """
    return get_pro('checkedStatements', [])

def mark_statements_as_unchecked():
    """
    Flags all program statements as being unchecked.
    """
    set_checks(generate_unchecked_list())

def mark_statement_as_checked():
    """
    Flags the current statement as being checked. That is, as having been
    successfully executed by the interpreter in its entirety, without error.
    """
    s = get_checks()
    s[get_line_index()][get_statement_index()] = True
    set_checks(s)

def set_checks(s):
    """
    Stores check-list s in program memory.
    """
    set_pro('checkedStatements', s)

def unchecked_file_line_numbers():
    """
    Returns the source-file line numbers of the unchecked statements.
    """
    u = set(unchecked_line_indices())
    n = get_file_line_numbers()
    return [m for i, m in enumerate(n) if i in u]

def unchecked_line_indices():
    """
    Returns the indices of any BASIC program lines containing at least one
    unchecked statement.
    """
    return [i for i, x in enumerate(get_checks()) if not all(x)]

def unchecked_line_numbers():
    """
    Returns the BASIC program line numbers of the unchecked statements.
    """
    u = set(unchecked_line_indices())
    n = get_line_numbers()
    return [m for i, m in enumerate(n) if i in u]

def unchecked_lines():
    """
    Returns a listing of the unchecked (not wholly checked) program lines.
    """
    p = program_listing()
    s = set(line_has_statement(p))
    q = [a for i, a in enumerate(p) if i in s]
    u = set(unchecked_line_indices())
    return [a for i, a in enumerate(q) if i in u]

###############################################################################
# Print-buffer management.

def anything_in_print_buffer():
    """
    Returns True when the print buffer contains at least one character.
    Returns False otherwise.
    """
    return characters_in_print_buffer() > 0

def append_to_print_buffer(s):
    """
    Appends character string s to the print buffer.
    """
    # If s contains a newline or carriage return, the buffer is printed up to
    # (including) that character. If the buffer is too large for the console,
    # lines are printed until the remainder fits.
    s = str(s)
    if len(s) == 0:
        return None
    m = re.search('[\n\r]', s)
    while m is not None:
        i = m.start()
        set_print_buffer(get_print_buffer() + [substring(s, 0, i - 1)])
        reduce_print_buffer()
        print_print_buffer()
        if substring(s, i, i) == '\n':
            print_new_line()
        else:
            print_carriage_return()
        s = substring(s, i + 1)
        m = re.search('[\n\r]', s)
    set_print_buffer(get_print_buffer() + [s])
    reduce_print_buffer()

def characters_in_print_buffer():
    """
    Returns the number of characters, printable or otherwise, in the buffer.
    """
    return sum([len(x) for x in get_print_buffer()])

def clear_print_buffer():
    """
    Empties the print buffer, leaving nothing to be printed.
    """
    set_pro('printBuffer', [])

def get_print_buffer():
    """
    Retrieves the print buffer; a list of strings to be printed.
    """
    return get_pro('printBuffer', [])

def reduce_print_buffer():
    """
    When printing of the buffer would extend beyond the width of the terminal,
    we print however much fits and then begin a new line.
    """
    w = terminal_width()
    while virtual_cursor_position() > w:
        n = w - get_cursor_position()
        s = ''.join(get_print_buffer())
        print_text(substring(s, 0, n - 1))
        print_new_line()
        set_print_buffer(substring(s, n))

def set_print_buffer(s):
    """
    Sets the print buffer to string(s) s.
    """
    set_pro('printBuffer', s)

def terminal_width():
    """
    Returns the width of the terminal, in characters.
    """
    return int(get_terminal_size((80, 20))[0])

###############################################################################
# Cursor position.

def advance_cursor_position(n):
    """
    Moves the cursor n spaces to the right (whether or not that's still on the
    page).
    """
    set_cursor_position(get_cursor_position() + n)

def get_cursor_position():
    """
    Returns the cursor position; that being the (zero-indexed) console column
    from where the next chunk of printed output will begin. Not accurate when
    special characters (\a, \t, etc.) have already been printed on the line.
    """
    return get_pro('cursorPosition', 0)

def reset_cursor_position():
    """
    Resets the cursor position to the first (zero-eth) console column.
    """
    set_cursor_position(0)

def set_cursor_position(n):
    """
    Sets the cursor position to console column number n (zero-indexed).
    """
    set_pro('cursorPosition', n)

def virtual_cursor_position():
    """
    The position the cursor would have after printing the buffer without any
    line break. Not accurate in the presence of special characters; \a, etc.
    """
    return get_cursor_position() + characters_in_print_buffer()

###############################################################################
# Overprinting and print-skipping.

def get_characters_on_line():
    """
    The character string already printed on the current line.
    """
    # This is needed in case of a carriage return and subsequent TAB, SPC, or
    # comma over-skipping.
    return get_pro('printedChars', '')

def set_characters_on_line(s):
    """
    Sets the character string already printed on the current line.
    """
    set_pro('printedChars', s)

def set_no_characters_on_line():
    """
    Sets the current line to be empty.
    """
    set_characters_on_line('')

def update_characters_on_line(s):
    """
    Adds string s to the text printed on the current line, at the current
    cursor position. Text may already extend right of the cursor, in which
    case some or all of it is overprinted by s. Updates the cursor position
    accordingly.
    """
    n = len(s)
    k = get_cursor_position()
    p = get_characters_on_line()
    set_characters_on_line(substring(p, 0, k - 1) + s + substring(p, k + n))
    advance_cursor_position(n)

###############################################################################
# Teletypewriter-effect controls.

def character_pause():
    """
    Returns however many seconds are to be dwelt after printing a character.
    """
    return get_pro('ttCharDelay', 0)

def line_pause():
    """
    Returns however many seconds are to be dwelt after printing each line.
    """
    return get_pro('ttLineDelay', 0)

def set_teletype_char_delay(m):
    """
    Sets the teletype character-pause aesthetic. The argument, m, is a delay
    time, in milliseconds, to be dwelt after printing each character. The
    delay is restricted to between 0 and 0.2 seconds, with zero being the
    default. Real teletypes could manage around 10 characters per second.
    """
    if type(m) is int or type(m) is float:
        s = m / 1000
    else:
        s = 0
    set_pro('ttCharDelay', max(0, min(s, 0.2)))
    if (s < 0):
        set_teletype_line_delay(-1)

def set_teletype_line_delay(m):
    """
    Sets the teletype line-pause aesthetic. The argument, m, is a delay time,
    in milliseconds, to be dwelt after completing each line of printing. The
    delay is limited to no more than two seconds, with zero as the default.
    Negative values impose no delay, but flush the console after every line of
    printing.
    """
    if (type(m) is int or type(m) is float) and m != 0:
        s = m / 1000
    else:
        s = line_pause()
    if s < 0:
        s = -1
    else:
        s = min(s, 2)
    set_pro('ttLineDelay', s)

def set_upper_case_out(u):
    """
    Sets the upper-case aesthetic flag. If u is anything besides True, the
    flag is set to False (do not convert printed output to upper case).
    """
    set_pro('upperCase', u is True)

def upper_case_out():
    """
    Returns True when printing is to be done in upper case, otherwise False.
    """
    return get_pro('upperCase', False)

###############################################################################
# Pseudorandom numbers.

def get_last_random_number():
    """
    Returns the most recent previously generated pseudorandom number.
    """
    return get_pro('lastRandomNumber', 0)

def get_new_random_number():
    """
    Generates and returns a new pseudorandom number from the standard uniform
    distribution. Updates lastRandomNumber in case the value is wanted again.
    """
    return set_pro('lastRandomNumber', random())

###############################################################################
# Run-state tests, for trapping errors and terminating execution.

def exitt():
    """
    Returns the exit trigger, that being a BASIC error or break object. This
    is used to propagate the original error back up the function call stack.
    """
    return get_exit_trigger()

def running():
    """
    Returns True if and only if no exit message has been set (whether or not
    the program-counter lies within the program). Otherwise returns False.
    """
    return 'exitTrigger' not in prog_memory

def terminated():
    """
    Returns True if and only if an exit message has been set (whether or not
    the program-counter lies within the program). Otherwise returns False.
    """
    return 'exitTrigger' in prog_memory

###############################################################################
# BASIC heap storage, within a Python dictionary.                             #
###############################################################################

###############################################################################
# Clear heap memory.

def reset_heap_memory():
    """
    Delete all BASIC data storage objects (un-assigns all variables).
    """
    heap_memory.clear()

###############################################################################
# Python-object setter and getter.

def get_object(n):
    """
    Retrieves the storage-object named n, in its entirety.
    """
    return heap_memory[n]

def object_exists(n):
    """
    Returns True if and only if a storage-object (dictionary key) named n
    exists. Returns False otherwise.
    """
    return n in heap_memory.keys()

def set_element(n, e, v):
    """
    Assigns value v to element e of the storage-object named n.
    """
    heap_memory[n]['elements'][e] = v
    return v

def set_object(n, v):
    """
    Assigns value v to the storage-object named n.
    """
    heap_memory[n] = v
    return v

###############################################################################
# Functions acting upon Python object storage names.

def create_object(n, d):
    """
    Creates a storage-object of name n and BASIC (array) dimensions d.
    For a singleton (non-array) object, d should be an empty list.
    """
    v = initial_value(n)
    if (len(d) == 0):
        return set_object(n, v)
    e = d[0] + 1
    for i in range(1, len(d)):
        e = e * (d[i] + 1)
    return set_object(n, {'extent': d, 'elements': [v] * e})

def initial_value(n):
    """
    Returns the value to which the storage-object named n is initialised at
    the time of its creation.
    """
    if type_from_name(n) == BASIC_S: return INITIAL_STRING
    return INITIAL_NUMBER

###############################################################################
# Functions acting upon Python BASIC-data storage objects.

def assign_variable(v, a):
    """
    Assigns BASIC-value a to the BASIC variable (or array element) referenced
    by v.
    """
    if is_integer_valued(v):
        b = floor(pvalue(a))
    else:
        b = a
    if is_array(v):
        n = name_for_object(v)
        i = linearised_index(get_object(n), v)
        set_element(n, i, b)
    else:
        set_object(name_for_object(v), b)
    return b

def dimensionality_of_object(x):
    """
    Returns the integer number of dimensions of storage-object x (zero, in the
    case of a singleton non-array object).
    """
    return len(extent_of_object(x))

def extent_of_object(x):
    """
    Returns a tuple of the BASIC array dimensions spanned by Python storage-
    object x. That is, a return value of (2, 3) means x stores a BASIC array
    of those dimensions, e.g., A(2,3). Returns an empty tuple when x is not
    an array.
    """
    if is_array_object(x):
        return x['extent']
    return []

def is_array_object(x):
    """
    Returns True if heap-memory object x stores an array, or False otherwise
    (when x has no subscripts and stores only a scalar or singleton).
    """
    return type(x) is dict

def linearised_index(x, v):
    """
    Maps an n-dimensional set of BASIC-variable reference (v) subscripts to
    the index of a single element of Python storage-object x. Includes zero-
    dimensional singleton (non-array) objects and variables.
    """
    s = subscripts_of_variable(v)
    if len(s) == 0: return 0
    if len(s) == 1: return s[0]
    e = extent_of_object(x)
    i = s[0]
    p = 1
    for j in range(len(s) - 1):
        p = p * (e[j] + 1)
        i = i + p * s[j + 1]
    return i

def retrieve_value(x, v):
    """
    Extracts the BASIC value referenced by variable v from storage-object x.
    Variable subscript validity checks should already have been performed.
    """
    if is_array_object(x):
        a = x['elements'][linearised_index(x, v)]
    else:
        a = x
    if is_string_valued(v):
        return as_string(a)
    return as_number(a)

def subscripts_match(x, v):
    """
    Checks whether or not a storage-object, x, and a BASIC variable reference,
    v, have the same number of dimensions (subscripts) and that x is large
    enough to encompass the specific subscripts of v. Returns True if and only
    if this is the case, or False otherwise. Subscripts must be evaluated to
    integers before this is called.
    """
    d = dimensionality_of_object(x)
    n = number_of_subscripts(v)
    if (d == 0) and (n == 0): return True
    if d != n: return False
    e = extent_of_object(x)
    s = subscripts_of_variable(v)
    for i in range(len(e)):
        if e[i] < s[i]: return False
    return True

###############################################################################
# BASIC-variable reference-object constructor and getters.

def name_of_variable(v):
    """
    Returns the name of the BASIC variable referenced by v, as a character
    string. This includes the trailing $ or % in the case of string or integer
    variables, respectively. Does not include the parenthesis or subscripts of
    array-element references (only the name of the whole array).
    """
    return v['name']

def subscripts_of_variable(v):
    """
    Returns the subscripts of BASIC variable reference v as a list of either
    integers (of evaluated subscripts) or of strings (of unevaluated BASIC
    expressions). This is empty when the variable is dimensionless (has no
    subscripts).
    """
    return v['subscripts']

def variable(n, i):
    """
    Constructs a BASIC variable reference object, for a variable of name n and
    subscripts i. For scalar (non-array) references, i should be an empty list.
    """
    # The subscripts, i, may be evaluated (to integers) or unevaluated strings
    # of BASIC expressions (ordinarily the latter). Besides the usual data-
    # typed variables, A, A$, etc., we also use these constructs for user-
    # defined functions, FNA(X). These have the same name-subscripts-value
    # description, and are indeed variable, but the subscripts need not be
    # integers and the (string) value is evaluated as code, rather than taking
    # its face value.
    return {'name': n, 'subscripts': i}

###############################################################################
# Initialisation, assignment and recall of BASIC variables.

def dimension_array(v):
    """
    Initialises a BASIC array of the name and dimensions in reference v.
    """
    n = name_for_object(v)
    if object_exists(n): return set_redimmed_array_error()
    i = eval_subscripts(subscripts_of_variable(v))
    if terminated(): return Exit()
    return create_object(n, i)

def get_value(v):
    """
    Returns the value of the BASIC variable (or array element) referenced by
    v. A default value is set if the variable has not yet been assigned.
    """
    n = name_of_variable(v)
    s = eval_subscripts(subscripts_of_variable(v))
    v = variable(n, s)
    if terminated(): return Exit()
    x = get_or_create_object(v)
    if not subscripts_match(x, v): return set_bad_subscript_error()
    return retrieve_value(x, v)

def set_value(v, a):
    """
    Assigns BASIC value a to the BASIC variable (or array element) referenced
    by v. Returns a.
    """
    n = name_of_variable(v)
    s = eval_subscripts(subscripts_of_variable(v))
    v = variable(n, s)
    if terminated(): return Exit()
    x = get_or_create_object(v)
    if not subscripts_match(x, v): return set_bad_subscript_error()
    if not types_match(v, a): return set_type_mismatch_error()
    assign_variable(v, a)
    return a

###############################################################################
# Functions acting upon BASIC-variable references.

def default_extent(v):
    """
    Returns default BASIC array dimensions for initialising the BASIC variable
    referenced by v when it has not already been defined by a DIM statement.
    Returns an empty list when v is a singleton (not an array).
    """
    return [DEFAULT_EXTENT for i in range(number_of_subscripts(v))]

def get_or_create_object(v):
    """
    Retrieves the entirety of the Python storage-object for the BASIC variable
    or array referenced by v. If the storage-object does not already exist, it
    will be created (with default dimensions and values) beforehand.
    """
    n = name_for_object(v)
    if object_exists(n): return get_object(n)
    return create_object(n, default_extent(v))

def is_array(v):
    """
    Returns True if and only if the BASIC variable referenced by v is an
    element of a BASIC array. Returns False otherwise.
    """
    return number_of_subscripts(v) != 0

def is_integer_valued(v):
    """
    Returns True if and only if the BASIC variable referenced by v is an
    integer-constrained number. Returns False otherwise.
    """
    return is_integer_constrained(name_of_variable(v))

def is_number_valued(v):
    """
    Returns True if and only if the BASIC variable referenced by v is a
    number (be it float or integer). Returns False otherwise.
    """
    return type_of_variable(v) == BASIC_N

def is_string_valued(v):
    """
    Returns True if and only if the BASIC variable referenced by v is a
    character string. Returns False otherwise.
    """
    return type_of_variable(v) == BASIC_S

def name_for_object(v):
    """
    Maps the name of the BASIC variable referenced by v to the name of its
    Python data-storage object (dictionary key).
    """
    # In BASIC, X and X(1) are two different objects. We prepend a marker to
    # array names, rather than appending a '(', in order to keep variable
    # data-type checks simple (these look for a trailing '$').
    if is_array(v): return '_' + name_of_variable(v)
    return name_of_variable(v)

def number_of_subscripts(v):
    """
    Returns the number of subscripts (dimensions) of BASIC variable v.
    """
    return len(subscripts_of_variable(v))

def types_match(v, a):
    """
    Returns True if and only if the BASIC data type of the variable reference
    v matches that of the BASIC value a. Returns False otherwise.
    """
    return type_of_variable(v) == btype(a)

def type_of_variable(v):
    """
    Returns the BASIC data type (string or number) of variable (reference) v.
    """
    return type_from_name(name_of_variable(v))

###############################################################################
# Define and recall user-defined BASIC functions.

def define_function(f, p, s):
    """
    Define a function, named f, of parameter variables named p, as the BASIC
    expression of character string s. The parameters must all be singletons
    (no arrays).
    """
    # Parameters are stored by the names of their corresponding Python objects.
    # To distinguish the function from data-type objects, its name, f,
    # necessarily begins with 'FN' (in upper, lower, or mixed case).
    n = [name_for_object(variable(v, [])) for v in p]
    set_object(f, {'parameters': n, 'definition': s})

def recall_function(f):
    """
    Returns the definition of the user-defined function named f. To distinguish
    the function from data-type objects, its name, f, necessarily begins with
    'FN' (in upper, lower, or mixed case).
    """
    if not object_exists(f): return set_undefined_function_error()
    return get_object(f)

###############################################################################
# Type utilities, acting on any name(s); variable, function, or storage-object.

def is_integer_constrained(n):
    """
    Returns True when string n names an integer-constrained variable, Python
    storage object, or user-defined function. Returns False otherwise.
    """
    return substring(n, len(n) - 1) == '%'

def type_from_name(n):
    """
    Returns the data-type of a variable, or the return type of a user-defined
    function, from either its name, or the associated Python-object name, n.
    """
    if substring(n, len(n) - 1) == '$': return BASIC_S
    return BASIC_N

def types_from_names(n):
    """
    Returns a list of the data-types of the variables, storage-objects, or
    user-defined functions named in list n.
    """
    return [type_from_name(m) for m in n]

###############################################################################
# BASIC data type definitions, casting, and testing.                          #
###############################################################################

# BASIC expressions are evaluated to data objects (mainly numbers and strings,
# but also errors and operators), consisting of a data-type (name) and a data
# value bound in a tuple. Errors return data objects as a simple expediency.
# Operators are treated as data objects until such time as they are applied.

###############################################################################
# BASIC-datum type and value extractors.

def caseless(x):
    """
    Returns the underlying Python value of BASIC datum x, but raised to upper
    case if x is a string. Used to make case-insensitive comparisons.
    """
    if is_string(x):
        return pvalue(x).upper()
    return pvalue(x)

def btype(x):
    """
    Returns the data-type of BASIC datum x.
    """
    return x[0]

def pvalue(x):
    """
    Returns the underlying Python value of BASIC datum x.
    """
    return x[1]

###############################################################################
# BASIC type casters.

def as_break(m):
    """
    Flags m as being a break result (message).
    """
    return as_type(m, BASIC_B)

def as_error(m):
    """
    Flags m as being an error result (message).
    """
    return as_type(m, BASIC_E)

def as_number(n):
    """
    Flags n as being an evaluated BASIC numerical value.
    """
    return as_type(n, BASIC_N)

def as_operator(s):
    """
    Flags s as being an unapplied BASIC operator.
    """
    return as_type(s, BASIC_O)

def as_string(s):
    """
    Flags s as being an evaluated BASIC character string.
    """
    return as_type(s, BASIC_S)

def as_type(x, y):
    """
    Casts object x to BASIC data-type y.
    """
    # Object x might already be a BASIC value of type y, or it might be of some
    # other type, or it might be a raw Python value (the underlying value of a
    # BASIC datum).
    if type(x) is not tuple or len(x) == 1:
        return (y, x)
    if btype(x) != y:
        return (y, pvalue(x))
    return x

###############################################################################
# BASIC type checkers.

def is_break(x):
    """
    Returns True if x is a BASIC break result (message).
    Otherwise returns False.
    """
    return is_type(x, BASIC_B)

def is_error(x):
    """
    Returns True if x is a BASIC error result (message).
    Otherwise returns False.
    """
    return is_type(x, BASIC_E)

def is_number(x):
    """
    Returns True if x is a fully evaluated BASIC number.
    Otherwise returns False.
    """
    return is_type(x, BASIC_N)

def is_operator(x):
    """
    Returns True if x is an unapplied BASIC operator.
    Otherwise returns False.
    """
    return is_type(x, BASIC_O)

def is_string(x):
    """
    Returns True if x is a fully evaluated BASIC string.
    Otherwise returns False.
    """
    return is_type(x, BASIC_S)

def is_type(x, y):
    """
    Returns True if and only if x is a BASIC datum of type y.
    Otherwise returns False.
    """
    return type(x) is tuple and len(x) == 2 and btype(x) == y

###############################################################################
# Implements the action of BASIC commands (beginning with a keyword).         #
###############################################################################

###############################################################################
# Top-level statement processor.

def enact(s):
    """
    Top-most BASIC-statement processing function. Identifies the primary
    command keyword of statement s, and calls the appropriate method for
    handling it.
    """
    if terminated(): return exitt()
    a = which_action(s)
    if a == 'None':
        return enact_none(s)
    return ACTION[a](trim(s, a))

###############################################################################
# Utilities for the top-level processor.

def trim(s, w):
    """
    Removes as many characters as are in word w from the start of string s.
    """
    return substring(s, len(w))

def which_action(s):
    """
    Returns the leading BASIC keyword (command) of statement s, or 'None' in
    the absence of such.
    """
    k = begins_with_which(KEYWORDS, s)
    if len(k) == 0:
        return 'None'
    return k

###############################################################################
# Implied actions when no leading keyword is present.

def enact_implied_GOTO(s):
    """
    A string of digits after THEN is an implied GOTO (that line number).
    """
    return enact_GOTO(s)

def enact_implied_LET(s):
    """
    No keyword at the beginning of a non-blank statement is an implied LET.
    """
    return enact_LET(s)

def enact_none(s):
    """
    No keyword at the beginning of a statement is either an implied LET
    assignment (when the statement is non-blank), or simply a do-nothing (when
    the statement is blank). Although supported here, blank statements are not
    found in original BASIC.
    """
    if len(s) > 0: return enact_implied_LET(s)
    mark_statement_as_checked()
    advance_to_next_statement()

###############################################################################
# Actions for each BASIC command (keyword).

def enact_CLEAR(s):
    """
    Performs a CLEAR; deletes everything in heap memory.
    """
    # Does not touch either the loop or subroutine return-point stacks. In 8K
    # Altair BASIC, CLEAR <N> deletes everything in heap memory and allocates
    # <N> (bytes?) for character string storage. Here, we ignore <N>, so long
    # as it is a positive number.
    if len(s) > 0:
        n = eval_expression(s)
        if not is_number(n): return set_type_mismatch_error()
        if pvalue(n) < 0: return set_illegal_quantity_error()
    reset_heap_memory()
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_DATA(s):
    """
    Actions DATA statements at run-time (when they are are skipped-over).
    """
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_DEF(s):
    """
    Actions DEF FN definition of custom user-functions.
    """
    # A function must have at least one parameter variable, even if just a
    # dummy. Here, we allow multiple parameters of any data type (number,
    # integer, or string). Many original flavours of BASIC insisted on
    # precisely one parameter, of number type only. Parameters cannot have
    # subscripts (no array elements allowed). Here, functions may return
    # numbers or strings, and must have the usual type suffix, $, for the
    # latter. Number-valued functions may possess the integer suffix, %, in
    # which case their output is constrained as such. Many original BASICs
    # only support unconstrained number-valued definitions.
    if not begins_with('FN', s): return(set_syntax_error())
    # The detach_leading_variable() function would raise an error on 'FN'.
    a = detach_leading_variable(trim(s, 'FN'))
    v = a['variable']
    if not is_array(v): return set_syntax_error()
    # Restore the 'FN' (or 'fn', etc.) to the case-sensitive function name, n.
    n = substring(s, 0, 1) + name_of_variable(v)
    p = subscripts_of_variable(v)
    # Check all parameter names are singletons (no subscripted array-members).
    for q in p:
        if not re.fullmatch('[a-zA-Z][a-zA-Z0-9]*[%$]{0,1}', q):
            return set_syntax_error()
    r = set()
    for q in p:
        if q in r: return set_duplicated_parameter_error()
        r.add(q)
    s = a['remainder']
    if not begins_with('=', s): return set_syntax_error()
    s = substring(s, 1)
    if len(s) == 0: return set_syntax_error()
    define_function(n, p, s)
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_DELAY(s):
    """
    Actions DELAY commands, for pausing execution for some amount of time.
    """
    # This is not found in original BASIC, but is introduced here as a
    # replacement for delay loops.
    n = eval_expression(s)
    if not is_number(n): return set_type_mismatch_error()
    if pvalue(n) < 0: return set_illegal_quantity_error()
    print_print_buffer()
    sys.stdout.flush()
    sleep(pvalue(n))
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_DIM(s):
    """
    Actions a DIM command, for dimensioning one or more arrays.
    """
    a = split_arguments(s)
    if terminated(): return exitt()
    for b in a:
        v = detach_leading_variable(b)
        if terminated(): return exitt()
        if len(v['remainder']) > 0: return set_syntax_error()
        dimension_array(v['variable'])
        if terminated(): return exitt()
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_END(s):
    """
    Actions END commands. These set a blank exit message to halt program
    execution and terminate quietly.
    """
    if len(s) > 0: return set_syntax_error()
    mark_statement_as_checked()
    set_end_message()

def enact_FN(s):
    """
    It is an error for a statement to begin with FN, which should only appear
    after DEF, or as part of a name within an arithmetical expression.
    """
    return set_syntax_error()

def enact_FOR(s):
    """
    Implements FOR - TO - STEP commands. These define a looping condition to
    be checked by NEXT.
    """
    # This function is only called to initialise the loop, not on every
    # iteration. Because the looping condition is not checked at this (FOR)
    # point, BASIC loops always execute at least once (this was the case for
    # early versions of BASIC, but not for later versions). While it would be
    # easier to process the STEP term first, we work in left-to-right order so
    # that the user hears about the leftmost error (should one occur).
    a = detach_leading_variable(s)
    if terminated(): return exitt()
    v = a['variable']
    s = a['remainder']
    if not is_number_valued(v) or is_array(v): return set_syntax_error()
    if not begins_with('=', s): return set_syntax_error()
    i = position_of_first('TO', s)
    if i < 0: return set_syntax_error()
    a = eval_expression(substring(s, 1, i - 1))
    if not is_number(a): return set_type_mismatch_error()
    s = substring(s, i + 2)
    i = position_of_first('STEP', s)
    if i < 0:
        b = eval_expression(s)
    else:
        b = eval_expression(substring(s, 0, i - 1))
    if not is_number(b): return set_type_mismatch_error()
    if i < 0:
        d = as_number(1)
    else:
        d = eval_expression(substring(s, i + 4))
        if not is_number(d): return set_type_mismatch_error()
    set_value(v, a)
    if terminated(): return exitt()
    initiate_loop(v, b, d)
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_GO(s):
    """
    GO on its own is an error. While a reserved word, it should only appear as
    part of GOTO or GOSUB. (Historically, GO TO was allowed with a space.)
    """
    return set_syntax_error()

def enact_GOSUB(s):
    """
    Actions GOSUB commands. The subroutine must be an integer literal.
    """
    if re.fullmatch('\d+', s) is None:
        return(set_undefined_statement_error())
    m = int(s)
    n = get_line_numbers()
    if m not in n: return set_undefined_statement_error()
    push_return_point(get_point())
    mark_statement_as_checked()
    scope_subroutine_loops()
    go_to_start_of_line(n.index(m))

def enact_GOTO(s):
    """
    Actions GOTO commands. The destination must be an integer literal.
    """
    if re.fullmatch('\d+', s) is None:
        return(set_undefined_statement_error())
    m = int(s)
    n = get_line_numbers()
    if m not in n: return set_undefined_statement_error()
    mark_statement_as_checked()
    go_to_start_of_line(n.index(m))

def enact_IF(s):
    """
    Actions IF - THEN and IF - GOTO statements.
    """
    # The statement will only be marked as checked after the condition has
    # evaluated True and the subsequent THEN (or GOTO) sub-statement has been
    # successfully executed.
    i = position_of_first('THEN', s)
    g = position_of_first('GOTO', s)
    if (g > 0) and ((i < 0) or (g < i)):
        i = g
    if (i < 1): return set_syntax_error()
    k = is_false(eval_expression(substring(s, 0, i - 1)))
    if terminated(): return exitt()
    if k:
        return advance_to_start_of_next_line()
    s = substring(s, i + 4)
    if i == g:
        return enact_GOTO(s)
    if re.fullmatch('\d+', s) is not None:
        return enact_implied_GOTO(s)
    return enact(s)

def enact_INPUT(s):
    """
    Actions INPUT statements, through which user-input is entered.
    """
    # Specifies the default input prompt.
    p = 1

    # The INPUT keyword may be immediately followed by an optional string
    # literal. If so, append it to the print buffer. The string must be
    # followed by either a semicolon (display the default input prompt) or a
    # comma (do not display any input prompt). Set p accordingly.
    i = [x.start() for x in re.finditer('"', s)]
    if (len(i) > 0) and (i[0] == 0):
        if len(i) < 2: return set_syntax_error()
        i = i[1]
        p = substring(s, i + 1, i + 1)
        if (p != ",") and (p != ";"): return set_syntax_error()
        append_to_print_buffer(substring(s, 1, i - 1))
        s = substring(s, i + 2)
        p = int(p == ';')

    # The statement should end with a comma-separated list of zero or more
    # variables to be assigned. Separate these.
    if len(s) > 0:
        v = detach_leading_variables(s)
        if terminated(): return exitt()
        if len(v['remainder']) > 0: return set_syntax_error()
        v = v['variables']
    else:
        v = []

    # Accept as many comma-separated input items from the user as there are
    # variables to assign (or one item, in the no-variable case). If the user
    # enters too few items, the addendum prompt is displayed and the remainder
    # are sought. If the user enters too many items, or an item of the wrong
    # data type (not-a-number, where a number was expected), a warning is
    # issued and we start over. Human errors here are non-fatal.
    a = []
    u = prompt_for_input(p)
    while len(a) < len(v):
        for s in scan_data(u):
            if len(a) >= len(v):
                p = -1
                break
            d = datum_to_variable(v[len(a)], s)
            if is_error(d):
                p = -1
                break
            a.append(d)
        if p < 0:
            issue_redo_from_start_warning()
            a = []
        if len(a) == len(v):
            break
        p = int(sign(len(a))) + 1
        u = prompt_for_input(p)

    # Assign all variables (if any), before moving on to the next statement.
    if len(v) > 0:
      for x, y in zip(v, a):
          set_value(x, y)
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_LET(s):
    """
    Actions LET commands (assigns values to variables).
    """
    # The first = in a LET statement is the assignment operator; any others
    # being relational comparisons.
    a = detach_leading_variable(s)
    if terminated(): return exitt()
    x = a['variable']
    s = a['remainder']
    if not begins_with('=', s): return set_syntax_error()
    v = eval_expression(substring(s, 1))
    if terminated(): return exitt()
    set_value(x, v)
    if terminated(): return exitt()
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_NEXT(s):
    """
    Actions NEXT commands.
    """
    # The statement s can be empty (tests the most recent loop), or a comma-
    # separated list of variable names (each tests that specific loop). Unlike
    # enact_FOR(), this function is called on every iteration. A loop is only
    # broken when the iterator exceeds its goal; merely equalling the goal
    # results in one more iteration. By 'exceed', we mean 'greater than' when
    # the step is non-negative, and 'less than' when the step is negative.
    r = ''
    v = None
    if len(s) > 0:
        v = detach_leading_variable(s)
        if terminated(): return exitt()
        r = v['remainder']
        v = v['variable']
    p = get_loop_parameters(v)
    if terminated(): return exitt()
    if len(r) == 0: mark_statement_as_checked()
    v = p['variable']
    g = pvalue(p['goal'])
    s = pvalue(p['step'])
    a = pvalue(get_value(v)) + s
    set_value(v, as_number(a))
    if s < 0:
        s = -1
    else:
        s = 1
    if sign(a - g) != s:
        return loop_again(p)
    conclude_loop(p)
    if len(r) > 0:
        if not begins_with(',', r) or (len(r) < 2): return set_syntax_error()
        return enact_NEXT(substring(r, 1))
    advance_to_next_statement()

def enact_ON(s):
    """
    # Actions ON - GOTO/GOSUB commands.
    """
    # The switching number, k, between ON and GOTO or GOSUB, cannot be
    # negative. Destinations, after the GOTO or GOSUB, must be integer
    # literals. The program will jump to the k-th destination. If k is zero,
    # or exceeds the number of destinations, the ON command is ignored, and
    # the program moves on to the next statement. It is an error for k to be
    # negative. The statement is marked as checked once any one GOTO or GOSUB
    # has been successfully executed. Checking is imperfect, since one of the
    # other destinations might not exist.
    i = position_of_first('GO', s)
    if i < 0: return set_syntax_error()
    k = eval_expression(substring(s, 0, i - 1))
    if not is_number(k): return set_type_mismatch_error()
    k = int(floor(pvalue(k)))
    if k < 0: return set_illegal_quantity_error()
    if k == 0: return advance_to_next_statement()
    r = substring(s, i, i + 5)
    if begins_with('GOTO', r):
        g = 'GOTO'
    elif begins_with('GOSUB', r):
        g = 'GOSUB'
    else:
        return set_syntax_error()
    s = scan_data(substring(s, i + len(g)))
    if k > len(s): return advance_to_next_statement()
    return ACTION[g](s[k - 1])

def enact_PRINT(s):
    """
    Evaluates, formats, and prints each term of PRINT statement s.
    """
    eval_print_statement(s)
    if terminated(): return print_non_empty_line()
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_READ(s):
    """
    Actions READ statements, wherein each variable of a comma-separated list
    is assigned the next inline DATA item.
    """
    u = detach_leading_variables(s)
    if terminated(): return exitt()
    if len(u['remainder']) != 0: return set_syntax_error()
    for v in u['variables']:
        s = get_datum()
        if terminated(): return exitt()
        d = datum_to_variable(v, s)
        if is_error(d): return set_type_mismatch_error()
        set_value(v, d)
        if terminated(): return exitt()
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_REM(s):
    """
    Actions REM remarks. Being comments, these are skipped-over.
    """
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_RESTORE(s):
    """
    Actions RESTORE commands.
    """
    # The command word may optionally be followed by a number (literal or
    # variable). In the absence of that number, the data pointer resets to the
    # first inline BASIC DATA item. In the presence of that number, the data
    # pointer moves to the first datum on the first line with a BASIC line
    # number not less than the RESTORE number. The original flavours of BASIC
    # had differing capabilities with regard to the RESTORE number (allowed,
    # only literal integer constants allowed, or not allowed).
    if len(s) == 0:
        go_to_first_datum()
    else:
        n = eval_expression(s)
        if not is_number(n): return set_type_mismatch_error()
        seek_data(n)
    mark_statement_as_checked()
    advance_to_next_statement()

def enact_RETURN(s):
    """
    Actions a RETURN command, to move the program back to the first statement
    after the last GOSUB.
    """
    if len(s) != 0: return set_syntax_error()
    p = pop_return_point()
    if terminated(): return exitt()
    mark_statement_as_checked()
    drop_subroutine_loop()
    go_to_first_statement_after(p)

def enact_STEP(s):
    """
    It is an error for a statement to begin with STEP, which should only
    appear after FOR and TO, as part of a FOR - TO - STEP statement.
    """
    return set_syntax_error()

def enact_STOP(s):
    """
    Actions STOP commands. These terminate the program with a break message.
    """
    if len(s) != 0: return set_syntax_error()
    mark_statement_as_checked()
    set_break_message()

def enact_THEN(s):
    """
    It is an error for a statement to begin with THEN, which should appear
    only after IF, as part of an IF - THEN statement.
    """
    return set_syntax_error()

def enact_TO(s):
    """
    It is an error for a statement to begin with TO, which should only appear
    after FOR, as part of a FOR - TO - <STEP> statement.
    """
    return set_syntax_error()

###############################################################################
# Parsing of BASIC-variable names.

def detach_leading_variable(s):
    """
    Extracts the BASIC variable at the beginning of (partial) statement s, and
    returns that variable, along with the remainder of the statement, in a
    dictionary. If s does not begin with a variable, a syntax error is raised.
    """
    i = end_of_leading_name(s)
    if i < 0: return set_syntax_error()
    j = position_of_closing_parenthesis(substring(s, i + 1))
    if j < 0:
        k = []
        r = substring(s, i + 1)
    else:
        k = split_arguments(substring(s, i + 2, i + j))
        r = substring(s, i + j + 2)
    v = variable(substring(s, 0, i), k)
    return {'variable': v, 'remainder': r}

def detach_leading_variables(s):
    """
    Extracts all of the comma-separated variables from partial statement s,
    and returns them in a dictionary, along with the remainder of s.
    """
    v = []
    while running():
        a = detach_leading_variable(s)
        if terminated(): return exitt()
        v.append(a['variable'])
        s = a['remainder']
        if substring(s, 0, 0) != ",": break
        s = substring(s, 1)
    return {'variables': v, 'remainder': s}

def end_of_leading_name(s):
    """
    Returns the position of the last character of the name at the beginning of
    string s, or 0 or -1 if no such name is there.
    """
    # A name is one alphabetical character followed by a (possibly empty)
    # string of alphanumerics before up to one type identifier (% or $), and
    # does not include any BASIC reserved word (command keyword, function, or
    # logical operator).
    i = re.match('[a-zA-Z][a-zA-Z0-9]*[%$]{0,1}', s)
    if i is None:
        return -1
    return position_of_first_reserved_word(substring(s, 0, i.end() - 1)) - 1

def position_of_first(w, s):
    """
    Returns the position of the first case-insensitive appearance of word w
    within string s, but not within a string literal. Returns -1 when w does
    not appear within s.
    """
    i = uncontained(w.upper(), s.upper(), '"')
    if len(i) < 1:
      return -1
    return i[0]

def position_of_first_reserved_word(s):
    """
    Returns the position of the first appearance of any reserved BASIC word
    (keyword, function, or operator) within non-empty string s, which should
    consist of an alphabetic character followed by zero or more alphanumeric
    characters and an optional trailing % or $.
    """
    # The magic numbers 2 and 6 come about from all reserved words being
    # between 2 and 7 characters. None contain digits or end in %. Returns the
    # length of s when no reserved word is present (positions within s lie on
    # {0, 1, ... len(s) - 1}).
    for g in re.finditer('[A-Z]{2,}[$]*', s.upper()):
        t = g.group()
        d = t[-1] == '$'
        m = len(t) - int(d)
        for i in range(0, m - 1):
            for j in range(i + 1, min(i + 6, m)):
                q = substring(t, i, j)
                w = get_reserved_words(j - i + 1, False)
                for v in w:
                    if v == q: return g.start() + i
            if d and (m - i > 1) and (m - i < 6):
                q = substring(t, i, m + 1)
                w = get_reserved_words(m - i, True)
                for v in w:
                    if v == q: return g.start() + i
    return len(s)

def uncontained(w, s, z):
    """
    Returns all positions of character (or word) w within string s that do not
    lie between a pair of delimiting characters (or words, typically quotation
    marks) z, according to the even/odd delimiter-count rule. Case sensitive.
    """
    u = positions_of(w, s)
    v = positions_of(z, s)
    return [x for x in u if len([1 for y in v if y < x]) % 2 == 0]

###############################################################################
# Data readers (including user input).

def datum_to_number(s):
    """
    Converts string s (being user-input or a DATA item) to a BASIC number.
    """
    # BASIC regards blanks, and decimal points with no digit on either side,
    # as representations of zero. Returns a non-fatal error on failure.
    w = re.sub('[ \t]+', '', s).upper()
    p = '[+-]{0,1}\\.(E[+-]{0,1}[\d]*){0,1}$'
    if (len(w) == 0) or (re.match(p, w) is not None):
        return as_number(0)
    try:
        n = float(w)
    except:
        return as_error('Failed Numeric Conversion')
    return as_number(n)

def datum_to_string(s):
    """
    Converts Python-string s (being user-input or a DATA item) to a BASIC
    string, by removing leading and trailing quotes only when a leading quote
    is present.
    """
    if begins_with('"', s):
        return as_string(re.sub('^"|"$', '', s))
    else:
        return as_string(s)

def datum_to_variable(v, s):
    """
    Converts Python-string s (being either user-input or a DATA item) to a
    BASIC string or number, whichever is appropriate for variable v. Returns a
    non-fatal error in response to conversion failure.
    """
    if is_string_valued(v):
        return datum_to_string(s)
    else:
        return datum_to_number(s)

def scan_data(s):
    """
    Picks comma-separated values (inline or user-input) out of string s, for
    use with DATA, INPUT, or ON commands.
    """
    # BASIC takes no action on any keywords in data, so 'DATA 1REM,2,3' scans
    # to three items, rather than one and a remark. Colons still split
    # statements, so 'DATA 1:REM,2' contains one data point. We leave encasing
    # quotes in place, because while 'DATA 5' can be READ to string or number
    # type, 'DATA "5"' can only be READ as a string. Items with an opening
    # quotation mark need not have a closing one.
    i = uncontained(',', s, '"')
    j = [0] + [h + 1 for h in i]
    k = [h - 1 for h in i] + [len(s) - 1]
    return [substring(s, x, y) for x, y in zip(j, k)]

###############################################################################
# BASIC to Python logical truth of value conversion.

def is_false(x):
    """
    Returns True (or False) if BASIC-value x is regarded as logically false
    (or true) in BASIC. Sets a syntax error when x is not a value type.
    """
    if is_number(x): return pvalue(x) == 0
    if is_string(x): return len(pvalue(x)) == 0
    return set_syntax_error()

def is_true(x):
    """
    Returns True (or False) if BASIC-value x is regarded as logically true
    (or false) in BASIC. Sets a syntax error when x is not a value type.
    """
    if is_number(x): return pvalue(x) != 0
    if is_string(x): return len(pvalue(x)) > 0
    return set_syntax_error()

###############################################################################
# Evaluation of BASIC expressions (not containing a command keyword).         #
###############################################################################

###############################################################################
# Top-level evaluators.

def eval_expression(s):
    """
    Evaluates the BASIC expression supplied in non-empty character string s.
    """
    if terminated(): return exitt()
    if is_evaluated(s): return(s)
    a = []
    while len(s) > 0:
        p = eval_first_term(s)
        a = a + p[:-1]
        s = p[-1]
    a = result(a)
    if is_evaluated(a): return a
    a = result(eval_unary_groups(a))
    if is_evaluated(a): return a
    a = result(apply_binary_operators(a))
    if is_evaluated(a): return a
    return set_syntax_error()

def eval_first_term(s):
    """
    Delegates the evaluation of the BASIC expression in string s to a handler
    specific to the leading (left-most) term in that expression. Returns the
    result of evaluating that first term in a list along with any remaining
    unevaluated portion of the expression.
    """
    # The SPC() and TAB() functions are only permitted within PRINT statements
    # (which is not here).
    if begins_with_any(('SPC', 'TAB'), s): return set_syntax_error()
    if begins_with_any(LETTERS, s): return eval_name(s)
    if begins_with_any(DIGITS, s): return eval_number(s)
    if begins_with_any(OPERATORS, s): return isolate_operator(s)
    if begins_with('(', s): return eval_group(s)
    if begins_with('"', s): return eval_string(s)
    return interrupt(set_syntax_error())

###############################################################################
# Component-specific evaluators.

def eval_arguments(s):
    """
    Evaluates each expression in a comma-separated list supplied as string s.
    """
    return eval_expressions(split_arguments(s))

def eval_expressions(x):
    """
    Evaluates each expression (string) in list x.
    """
    if type(x) is str: return [eval_expression(x)]
    return [eval_expression(a) for a in x]

def eval_function(s):
    """
    Evaluates the BASIC function at the beginning of expression s.
    """
    f = begins_with_which(FUNCTIONS, s)
    r = trim(s, f)
    i = position_of_closing_parenthesis(r)
    a = eval_arguments(substring(r, 1, i - 1))
    return intermediate(BFUN[f](a), substring(r, i + 1))

def eval_group(s):
    """
    Evaluates the parenthesis-enclosed expression at the head of string s.
    """
    i = position_of_closing_parenthesis(s)
    if i < 0: return interrupt(set_syntax_error())
    g = substring(s, 1, i - 1)
    if len(g) == 0: return interrupt(set_syntax_error())
    return intermediate(eval_expression(g), substring(s, i + 1))

def eval_name(s):
    """
    Evaluates the alphanumerically named object at the beginning of statement
    s. This might be a variable, a function, or a logical operator.
    """
    if begins_with('FN', s): return(eval_user_function(s))
    if begins_with_any(LOGICALS, s): return(isolate_logical(s))
    if begins_with_any(FUNCTIONS, s): return(eval_function(s))
    v = detach_leading_variable(s)
    return intermediate(get_value(v['variable']), v['remainder'])

def eval_number(s):
    """
    Evaluates the character-representation integer or floating point number at
    the beginning of string s to a numeric data type.
    """
    # In BASIC, spaces are allowed anywhere (these will have been removed),
    # parentheses are not allowed anywhere, and E can only be followed by an
    # (optional, signed) integer (read as 0 in its absence).
    i = re.match('\d*\.{0,1}\d*', s).end()
    if i >= (len(s) - 1):
        return intermediate(as_number(string_to_number(s)), '')
    a = substring(s, i)
    j = re.match('[eE][+-]{0,1}\d*', a)
    if j is not None:
        i = i + j.end()
        a = substring(a, j.end())
    return intermediate(as_number(string_to_number(substring(s, 0, i - 1))), a)

def eval_string(s):
    """
    Evaluates the BASIC string literal at the beginning of expression string
    s. (Removes the enclosing quotes, the first is guaranteed to be present.)
    """
    i = s.find('"', 1)
    if i < 1: return intermediate(as_string(substring(a, 1)), '')
    return intermediate(as_string(substring(s, 1, i - 1)), substring(s, i + 1))

def eval_subscripts(s):
    """
    Evaluates a list of BASIC array-variable subscripts, s, to Python integers,
    for getting and setting values in heap memory. The subscripts might already
    be evaluated, or they might be lists of unevaluated expression strings.
    """
    if (len(s) < 1) or (type(s[0]) is int): return s
    i = eval_expressions(s)
    for j in range(len(i)):
        if btype(i[j]) != BASIC_N: return set_type_mismatch_error()
        i[j] = int(floor(pvalue(i[j])))
        if i[j] < 0: return set_illegal_quantity_error()
    return i

def eval_unary_groups(a):
    """
    Evaluates the (implied) groups over which unary operations +, -, and NOT
    extend, before applying the unary operation to the result.
    """
    # For simplicity, evaluation is performed right to left. Order of
    # precedence is preserved, with unary + applying only to the immediately
    # adjacent element, unary - extending as far as the next operator besides
    # ^ (at position j), and unary NOT extending as far as the first logical
    # binary operator (at position k).
    j = len(a)
    k = len(a)
    x = [i for i, b in enumerate(a) if btype(b) == BASIC_O]
    x.reverse()
    for i in x:
        n = pvalue(a[i])
        # When the operator is a unary NOT, evaluate its group, then apply the
        # NOT. With right to left evaluation, groups cannot contain any unary
        # operators, so we need only apply any binaries.
        if n == 'NOT':
            if k - i < 2: return set_syntax_error()
            a[i] = eval_NOT(apply_binary_operators(a[(i + 1):k]))
            del a[(i + 1):k]
            k = i + 1
            j = k
            continue
        # Unary + and - are distinguishable from their binary counterparts by
        # their immediately following either another operator, or nothing
        # (being in the first position). Unary + isn't quite the same as doing
        # nothing, since it raises an error if its operand isn't a number or
        # string.
        if (i == 0) or is_unevaluated(a[i - 1]):
            if n == '-':
                if j - i < 2: return set_syntax_error()
                a[i] = eval_NEGATE(apply_binary_operators(a[(i + 1):j]))
                del a[(i + 1):j]
                k = k - j + i + 1
                j = i + 1
                continue
            if n == '+':
                a[i] = eval_IDENTITY(a[i + 1])
                del a[i + 1]
                j = j - 1
                k = k - 1
                continue
        # When the operator is binary, reassess the end-points of the extent
        # of any subsequent (leftward) arithmetical (j) or logical (k) unary
        # operators.
        if n != '^':
            j = i
            if n in LOGICALS:
                k = i
    return a

def eval_user_function(s):
    """
    Evaluates the user-defined BASIC function at the beginning of string s.
    """
    # Note that function parameters, as in f['parameters'], are stored as names
    # of the underlying heap-memory storage-objects, not as BASIC variables.
    a = detach_leading_variable(trim(s, 'FN'))
    if terminated():
        return interrupt(exitt())
    v = a['variable']
    n = substring(s, 0, 1) + name_of_variable(v)
    y = type_from_name(n)
    f = recall_function(n)
    if terminated():
        return interrupt(exitt())
    p = f['parameters']
    u = eval_expressions(subscripts_of_variable(v))
    if not args_match(types_from_names(p), u):
        return interrupt(exitt())
    z = []
    for q, v in zip(p, u):
        if object_exists(q):
            z.append(get_object(q))
        else:
            z.append(initial_value(q))
        w = pvalue(v)
        if is_integer_constrained(q):
            w = floor(w)
        set_object(q, w)
    x = eval_expression(f['definition'])
    for q, v in zip(p, z):
        set_object(q, v)
    if btype(x) != y:
        return interrupt(set_type_mismatch_error())
    if is_integer_constrained(n):
        x = as_number(floor(pvalue(x)))
    return intermediate(x, a['remainder'])

###############################################################################
# Evaluation assistants.

def args_match(a, x):
    """
    Returns True if the evaluated BASIC values in list x exactly match the
    types named by list a. Raises an error and returns False otherwise. This
    function is only called after complete evaluation of all arguments in x.
    """
    # Hence all are of BASIC number of string type (no Nones, operators, or
    # untyped values), otherwise an error would have been raised beforehand by
    # eval_expression().
    if (len(a) == len(x)):
        if all([b == btype(y) for b, y in zip(a, x)]):
            return True
        else:
            set_type_mismatch_error()
    else:
        set_syntax_error()
    return False

def begins_with(w, s):
    """
    Returns True if and only if string s begins with word w. Returns False
    otherwise. Case insensitive.
    """
    return s.upper().startswith(w.upper())

def begins_with_any(w, s):
    """
    Returns True if string s begins with any of the strings in list w.
    Alternatively, s can be a list and w a string. Case insensitive.
    """
    if type(w) is not str:
        for v in w:
            if begins_with(v, s): return True
        return False
    elif type(s) is not str:
        for r in s:
            if begins_with(w, r): return True
        return False
    return begins_with(w, s)

def begins_with_which(w, s):
    """
    Returns the longest string from list w that appears at the beginning of
    string s (i.e., the greediest match). Case insensitive. Returns an empty
    string when no string in w matches the beginning of s.
    """
    a = ''
    for v in w:
        if begins_with(v, s) and (len(v) > len(a)):
            a = v
    return a

def is_evaluated(x):
    """
    Returns True if x is a fully evaluated BASIC value (a string or number).
    Otherwise returns False, including if x is None.
    """
    return not is_unevaluated(x)

def is_function(s):
    """
    Returns True if s is the name of a BASIC function (ABS, MID$, et cetera).
    Otherwise returns False, including if s is empty or None.
    """
    return (type(s) is str) and (s.upper() in FUNCTIONS)

def isolate_logical(s):
    """
    Detaches a logical operator from the beginning of statement s.
    The operator is not applied at this time.
    """
    x = begins_with_which(LOGICALS, s)
    return intermediate(as_operator(x), substring(s, len(x)))

def isolate_operator(s):
    """
    Detaches an arithmetical or relational operator from the beginning of
    statement s. The operator is not applied at this time.
    """
    x = begins_with_which(OPERATORS, s)
    return intermediate(as_operator(x), substring(s, len(x)))

def is_unevaluated(x):
    """
    Returns False if x is a fully evaluated BASIC value (a string or number).
    Otherwise returns True, including if x is None or empty or non-singleton.
    """
    return (type(x) is not tuple) or (btype(x) not in (BASIC_N, BASIC_S))

def intermediate(x, s):
    """
    Bundles the result, x, of evaluating part of a statement, with the
    remaining (unevaluated) part, s (a character string), into list.
    """
    return [x, s]

def interrupt(e):
    """
    A special version of intermediate() for when an error has occurred. Sets
    the remaining (unevaluated) expression to the empty string, leaving
    nothing to evaluate (ends evaluation, even if the error itself doesn't).
    """
    return intermediate(e, '')

def position_of_closing_parenthesis(s):
    """
    If the first character in statement s is an opening parenthesis, we return
    the position (index) of the corresponding closing parenthesis. If that
    closing parenthesis does not exist within s, then an error is raised and
    -2 is returned. If the first character in s is not an opening parenthesis,
    then -1 is returned (no error is raised in this case).
    """
    # While we perhaps ought to check for REMs here (which would hide any
    # parentheses to the right), we get the same syntax error on attempting to
    # evaluate the REM, anyway. In original BASIC, 'MID$("ABC", "D", REM)' and
    # 'MID$("ABC", "D"' are both type mismatch errors (on the "D"), before
    # getting to the REM or missing parenthesis, while we'll get a syntax error
    # as all arguments are evaluated before type checks.
    if not begins_with('(', s): return(-1)
    iq = positions_of('"', s)
    io = unenclosed('(', s, iq)[1:]
    ic = unenclosed(')', s, iq)
    for i in range(len(ic)):
        if len([1 for j in io if j < ic[i]]) == i: return ic[i]
    set_syntax_error()
    return -2

def positions_of(w, s):
    """
    Returns all positions of word w within string s. Returns an empty list
    when w does not appear within s. Case sensitive.
    """
    if len(w) > len(s): return []
    if len(w) == 0: return list(range(len(s)))
    return [i for i in range(len(s) - len(w) + 1) if s.startswith(w, i)]

def result(x):
    """
    Unwraps list of terms x to a BASIC datum when the calculation is finished.
    """
    if (type(x) is list) and (len(x) == 1) and (type(x[0]) is tuple):
        return x[0]
    return x

def sign(x):
    """
    Signum function of number x.
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def split_arguments(s):
    """
    Splits a character string, s, of comma-separated (unevaluated) statements
    into a list of those same statements.
    """
    # As in position_of_closing_parenthesis, we do not check for REMs. If one
    # is present, we'll still get a syntax error on attempting to evaluate it.
    if s.find(',') < 0: return [s]
    if re.search('["(]', s) is None: return s.split(',')
    iq = positions_of('"', s)
    io = unenclosed('(', s, iq)
    ic = unenclosed(')', s, iq)
    id = unbracketed(unenclosed(',', s, iq), io, ic)
    a = [0] + [i + 1 for i in id]
    b = [i - 1 for i in id] + [len(s) - 1]
    return [substring(s, i, j) for i, j in zip(a, b)]

def string_to_number(s):
    """
    Converts the character-string representation of an integer or floating
    point number, s, to numerical type, without flagging it as being an
    evaluated BASIC number.
    """
    # Neither Python nor BASIC allow parentheses within the string, nor E being
    # followed by a non-integer power, nor E being the first character in the
    # string. BASIC allows '1E', '1E+', and '1E-' (all read as 1E0), while
    # Python insists upon the trailing 0. BASIC allows blank spaces while
    # Python does not, but these will have already been removed. Unlike Python,
    # BASIC allows '.', '.E', '.E+4', etc., so we catch these as a special case
    # ('.' without digits is read as floating-point zero).
    if re.match('\.(E|$)', s, re.IGNORECASE) is not None: return 0
    if re.search('E[+-]{0,1}$', s, re.IGNORECASE) is not None: s = s + '0'
    try:
        n = float(s)
    except:
        return set_syntax_error()
    return n

def substring(s, i, j = 1000000):
    """
    Extracts the i-th through j-th characters (both included), from string s.
    Both i and j can be negative or exceed the length of s.
    """
    if i < 0:
        i = 0
    if j > len(s) - 1:
        j = len(s) - 1
    if i > j:
        return ''
    else:
        return s[i:(j + 1)]

def unbracketed(x, a, b):
    """
    Returns the positions, x, along some string, that are not contained
    between opening and closing brackets at positions a and b, respectively.
    # Any or all of these can be empty. Returns an empty list when no
    # unbracketed positions appear within x. The 'k' in '(k' is considered to
    # be contained (even in the absence of a closing bracket).
    """
    return [y for y in x
            if len([1 for j in b if j < y]) >= len([1 for i in a if i < y])]

def unenclosed(w, s, i):
    """
    Returns all positions of word w within string s that are not inside a pair
    of delimiting characters (or words, typically double quotes) at positions
    i along the same string, according to the even/odd delimiter-count rule.
    Case sensitive. The delimiter-position list, i, can be empty. Returns an
    empty list when there are no unenclosed occurrences of w within s.
    """
    u = positions_of(w, s)
    return [v for v in u if len([1 for j in i if j < v]) % 2 == 0]

###############################################################################
# Binary-operator applicators.

def apply_adders(a):
    """
    Applies any addition or subtraction operators appearing within the list of
    BASIC statement components, a. Addition includes string concatenation.
    """
    return apply_collection(ADDERS, a)

def apply_binary_operators(a):
    """
    Applies all BASIC binary operators found within the list of (otherwise)
    evaluated expression components, a, in order of decreasing precedence.
    There can be no groupings or unary operators within the list.
    """
    a = result(apply_exponentiators(a))
    if is_evaluated(a): return a
    a = result(apply_multipliers(a))
    if is_evaluated(a): return a
    a = result(apply_adders(a))
    if is_evaluated(a): return a
    a = result(apply_relationals(a))
    if is_evaluated(a): return a
    return result(apply_logicals(a))

def apply_collection(f, a):
    """
    Applies any of the members of a dictionary of equal-precedence operators,
    f, wherever they appear within the list of BASIC statement components, a,
    in left-to-right order.
    """
    # An example of f is {'^': eval_RAISE}.
    # The terminated() check is necessary in case of adjacent operators.
    z = which_are_operators(f.keys(), a)
    for h in range(len(z)):
        j = z[h]
        i = j - 1
        k = j + 1
        a[k] = f[pvalue(a[j])](a[i], a[k])
        if terminated(): return set_syntax_error()
        del a[i:k]
        z = [y - 2 for y in z]
    return a

def apply_exponentiators(a):
    """
    Applies any exponentiation (power) operators appearing within the list of
    BASIC statement components, a, in left-to-right order.
    """
    return apply_collection(EXPONENTIATORS, a)

def apply_logicals(a):
    """
    Applies any binary logical operators appearing within the list of BASIC
    statement components, a, in order of decreasing precedence.
    """
    b = LOGICAL_BINARIES
    for k in b.keys():
        a = apply_collection({k:b[k]}, a)
    return a

def apply_multipliers(a):
    """
    Applies any multiplication or division operators appearing within the list
    of BASIC statement components, a.
    """
    return apply_collection(MULTIPLIERS, a)

def apply_relationals(a):
    """
    Applies any relational operators appearing within the list of BASIC
    statement components, a, in left-to-right order.
    """
    return apply_collection(RELATIONALS, a)

def which_are_operators(s, a):
    """
    Returns the position indices, within the list of BASIC statement
    components, a, of any member of the list of operator symbols, s.
    """
    return [i for i, x in enumerate(a)
            if btype(x) == BASIC_O and pvalue(x) in s]

###############################################################################
# BASIC function evaluators.

def eval_ABS(x):
    """
    Returns the absolute value of the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(abs(pvalue(x[0])))

def eval_ASC(x):
    """
    Returns the ASCII code of the first character of the BASIC string x.
    """
    if not args_match([BASIC_S], x): return exitt()
    s = pvalue(x[0])
    if len(x) < 1: return set_illegal_quantity_error()
    return as_number(ord(s[0]))

def eval_ATN(x):
    """
    Returns the arctangent of the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(atan(pvalue(x[0])))

def eval_CHR_(x):
    """
    Returns the ASCII character whose code is the greatest integer not greater
    than the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    v = int(floor(pvalue(x[0])))
    if v < 0: return set_illegal_quantity_error()
    return as_string(chr(v))

def eval_COS(x):
    """
    Returns the cosine of the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(cos(pvalue(x[0])))

def eval_EXP(x):
    """
    Returns the exponential of the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(exp(pvalue(x[0])))

def eval_INSTR(x):
    """
    Locates one string within another. List x contains two or three arguments:
    # integer N, string S, and word W, with N being optional (defaults to one).
    # Returns the position of the first (case-insensitive) occurrence of W
    # within S not before the Nth character. Returns zero when S is empty, or
    # has fewer than N characters, or when W does not appear within S at or
    # after the Nth character. W can be the empty string (matches at N).
    """
    if len(x) == 2: x.insert(0, as_number(1))
    if not args_match([BASIC_N, BASIC_S, BASIC_S], x): return exitt()
    i = max(1, int(floor(pvalue(x[0])))) - 1
    s = pvalue(x[1]).upper()
    w = pvalue(x[2]).upper()
    if i >= len(s): return as_number(0)
    return as_number(s.find(w, i) + 1)

def eval_INT(x):
    """
    Returns the greatest integer not greater than the BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(floor(pvalue(x[0])))

def eval_LEFT_(x):
    """
    Returns the leftmost x[1] characters of BASIC string x[0], or the whole of
    x[0] if it has fewer than x[1] characters.
    """
    if not args_match([BASIC_S, BASIC_N], x): return exitt()
    n = int(floor(pvalue(x[1])))
    if n < 0: return set_illegal_quantity_error()
    return as_string(substring(pvalue(x[0]), 0, n - 1))

def eval_LEN(x):
    """
    Returns the number of characters in BASIC string x.
    """
    if not args_match([BASIC_S], x): return exitt()
    return as_number(len(pvalue(x[0])))

def eval_LOG(x):
    """
    Returns the natural logarithm of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    v = pvalue(x[0])
    if v <= 0: return set_illegal_quantity_error()
    return as_number(log(v))

def eval_MID_(x):
    """
    Returns x[2] characters from BASIC string x[0], beginning from the x[1]th
    character. If x[2] is omitted, or if x[1] + x[2] exceeds the number of
    characters in x[0], then all characters in x[0], from the x[1]th onward,
    are returned. If x[1] exceeds the number of characters in x[0], then an
    empty string is returned.
    """
    if not args_match([BASIC_S, BASIC_N, BASIC_N][:len(x)], x): return exitt()
    s = pvalue(x[0])
    i = int(floor(pvalue(x[1]))) - 1
    if len(x) == 3:
        j = int(floor(pvalue(x[2])))
    else:
        j = len(s)
    if (i < 0) or (j < 0): return set_illegal_quantity_error()
    return as_string(substring(s, i, i + j - 1))

def eval_POS(x):
    """
    Returns the (virtual) cursor position from the left margin (position 0).
    Not accurate when special characters are on the line (\a, \t, et cetera).
    """
    if not args_match([BASIC_N], x): return exitt()
    if pvalue(x[0]) != 1: return set_illegal_quantity_error()
    return as_number(virtual_cursor_position())

def eval_RND(x):
    """
    Returns a pseudo-random variate from the uniform distribution over (0, 1).
    When x is zero, the previous value is returned (rather than a new one).
    """
    if not args_match([BASIC_N], x): return exitt()
    v = pvalue(x[0])
    if v == 1: return as_number(get_new_random_number())
    if v == 0: return as_number(get_last_random_number())
    return set_illegal_quantity_error()

def eval_RIGHT_(x):
    """
    Returns the rightmost x[1] characters of BASIC string x[0], or the whole
    of x[0] if it has fewer than x[1] characters.
    """
    if not args_match([BASIC_S, BASIC_N], x): return exitt()
    s = pvalue(x[0])
    m = pvalue(x[1])
    if m < 0: return set_illegal_quantity_error()
    n = len(s)
    return as_string(substring(s, n - int(floor(m)), n))

def eval_SGN(x):
    """
    Returns the signum function of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(sign(pvalue(x[0])))

def eval_SIN(x):
    """
    Returns the sine of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(sin(pvalue(x[0])))

def eval_SPC(x):
    """
    Rapidly moves the cursor x spaces to the right or left, wrapping at the
    width of the console (which may trigger one or more newlines). Wrapping
    may be inaccurate when special characters (\t, etc.) are on the line.
    """
    if not args_match([BASIC_N], x): return exitt()
    n = int(floor(pvalue(x[0])))
    if n < 0:
        retract_print_head(-n)
        return as_operator(';')
    k = virtual_cursor_position()
    w = terminal_width()
    m = (k + n) - w
    if m > 0:
        print_buffer_and_new_line()
        n = m
    while n > w:
        print_new_line();
        n = n - w
    advance_print_head(n)
    return as_operator(';')

def eval_SQR(x):
    """
    Returns the square root of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    v = pvalue(x[0])
    if v < 0: return set_illegal_quantity_error()
    return as_number(sqrt(v))

def eval_STR_(x):
    """
    Returns a character-string representation of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    s = PRINT_PRECISION.format(pvalue(x[0]))
    return as_string(re.sub('^0\.', '.', s))

def eval_STRING_(x):
    """
    Returns a BASIC string consisting of x[0] copies of string x[1] (or of
    spaces, if x[1] is omitted).
    """
    if not args_match([BASIC_N, BASIC_S][:len(x)], x): return exitt()
    n = int(floor(pvalue(x[0])))
    if n < 0: return set_illegal_quantity_error()
    if len(x) == 2:
        s = pvalue(x[1])
    else:
        s = " "
    return as_string(s * n)

def eval_SYST(x):
    """
    Returns the current system date-time, in seconds.
    """
    if not args_match([BASIC_N], x): return exitt()
    if pvalue(x[0]) != 1: return set_illegal_quantity_error()
    return as_number(datetime.today().timestamp())

def eval_TAB(x):
    """
    Positions the cursor such that the next character will be printed in
    column x. We extend to allow negative values to mean -x spaces from the
    right-hand margin. If the cursor already lies to the right of the
    requested position, a new line is begun. Positioning will be inaccurate
    when special characters (\a, \b, \t, etc.) have been placed on the line.
    """
    if not args_match([BASIC_N], x): return exitt()
    p = int(floor(pvalue(x[0]))) % terminal_width()
    k = virtual_cursor_position()
    if p < k:
        print_buffer_and_new_line()
        k = 0
    advance_print_head(p - k)
    return as_operator(';')

def eval_TAN(x):
    """
    Returns the tangent of BASIC number x.
    """
    if not args_match([BASIC_N], x): return exitt()
    return as_number(tan(pvalue(x[0])))

def eval_TTW(x):
    """
    Returns the current width of the terminal, as a number of characters.
    """
    if not args_match([BASIC_N], x): return exitt()
    if pvalue(x[0]) != 1: return set_illegal_quantity_error()
    return as_number(terminal_width())

def eval_VAL(x):
    """
    Treats BASIC string x as the character representation of a numerical
    value, and returns the corresponding BASIC number. When x cannot be
    identified as a number, BASIC 0 is returned (no error is raised).
    """
    if not args_match([BASIC_S], x): return exitt()
    s = pvalue(x[0])
    if re.search('E[+-]{0,1}$', s, re.IGNORECASE) is not None: s = s + '0'
    try:
        n = float(s)
    except:
        return as_number(0)
    return as_number(n)

###############################################################################
# Arithmetical operations.

def eval_ADD(x, y):
    """
    Applies the addition operator between two BASIC numbers or two BASIC
    strings (performs concatenation), x and y.
    """
    if is_string(x) and is_string(y):
        return as_string(pvalue(x) + pvalue(y))
    if is_number(x) and is_number(y):
        return as_number(pvalue(x) + pvalue(y))
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_DIVIDE(x, y):
    """
    Applies the division operator between two BASIC numbers, x (the dividend)
    and y (the divisor).
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if not is_number(x) or not is_number(y):
        return set_type_mismatch_error()
    if pvalue(y) == 0:
        return set_division_by_zero_error()
    return as_number(pvalue(x) / pvalue(y))

def eval_IDENTITY(x):
    """
    Applies the unary identity operation to a BASIC string or number, x.
    This function is only called after x has been fully evaluated. BASIC
    allows this operation upon strings (e.g., +'A'). Expressions such as '3+'
    and '+' are not allowed; the operator must still act on a valid value.
    """
    if is_unevaluated(x):
        return set_syntax_error()
    return x

def eval_MULTIPLY(x, y):
    """
    Applies the multiplication operator between two BASIC numbers, x and y.
    """
    if is_number(x) and is_number(y):
        return as_number(pvalue(x) * pvalue(y))
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_NEGATE(x):
    """
    Applies the unary negation operator to a BASIC number, x.
    This function is only called after x has been fully evaluated.
    """
    # BASIC does not allow negation of strings.
    if is_number(x):
        return as_number(-pvalue(x))
    if is_unevaluated(x):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_RAISE(x, y):
    """
    Applies the exponentiation operator between two BASIC numbers, x (the
    base) and y (the power).
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if not is_number(x) or not is_number(y):
        return set_type_mismatch_error()
    a = pvalue(x)
    b = pvalue(y)
    if (a < 0) and (b != floor(b)):
        return set_illegal_quantity_error()
    if (a == 0) and (b < 0):
        return set_division_by_zero_error()
    return as_number(a ** b)

def eval_SUBTRACT(x, y):
    """
    Applies the subtraction operator between two BASIC numbers, x (the
    subtrahend) and y (the minuend).
    """
    if is_number(x) and is_number(y):
        return as_number(pvalue(x) - pvalue(y))
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    return set_type_mismatch_error()

###############################################################################
# Relational operations.

def eval_EQUAL(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x equals BASIC value y. Otherwise,
    returns BASIC 0 (false). String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) == caseless(y)))

def eval_GREATER(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x is greater than BASIC value y.
    Otherwise, returns BASIC 0 (false).
    String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) > caseless(y)))

def eval_LESS(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x is less than BASIC value y.
    Otherwise, returns BASIC 0 (false).
    String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) < caseless(y)))

def eval_NOT_EQUAL(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x does not equal BASIC value y.
    Otherwise, returns BASIC 0 (false).
    String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) != caseless(y)))

def eval_NOT_GREATER(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x is less than or equal to BASIC
    value y. Otherwise, returns BASIC 0 (false).
    String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) <= caseless(y)))

def eval_NOT_LESS(x, y):
    """
    Returns BASIC -1 (true) if BASIC value x is greater than or equal to BASIC
    value y. Otherwise, returns BASIC 0 (false).
    String comparisons are case-insensitive.
    """
    if is_unevaluated(x) or is_unevaluated(y):
        return set_syntax_error()
    if btype(x) != btype(y):
        return set_type_mismatch_error()
    return as_number(-int(caseless(x) >= caseless(y)))

###############################################################################
# Logical bitwise operations.

def eval_AND(a, b):
    """
    Performs bitwise logical AND on BASIC numbers a and b, after coercing both
    to integer format.
    """
    if is_number(a) and is_number(b):
        return as_number(int(pvalue(a)) & int(pvalue(b)))
    if is_unevaluated(a) or is_unevaluated(b):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_NOT(a):
    """
    Performs bitwise logical NOT on BASIC number a, after coercing it to
    integer format. Within this format, NOT A = -(A + 1). Hence,
    NOT NOT A = A, NOT 0 = -1, and NOT -1 = 0, consistent with BASIC's
    false = 0, true = -1.
    """
    if is_number(a):
        return as_number(~int(pvalue(a)))
    if is_unevaluated(a):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_OR(a, b):
    """
    Performs bitwise logical OR on BASIC numbers a and b, after coercing both
    to integer format.
    """
    if is_number(a) and is_number(b):
        return as_number(int(pvalue(a)) | int(pvalue(b)))
    if is_unevaluated(a) or is_unevaluated(b):
        return set_syntax_error()
    return set_type_mismatch_error()

def eval_XOR(a, b):
    """
    Performs bitwise logical XOR on BASIC numbers a and b, after coercing both
    to integer format.
    """
    if is_number(a) and is_number(b):
        return as_number(int(pvalue(a)) ^ int(pvalue(b)))
    if is_unevaluated(a) or is_unevaluated(b):
        return set_syntax_error()
    return set_type_mismatch_error()

###############################################################################
# Evaluation and printing of PRINT statements (and INPUT prompts).            #
###############################################################################

###############################################################################
# Top-level print evaluators.

def eval_print_statement(s):
    """
    Evaluates, formats and prints each term of PRINT statement s.
    """
    if len(s) == 0:
        return print_buffer_and_new_line()
    a = []
    while running() and (len(s) > 0):
        p = eval_first_print_term(s)
        if terminated(): return print_final_term(a)
        a = a + p[:-1]
        s = p[-1]
        if interior_term_has_ended(a[-1], s):
            a = append_interior_term(a)
    if running():
        print_final_term(a)

def eval_first_print_term(s):
    """
    Delegates the evaluation of the BASIC PRINT expression in string s to a
    handler specific to the leading (left-most) term in that expression.
    Returns the result of evaluating that first term in a list along with any
    remaining (unevaluated) portion of the expression.
    """
    if begins_with('"', s): return eval_string(s)
    if begins_with_any(LETTERS, s): return eval_name(s)
    if begins_with_any(SEPARATORS, s): return isolate_separator(s)
    if begins_with('(', s): return eval_group(s)
    if begins_with_any(OPERATORS, s): return isolate_operator(s)
    if begins_with_any(DIGITS, s): return eval_number(s)
    return interrupt(set_syntax_error())

###############################################################################
# Evaluation assistants.

def append_interior_term(a):
    """
    Evaluates a single PRINT term, formats the result for printing, and
    appends it to the print buffer. List a comprises the term as a collection
    of BASIC values and operators, followed by a separator. The collection may
    be empty, or the separator absent (implied semicolon), but not both (list
    a cannot be empty).
    """
    n = len(a)
    s = is_separator(a[n - 1])
    if (n > 1) or (not s):
        if s:
            b = result(a[:-1])
        else:
            b = result(a)
        if is_unevaluated(b):
            b = result(eval_unary_groups(b))
        if is_unevaluated(b):
            b = result(apply_binary_operators(b))
        if is_unevaluated(b):
            return set_syntax_error()
        append_to_print_buffer(format_printable(b))
    if s:
        append_to_print_buffer(format_separator(a[n - 1]))
    return []

def format_printable(x):
    """
    Formats a BASIC string or number, x, to a print-ready Python string.
    """
    if is_string(x): return pvalue(x)
    n = PRINT_PRECISION.format(pvalue(x))
    n = re.sub('^(-{0,1})0\.', '\\1.', n)
    if not begins_with("-", n):
        n = ' ' + n
    return n + ' '

def format_separator(x):
    """
    Converts separation operator x to some number of spaces for printing. This
    is always zero when using skip_to_print_zone() for comma separators.
    """
    if pvalue(x) == ';':
        return ''
    else:
        return skip_to_print_zone()

def interior_term_has_ended(a, s):
    """
    Returns True on reaching the end of an interior PRINT term. This occurs
    when the last component of the current term, a, is a separator, or else
    when that same component is a data value and the remaining unevaluated
    statement, s, following it is both non-empty and does not begin with a
    binary operator.
    """
    # We have to look ahead on s, instead of just evaluating the next term, in
    # case it calls POS(1) (with the current term not yet committed to the
    # buffer).
    return (is_separator(a) or
        (is_evaluated(a) and len(s) > 0 and not begins_with_any(BINARIES, s)))

def isolate_separator(s):
    """
    Detaches a separation operator from the beginning of statement s.
    The operator is not applied at this time.
    """
    x = begins_with_which(SEPARATORS, s)
    return intermediate(as_operator(x), substring(s, len(x)))

def is_separator(x):
    """
    Returns True if x is a separation operator. Returns False otherwise.
    """
    return is_operator(x) and (pvalue(x) in SEPARATORS)

def print_final_term(a):
    """
    Evaluates a single PRINT term, formats the result for printing, and
    appends it to the print buffer. List a contains the term as a collection
    of BASIC data values and operators. The list can be empty, but cannot end
    with a term separator (comma or semicolon).
    """
    if len(a) < 1: return None
    if is_unevaluated(a): a = result(eval_unary_groups(a))
    if is_unevaluated(a): a = result(apply_binary_operators(a))
    if is_unevaluated(a): return set_syntax_error()
    append_to_print_buffer(format_printable(a))
    print_buffer_and_new_line()

def skip_to_print_zone():
    """
    Rapidly advances the cursor to the beginning of the next print zone (tab
    stop, without teletype print-speed restrictions). Inaccurate when the print
    buffer contains special or non-printing characters.
    """
    p = virtual_cursor_position()
    s = PRINT_ZONE_WIDTH - p % PRINT_ZONE_WIDTH
    w = terminal_width()
    if (p + s) < w:
        advance_print_head(s)
    else:
        print_buffer_and_new_line()
    return ''

###############################################################################
# Printing utilities.

def advance_print_head(n):
    """
    Rapidly advances the print head n spaces; in a single movement and without
    actually printing anything (i.e., without teletype effects). This has no
    protection against overshooting the console; wrapping is to be done before
    calling this function.
    """
    # When printed material on the line extends beyond the current cursor
    # position, we have to re-print the whole thing, so as not to overprint
    # anything.
    print_non_empty_buffer()
    k = get_cursor_position()
    p = get_characters_on_line()
    z = substring(p, k, k + n - 1)
    if n > len(z):
        z = z + ' ' * (n - len(z))
    update_characters_on_line(z)
    print(z, end = '')

def print_text(s):
    """
    Concatenates list of strings s to standard output.
    In teletype mode, this goes one character at a time, pausing after each.
    """
    p = character_pause()
    z = ''.join(s)
    if upper_case_out():
        z = z.upper()
    update_characters_on_line(z)
    if p == 0:
        print(z, end = '')
    else:
        for x in z:
            print(x, end = '')
            sys.stdout.flush()
            sleep(p)

def print_buffer_and_new_line():
    """
    Prints the print buffer, empty or not, followed by a newline.
    """
    print_print_buffer()
    print_new_line()

def print_carriage_return():
    """
    Prints a carriage return. Pauses afterward, if in teletype mode.
    """
    print('\r', end = '')
    p = line_pause()
    if p != 0: sys.stdout.flush()
    if p > 0: sleep(p)
    reset_cursor_position()

def print_exit_message():
    """
    Prints the exit message, then immediately deletes it from program memory.
    For use at the very end of a run(), after a program has terminated.
    """
    m = get_exit_message()
    if len(m) > 0:
        print_text(m)
        print_new_line()
    clear_exit_state()

def print_new_line():
    """
    Prints a newline. Pauses afterward, if in teletype mode.
    """
    print()
    p = line_pause()
    if p != 0: sys.stdout.flush()
    if p > 0: sleep(p)
    reset_cursor_position()
    set_no_characters_on_line()

def print_non_empty_buffer():
    """
    Prints the print buffer (sans newline), only if the buffer is non-empty.
    """
    if anything_in_print_buffer(): print_print_buffer()

def print_non_empty_line():
    """
    Prints the print buffer and a newline, only if the buffer is non-empty.
    """
    if anything_in_print_buffer(): print_buffer_and_new_line()

def print_print_buffer():
    """
    Sends the print buffer (even when empty) to standard output, and
    immediately deletes its content (after printing).
    """
    print_text(get_print_buffer())
    clear_print_buffer()

def retract_print_head(n):
    """
    Rapidly retracts the print head n spaces toward, but not beyond, the left
    margin, without teletype effects. We do this the long way, via a carriage
    return and advance_print_head(), so that Python's cursor position is in
    agreement.
    """
    print_non_empty_buffer()
    k = get_cursor_position()
    print('\r', end = '')
    reset_cursor_position()
    advance_print_head(max(0, k - n))

###############################################################################
# Seek user input.

def prompt_for_input(p):
    """
    Present the user with an input prompt, '?', an addenda prompt, '??', or no
    prompt, '', as specified by integer p, and accept one line of input.
    """
    if p == 1:
        a = '? '
    elif p == 2:
        a = '?? '
    else:
        a = ''

    # When a teletype character delay is in effect, we print the buffer first,
    # so that the effect is applied.
    if character_pause() > 0:
        print_print_buffer()
        print_text(a)
        a = input().strip()

    # When no teletype character delay is in effect (and need not be applied),
    # we print the buffer via input's prompt argument.
    else:
        a = ''.join(get_print_buffer() + [a])
        if upper_case_out():
            a = a.upper()
        a = input(a).strip()
        clear_print_buffer()

    reset_cursor_position()
    set_no_characters_on_line()
    return a

def issue_redo_from_start_warning():
    """
    Advise the user of an issue with their input (too much or wrong type; too
    little merely results in the addenda prompt), and that we're doing-over.
    """
    print_text('? Redo from start')
    print_new_line()

###############################################################################
# BASIC programmer's development tools.                                       #
###############################################################################

###############################################################################
# Program listing / checking.

def list_program():
    """
    Prints the current BASIC program to standard output.
    """
    for a in program_listing():
        print(a)

def not_run():
    """
    Prints a listing of unchecked (not wholly checked) lines of the current
    BASIC program, by source file line number. If a line is unchecked, it might
    indicate a problem with the line, or simply that one or more statements on
    it has not yet been reached. Use between repeated calls of run() to verify
    a BASIC program is free of major errors.
    """
    # The unchecked file line numbers, u, are monotonically increasing.
    u = unchecked_file_line_numbers()
    n = len(u)
    if n == 0:
        print('Ok')
        return None
    y = unchecked_lines()
    for v, x in zip(u, y):
        i = floor(log10(u[-1]) - floor(log10(v)))
        print((' ' * i) + '[' + str(v) + '] ' + x)
    print('(' + str(n) + ' unchecked line' + ('s' * (n > 1)) + ')')

###############################################################################
# Case conversion.

def lower_code(p):
    """
    Convert program listing p (a list of strings) to lower case, excepting its
    string literals. Does not modify the original list, p.
    """
    r = p.copy()
    for i in range(len(r)):
        if '"' not in r[i]:
            r[i] = r[i].lower()
        else:
            q = [m.start() for m in re.finditer('"', r[i])]
            u = [-1] + q
            v = [j - 1 for j in q + [len(r[i])]]
            a = [substring(r[i], j, k) for j, k in zip(u, v)]
            for j in range(0, len(a), 2):
                a[j] = a[j].lower()
            r[i] = ''.join(a)
    return r

def upper_code(p):
    """
    Convert program listing p (a list of strings) to upper case, excepting its
    string literals. Does not modify the original list, p.
    """
    r = p.copy()
    for i in range(len(r)):
        if '"' not in r[i]:
            r[i] = r[i].upper()
        else:
            q = [m.start() for m in re.finditer('"', r[i])]
            u = [-1] + q
            v = [j - 1 for j in q + [len(r[i])]]
            a = [substring(r[i], j, k) for j, k in zip(u, v)]
            for j in range(0, len(a), 2):
                a[j] = a[j].upper()
            r[i] = ''.join(a)
    return r

###############################################################################
# Constants                                                                   #
###############################################################################

# These need to come last in this script, because the function references in
# ACTION, BFUN, EXPONENTIATORS, etc., can only be made _after_ loading the
# functions.

###############################################################################
# BASIC-variable initialisation constants.

INITIAL_STRING = ''   # Initial value for a string-type variable.
INITIAL_NUMBER = 0    # Initial value for a number-type variable.
DEFAULT_EXTENT = 10   # Default extent for each dimension of an array.

###############################################################################
# BASIC data-type names.

BASIC_B = 'BASIC_B'   # Break message.
BASIC_E = 'BASIC_E'   # Error message.
BASIC_N = 'BASIC_N'   # Numerical value.
BASIC_O = 'BASIC_O'   # Operator.
BASIC_S = 'BASIC_S'   # Character string.

###############################################################################
# Recognised BASIC keywords (commands).

ACTION = {'CLEAR':  enact_CLEAR,    'DATA':     enact_DATA,
          'DEF':    enact_DEF,      'DELAY':    enact_DELAY,
          'DIM':    enact_DIM,      'END':      enact_END,
          'FN':     enact_FN,       'FOR':      enact_FOR,
          'GO':     enact_GO,       'GOSUB':    enact_GOSUB,
          'GOTO':   enact_GOTO,     'IF':       enact_IF,
          'INPUT':  enact_INPUT,    'LET':      enact_LET,
          'NEXT':   enact_NEXT,     'ON':       enact_ON,
          'PRINT':  enact_PRINT,    'READ':     enact_READ,
          'REM':    enact_REM,      'RESTORE':  enact_RESTORE,
          'RETURN': enact_RETURN,   'STEP':     enact_STEP,
          'STOP':   enact_STOP,     'THEN':     enact_THEN,
          'TO':     enact_TO}

KEYWORDS = tuple(ACTION.keys())

###############################################################################
# BASIC functions.

BFUN = {'ABS':    eval_ABS,     'ASC':  eval_ASC,     'ATN':      eval_ATN,
        'CHR$':   eval_CHR_,    'COS':  eval_COS,     'EXP':      eval_EXP,
        'INSTR':  eval_INSTR,   'INT':  eval_INT,     'LEFT$':    eval_LEFT_,
        'LEN':    eval_LEN,     'LOG':  eval_LOG,     'MID$':     eval_MID_,
        'POS':    eval_POS,     'RND':  eval_RND,     'RIGHT$':   eval_RIGHT_,
        'SGN':    eval_SGN,     'SIN':  eval_SIN,     'SPC':      eval_SPC,
        'SQR':    eval_SQR,     'STR$': eval_STR_,    'STRING$':  eval_STRING_,
        'SYST':   eval_SYST,    'TAB':  eval_TAB,     'TAN':      eval_TAN,
        'TTW':    eval_TTW,     'VAL':  eval_VAL}

FUNCTIONS = tuple(BFUN.keys())

###############################################################################
# BASIC operators and their Python-function implementations.

EXPONENTIATORS  = {'^': eval_RAISE}
ARITH_UNARIES   = {'-': eval_NEGATE, '+': eval_IDENTITY}
MULTIPLIERS     = {'*': eval_MULTIPLY, '/': eval_DIVIDE}
ADDERS          = {'+': eval_ADD, '-': eval_SUBTRACT}
RELATIONALS     = {'=': eval_EQUAL,   '<>': eval_NOT_EQUAL,
                   '>': eval_GREATER, '<=': eval_NOT_GREATER,
                   '<': eval_LESS,    '>=': eval_NOT_LESS}
LOGICAL_UNARIES  = {'NOT': eval_NOT}
LOGICAL_BINARIES = {'AND': eval_AND, 'OR': eval_OR, 'XOR': eval_XOR}

###############################################################################
# Derived tuples of operator groups (names only).

ARITHMETICALS = tuple(list(EXPONENTIATORS.keys())
                      + list(MULTIPLIERS.keys())
                      + list(ADDERS.keys()))
OPERATORS     = tuple(list(ARITHMETICALS)
                      + list(RELATIONALS.keys()))
LOGICALS      = tuple(list(LOGICAL_UNARIES.keys())
                      + list(LOGICAL_BINARIES.keys()))
BINARIES      = tuple(list(OPERATORS)
                      + list(LOGICAL_BINARIES.keys()))

###############################################################################
# BASIC digits (includes .), for detecting numeric literals.

DIGITS = tuple([str(n) for n in range(10)] + ['.'])

###############################################################################
# BASIC letters (upper case).

LETTERS = tuple(ascii_uppercase)

###############################################################################
# Term separators. These symbols delimit individual PRINT terms, expand to
# varying amounts of whitespace when printed, and provide line-continuation by
# instructing BASIC not to append a newline.

SEPARATORS = (';', ',')

###############################################################################
# Formatting constants (tab width, floating point precision).

PRINT_ZONE_WIDTH = 14
PRINT_PRECISION = '{:.6G}'

########################################################################### EOF
