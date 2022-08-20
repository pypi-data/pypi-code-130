##
## This is file `sagetexparse.py',
## generated with the docstrip utility.
##
## The original source files were:
##
## scripts.dtx  (with options: `parsermod')
## 
## This is a generated file. It is part of the SageTeX package.
## 
## Copyright (C) 2008--2015 by Dan Drake <dr.dan.drake@gmail.com>
## 
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by the
## Free Software Foundation, either version 2 of the License, or (at your
## option) any later version.
## 
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
## Public License for more details.
## 
## You should have received a copy of the GNU General Public License along
## with this program.  If not, see <http://www.gnu.org/licenses/>.
## 
import sys
import os
import textwrap
from pyparsing import *
def skipToMatching(opener, closer):
  nest = nestedExpr(opener, closer)
  return originalTextFor(nest)

curlybrackets = skipToMatching('{', '}')
squarebrackets = skipToMatching('[', ']')
sagemacroparser = r'\sage' + curlybrackets('code')
sagestrmacroparser = r'\sagestr' + curlybrackets('code')
sageplotparser = (r'\sageplot'
                 + Optional(squarebrackets)('opts')
                 + Optional(squarebrackets)('format')
                 + curlybrackets('code'))
sagetexpause = Literal(r'\sagetexpause')
sagetexunpause = Literal(r'\sagetexunpause')
class SoutParser():
  def __init__(self, fn):
    self.label = []
    parselabel = (r'\newlabel{@sageinline'
                 + Word(nums)('num')
                 + '}{'
                 + curlybrackets('result')
                 + '{}{}{}{}}')
    parselabel.ignore('%' + restOfLine)
    parselabel.setParseAction(self.newlabel)
    try:
      OneOrMore(parselabel).parseFile(fn)
    except IOError:
      print('Error accessing {}; exiting. Does your .sout file exist?'.format(fn))
      sys.exit(1)
  def newlabel(self, s, l, t):
    self.label.append(t.result[1:-1])
class DeSageTex():
  def __init__(self, texfn, soutfn):
    self.sagen = 0
    self.plotn = 0
    self.fn = os.path.basename(texfn)
    self.sout = SoutParser(soutfn)
    strmacro = sagestrmacroparser
    smacro = sagemacroparser
    smacro.setParseAction(self.sage)
    strmacro.setParseAction(self.sage)
    usepackage = (r'\usepackage'
                 + Optional(squarebrackets)
                 + '{sagetex}')
    usepackage.setParseAction(replaceWith(r"""% "\usepackage{sagetex}" line was here:
\RequirePackage{verbatim}
\RequirePackage{graphicx}
\newcommand{\sagetexpause}{\relax}
\newcommand{\sagetexunpause}{\relax}"""))
    splot = sageplotparser
    splot.setParseAction(self.plot)
    beginorend = oneOf('begin end')
    blockorverb = 'sage' + oneOf('block verbatim')
    blockorverb.setParseAction(replaceWith('verbatim'))
    senv = '\\' + beginorend + '{' + blockorverb + '}'
    silent = Literal('sagesilent')
    silent.setParseAction(replaceWith('comment'))
    ssilent = '\\' + beginorend + '{' + silent + '}'
    stexindent = Suppress(r'\setlength{\sagetexindent}' + curlybrackets)
    doit = smacro | senv | ssilent | usepackage | splot | stexindent |strmacro
    doit.ignore('%' + restOfLine)
    doit.ignore(r'\begin{verbatim}' + SkipTo(r'\end{verbatim}'))
    doit.ignore(r'\begin{comment}' + SkipTo(r'\end{comment}'))
    doit.ignore(r'\sagetexpause' + SkipTo(r'\sagetexunpause'))
    str = ''.join(open(texfn, 'r').readlines())
    self.result = doit.transformString(str)
  def sage(self, s, l, t):
    self.sagen += 1
    return self.sout.label[self.sagen - 1]
  def plot(self, s, l, t):
    self.plotn += 1
    if len(t.opts) == 0:
      opts = r'[width=.75\textwidth]'
    else:
      opts = t.opts[0]
    return (r'\includegraphics%s{sage-plots-for-%s.tex/plot-%s}' %
      (opts, self.fn, self.plotn - 1))
class SageCodeExtractor():
  def __init__(self, texfn, inline=True):
    smacro = sagemacroparser
    smacro.setParseAction(self.macroout)

    splot = sageplotparser
    splot.setParseAction(self.plotout)
    env_names = oneOf('sageblock sageverbatim sagesilent')
    senv = r'\begin{' + env_names('env') + '}' + SkipTo(
           r'\end{' + matchPreviousExpr(env_names) + '}')('code')
    senv.leaveWhitespace()
    senv.setParseAction(self.envout)

    spause = sagetexpause
    spause.setParseAction(self.pause)

    sunpause = sagetexunpause
    sunpause.setParseAction(self.unpause)

    if inline:
        doit = smacro | splot | senv | spause | sunpause
    else:
        doit = senv | spause | sunpause
    doit.ignore('%' + restOfLine)

    str = ''.join(open(texfn, 'r').readlines())
    self.result = ''

    doit.transformString(str)

  def macroout(self, s, l, t):
    self.result += '#> \\sage{} from line %s\n' % lineno(l, s)
    self.result += textwrap.dedent(t.code[1:-1]) + '\n\n'

  def plotout(self, s, l, t):
    self.result += '#> \\sageplot{} from line %s:\n' % lineno(l, s)
    if t.format != '':
      self.result += '#> format: %s' % t.format[0][1:-1] + '\n'
    self.result += textwrap.dedent(t.code[1:-1]) + '\n\n'

  def envout(self, s, l, t):
    self.result += '#> %s environment from line %s:' % (t.env,
      lineno(l, s))
    self.result += textwrap.dedent(''.join(t.code)) + '\n'

  def pause(self, s, l, t):
    self.result += ('#> SageTeX (probably) paused on input line %s.\n\n' %
                    (lineno(l, s)))

  def unpause(self, s, l, t):
    self.result += ('#> SageTeX (probably) unpaused on input line %s.\n\n' %
                    (lineno(l, s)))

