# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_process.ipynb.

# %% auto 0
__all__ = ['langs', 'nb_lang', 'first_code_ln', 'extract_directives', 'opt_set', 'instantiate', 'NBProcessor']

# %% ../nbs/03_process.ipynb 2
from .read import *
from .maker import *
from .imports import *

from execnb.nbio import *
from fastcore.script import *
from fastcore.imports import *
from fastcore.xtras import *

from collections import defaultdict
from pprint import pformat
from inspect import signature,Parameter
import ast,contextlib,copy
from collections import defaultdict

# %% ../nbs/03_process.ipynb 6
# from https://github.com/quarto-dev/quarto-cli/blob/main/src/resources/jupyter/notebook.py
langs = defaultdict(
    lambda: '#',  r = "#", python = "#", julia = "#", scala = "//", matlab = "%", csharp = "//", fsharp = "//",
    c = ["/*","*/"], css = ["/*","*/"], sas = ["*",";"], powershell = "#", bash = "#", sql = "--", mysql = "--", psql = "--",
    lua = "--", cpp = "//", cc = "//", stan = "#", octave = "#", fortran = "!", fortran95 = "!", awk = "#", gawk = "#", stata = "*",
    java = "//", groovy = "//", sed = "#", perl = "#", ruby = "#", tikz = "%", javascript = "//", js = "//", d3 = "//", node = "//",
    sass = "//", coffee = "#", go = "//", asy = "//", haskell = "--", dot = "//", apl = "⍝")

# %% ../nbs/03_process.ipynb 7
def nb_lang(nb): return nested_attr(nb, 'metadata.kernelspec.language', 'python')

# %% ../nbs/03_process.ipynb 9
def _dir_pre(lang=None): return fr"\s*{langs[lang]}\s*\|"
def _quarto_re(lang=None): return re.compile(_dir_pre(lang) + r'\s*[\w|-]+\s*:')

# %% ../nbs/03_process.ipynb 11
def _directive(s, lang='python'):
    s = re.sub('^'+_dir_pre(lang), f"{langs[lang]}|", s)
    if ':' in s: s = s.replace(':', ': ')
    s = (s.strip()[2:]).strip().split()
    if not s: return None
    direc,*args = s
    return direc,args

# %% ../nbs/03_process.ipynb 12
def _norm_quarto(s, lang='python'):
    "normalize quarto directives so they have a space after the colon"
    m = _quarto_re(lang).match(s)
    return m.group(0) + ' ' + _quarto_re(lang).sub('', s).lstrip() if m else s

# %% ../nbs/03_process.ipynb 14
def first_code_ln(code_list, re_pattern=None, lang='python'):
    if re_pattern is None: re_pattern = _dir_pre(lang)
    "get first line number where code occurs, where `code_list` is a list of code"
    return first(i for i,o in enumerate(code_list) if o.strip() != '' and not re.match(re_pattern, o))

# %% ../nbs/03_process.ipynb 16
def extract_directives(cell, remove=True, lang='python'):
    "Take leading comment directives from lines of code in `ss`, remove `#|`, and split"
    if cell.source:
        ss = cell.source.splitlines(True)
        first_code = first_code_ln(ss, lang=lang)
        if not ss or first_code==0: return {}
        pre = ss[:first_code]
        if remove:
            # Leave Quarto directives in place for later processing
            cell['source'] = ''.join([_norm_quarto(o, lang) for o in pre if _quarto_re(lang).match(o)] + ss[first_code:])
        return dict(L(_directive(s, lang) for s in pre).filter())

# %% ../nbs/03_process.ipynb 20
def opt_set(var, newval):
    "newval if newval else var"
    return newval if newval else var

# %% ../nbs/03_process.ipynb 21
def instantiate(x, **kwargs):
    "Instantiate `x` if it's a type"
    return x(**kwargs) if isinstance(x,type) else x

def _mk_procs(procs, nb): return L(procs).map(instantiate, nb=nb)

# %% ../nbs/03_process.ipynb 22
def _is_direc(f): return getattr(f, '__name__', '-')[-1]=='_'

# %% ../nbs/03_process.ipynb 23
class NBProcessor:
    "Process cells and nbdev comments in a notebook"
    def __init__(self, path=None, procs=None, preprocs=None, postprocs=None, nb=None, debug=False, rm_directives=True, process=False):
        self.nb = read_nb(path) if nb is None else nb
        self.lang = nb_lang(self.nb)
        for cell in self.nb.cells: cell.directives_ = extract_directives(cell, remove=rm_directives, lang=self.lang)
        self.procs,self.preprocs,self.postprocs = map_ex((procs,preprocs,postprocs), _mk_procs, nb=self.nb)
        self.debug,self.rm_directives = debug,rm_directives
        if process: self.process()

    def _process_cell(self, cell):
        self.cell = cell
        cell.nb = self.nb
        for proc in self.procs:
            if not hasattr(cell,'source'): return
            if not hasattr(cell, 'directives_'):
                cell.nb=None
                raise Exception(cell)
            if cell.cell_type=='code' and cell.directives_:
                for cmd,args in cell.directives_.items():
                    self._process_comment(proc, cell, cmd, args)
                    if not hasattr(cell,'source'): return
            if callable(proc) and not _is_direc(proc):
                cell = opt_set(cell, proc(cell))
#                 try: cell = opt_set(cell, proc(cell))
#                 except:
#                     cell.nb = None
#                     raise Exception((proc,cell))
        cell.nb = None

    def _process_comment(self, proc, cell, cmd, args):
        if _is_direc(proc) and getattr(proc, '__name__', '-')[:-1]==cmd: f=proc
        else: f = getattr(proc, f'_{cmd}_', None)
        if not f: return
        if self.debug: print(cmd, args, f)
        return f(self, cell, *args)
        
    def process(self):
        "Process all cells with `process_cell`"
        for proc in self.preprocs:
            self.nb = opt_set(self.nb, proc(self.nb))
            for i,cell in enumerate(self.nb.cells): cell.idx_ = i
        for cell in self.nb.cells: self._process_cell(cell)
        for proc in self.postprocs: self.nb = opt_set(self.nb, proc(self.nb))
        self.nb.cells = [c for c in self.nb.cells if c and getattr(c,'source',None) is not None]
