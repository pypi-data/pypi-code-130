import math
import copy
import operator
from pyparsing import *
from pyparsing import ParserElement


class ResultToken(dict):
    """A result token to encapsulate and augment pyparsing parse result items."""

    def __init__(self, m, s, loc, token, is_root=False):
        self._is_root = is_root
        self._marker = m
        self._string = s
        self._location = loc
        self.prop = dict()
        self.value = None
        self._result = token
        if len(token) > 0:
            self.value = token[0]
        if len(token) == 1:
            self.children = []
            if isinstance(token[0], ResultToken):
                self._code = token[0]._code
            else:
                self._code = str(token[0])
        if len(token) > 1:
            self.children = token[1:]
            self._code = ''
            for child in self.children:
                if isinstance(child, ResultToken):
                    self._code += child._code
        for child in token:
            if isinstance(child, ResultToken):
                self.prop[child._marker] = child

    def has(self, marker):
        """Checks if marker is a prop of the token."""
        if marker in self.prop:
            return True
        return False

    def as_list(self):
        # return [item for item in self._result]
        return list(self._result)

    @property
    def list(self):
        return self.as_list()

    def as_dump_list(self):
        out = ''
        for item in self.as_list():
            out += repr(item)
            out += '_\n'
        print(out)

    @property
    def dump_list(self):
        return self.as_dump_list()

    def __getattr__(self, key):
        return self.prop[key]

    # see https://www.peterbe.com/plog/must__deepcopy__
    def __deepcopy__(self, memo):
        token = ResultToken(self._marker, self._string, self._location, [])
        token.prop = self.prop
        token.value = self.value
        token._result = self._result
        return token

    def __len__(self):
        return len(self._result)

    def pprint_tree(self, _prefix="", _last=True, level=0, max_level=0):
        lines = "` " if _last else "|- "
        if isinstance(self.value, ResultToken):
            dump_value = ''
        else:
            dump_value = '({})'.format(self.value.replace('\n', '[newline]'))
        out = '{}{}: {}{}{}\n'.format(_prefix, level, lines, self._marker, dump_value)
        _prefix += "   " if _last else "|  "
        child_count = len(self.prop.keys())
        for i, child in enumerate(self.prop.keys()):
            _last = i == (child_count - 1)
            if max_level == 0 or level < max_level:
                if isinstance(self.prop[child], ResultToken):
                    out += self.prop[child].pprint_tree(_prefix, _last, level+1)
        return out

    @property
    def tree(self):
        print(self.pprint_tree())

    def __repr__(self):
        return self.pprint_tree(max_level=1)

    def __bool__(self):
        if len(self):
            return True
        return False


def named(marker):
    def parse_action_impl(s, loc, toks):
        if len(toks) == 0:
            return None
        return ResultToken(marker, s, loc, toks)
    return parse_action_impl


def patched_call(self, name=None):
    """
    Shortcut for :class:`setResultsName`, with ``listAllMatches=False``.
    If ``name`` is given with a trailing ``'*'`` character, then ``listAllMatches`` will be
    passed as ``True``.
    If ``name` is omitted, same as calling :class:`copy`.
    Example::
        # these are equivalent
        userdata = Word(alphas).setResultsName("name") + Word(nums + "-").setResultsName("socsecno")
        userdata = Word(alphas)("name") + Word(nums + "-")("socsecno")
    """
    if name is not None:
        return self.setParseAction(named(name)).setResultsName(name, listAllMatches=True)
    return self.copy()


ParserElement.__call__ = patched_call


def parse(element, s, parse_all=True):
    res = element.parseString(s, parseAll=parse_all)
    return ResultToken('root', s, 0, res, is_root=True)


exprStack = []

variables = {}


def pushFirst(strg, loc, toks):  # pragma: no cover
    exprStack.append(toks[0])


def pushUMinus(strg, loc, toks):  # pragma: no cover
    for t in toks:
        if t == '-':
            exprStack.append('unary -')
            # ~ exprStack.append( '-1' )
            # ~ exprStack.append( '*' )
        else:
            break


bnf = None


def BNF():  # pragma: no cover
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        # point = Literal(".")
        e = CaselessLiteral("E")
        # ~ fnumber = Combine( Word( "+-"+nums, nums ) +
        # ~ Optional( point + Optional( Word( nums ) ) ) +
        # ~ Optional( e + Word( "+-"+nums, nums ) ) )
        fnumber = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        ident = Word(alphas, alphas + nums + "_$")

        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")

        expr = Forward()
        atom = ((0, None) * minus + (pi | e | fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | Group(lpar + expr + rpar)).setParseAction(pushUMinus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left
        # exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))

        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        bnf = expr
    return bnf


# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = {"+": operator.add,
       "-": operator.sub,
       "*": operator.mul,
       "/": operator.truediv,
       "^": operator.pow}
fn = {"sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "abs": abs,
      "trunc": lambda a: int(a),
      "round": round,
      "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}


def evaluateStack(s):  # pragma: no cover
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack(s)
    if op in "+-*/^":
        op2 = evaluateStack(s)
        op1 = evaluateStack(s)
        return opn[op](op1, op2)
    elif op == "PI":
        return math.pi  # 3.1415926535
    elif op == "E":
        return math.e  # 2.718281828
    elif op in fn:
        return fn[op](evaluateStack(s))
    elif op[0].isalpha():
        if op in variables:
            return variables[op]
        raise Exception("invalid identifier '%s'" % op)
    elif '.' in op:
        return float(op)
    else:
        return int(op)


void_elements = [
    '', 'area', 'base', 'br', 'col', 'command',
    'embed', 'hr', 'img', 'input', 'keygen',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
]

inline_elements = [
    'h1', 'a', 'b', 'strong', 'i', 'em', 'title', 'label', 'button'
]


# general node semantics
ARITH_EXPRESSION = BNF()
COLON = Literal(':')

ALL = Word(printables + ' ' + '\n')('all')
ALL_NO_COLON = Word(printables + ' ', excludeChars=":")('all_no_colon')

UNQUOTED_WORDS = Word(printables + ' ', excludeChars="'{}<>")

DESCRIPTOR = Word(alphanums + '_')
GLYPH = Word('*$&~!+%#@|.', max=1)('glyph')

GLYPH_LINE = Optional(GLYPH) + DESCRIPTOR()('descriptor') + Optional(ALL_NO_COLON)
NAMESPACE_DESCRIPTOR = (Optional(GLYPH)('glyph') + DESCRIPTOR('namespace') + Literal('-') +
                        DESCRIPTOR()('descriptor'))('namespace_descriptor')
EMPTY = Empty()

LIST_ITEM_LINE = Literal('-')('list_item_glyph')
SINGLE_QUOTED_STRING = (QuotedString(quoteChar="'"))('quoted_string')
DOUBLE_QUOTED_STRING = QuotedString(quoteChar='"')
MOUSTACHE = Forward()('moustache')
ATTRIBUTES = Forward()('attributes')
INLINE_CONTENT = Forward()('inline_content')
# MODEL_INSTANTIATION = Forward()('model_instantiation')
TEXT_NODE = Optional(COLON)('colon') + Optional(Literal(' '))('space') + Optional(INLINE_CONTENT.leaveWhitespace())

NUMBER = (Word(nums))('number')
TRANSLATION = Suppress('!') + DESCRIPTOR()('language_code')
PROPERTY_ACCESSOR = (Suppress('.') + Word(alphanums + '_'))('property_accessor')
META_ACCESSOR = (Suppress('&') + Word(alphanums + '_'))('meta_accessor')
# TRANSLATION_ACCESSOR = Suppress('!') + DESCRIPTOR()('translation_descriptor') + ZeroOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')))('properties')
TRANSLATION_ACCESSOR = Suppress('!') + DESCRIPTOR()('translation_descriptor')
MODEL = Literal('+')('glyph') + DESCRIPTOR()('model_descriptor') + Optional(':')
MODEL_ACCESSOR = (Literal('+')('glyph') + DESCRIPTOR()('model_descriptor'))('model_accessor')
MODEL_DEFINITION = (Literal('+')('glyph') + DESCRIPTOR()('descriptor') + Optional(':') +
                    LineEnd())('model_definition')
# FIELD = (Optional(Literal('.')('glyph')) + DESCRIPTOR()('field_descriptor') + Optional(':'))('field')
FIELD_DEFINITION = (Literal('.')('glyph') + DESCRIPTOR()('descriptor') + Literal(':') + LineEnd())('field_definition')
COMPONENT_DESCRIPTOR = Suppress('*') + DESCRIPTOR()('component_descriptor')
CONTEXT_ACCESSOR = Literal('_context')('context_accessor')
CONTEXT_ITEM = Literal('#') + DESCRIPTOR()('context_item')

UID = Combine(Suppress('#') + Word(alphanums, excludeChars='# : .'))('uid')
CLS = Combine(Suppress('.') + Word(alphanums, excludeChars='. : #'))('cls')
CLASSES = ZeroOrMore(CLS)('classes')
ID_CLASSES = (Optional(UID) + CLASSES)('id_classes')
ATTRIBUTE_KEY = Word(alphanums + '_' + '-', excludeChars=": = '")
VALUE_ACCESSOR = Literal('_value')('value_accessor')
LIST = Literal('[]')('list')
DICT = Literal('{}')('dict')
BOOLEAN = (Literal('True') or Literal('False'))('boolean')
LITERAL = (quotedString.addParseAction(removeQuotes) ^ pyparsing_common.number)('literal')
EXPRESSION = Forward()('expression')
ATTRIBUTE_VALUE = Forward()('attribute_value')

code = \
"""
#ciphertext: '
----BEGIN PGP MESSAGE-----

jA0EBwMCKFOWDIApgLLx0o8BOb85gzkxIdVAE3tSIX9R/3yXthBUd5QPemx1Lfiz
pHpjmG/DOKJ1aN9ZwqzksAlgqLTf8UPRG9Ch/MPZoy9Q1R5KJv6QKlMPbn5XHqqo
NW5jSV5g2bX6pcl1FUqbCI9yfyDCw99Rxap01qWXxmlkD7uTp5tL2CFmg3SlDVKb
hAX8YpCjSYNDKlXL56O6rg==
=0C/y
-----END PGP MESSAGE-----
'
"""


# ParserElement.setDefaultWhitespaceChars(" \t")

DATA_NODE_ACCESSOR = (Suppress('#')('glyph') + DESCRIPTOR()('data_node_descriptor'))('data_node_accessor')
SLOT_NODE = Literal('|')('glyph') + DESCRIPTOR()('descriptor')
SLOT_NODE_INLINE = Literal('|')('glyph') + DESCRIPTOR()('descriptor')
RESOURCE_ACCESSOR = (Suppress('@') + DESCRIPTOR()('resource'))('resource_accessor')
ACCESSOR_ITEM = (RESOURCE_ACCESSOR | MODEL_ACCESSOR | DATA_NODE_ACCESSOR |
                 PROPERTY_ACCESSOR | META_ACCESSOR)('accessor_item')
COMBINED_ACCESSOR = \
    OneOrMore(ACCESSOR_ITEM)('combined_accessor')
CID = Combine(Literal('Q') + DESCRIPTOR()('cid'))
SEGMENT = (DATA_NODE_ACCESSOR |
           MODEL |
           META_ACCESSOR |
           CONTEXT_ITEM |
           OneOrMore(PROPERTY_ACCESSOR)('properties'))
FULL_PATH = Optional(CID('resource')) + OneOrMore(SEGMENT.setParseAction(named('segment')))('segments')  # noqa
MOUSTACHE_EXPRESSION = MODEL ^ RESOURCE_ACCESSOR ^ CONTEXT_ACCESSOR ^ COMBINED_ACCESSOR ^ CONTEXT_ITEM ^ COMPONENT_DESCRIPTOR
MOUSTACHE_ATTRIBUTE_VALUE = NUMBER | SINGLE_QUOTED_STRING | MOUSTACHE_EXPRESSION
MOUSTACHE_ATTRIBUTE = ATTRIBUTE_KEY('moustache_attribute_key') + Optional(Literal('=') + MOUSTACHE_ATTRIBUTE_VALUE('moustache_attribute_value'))
MOUSTACHE_ATTRIBUTES = ZeroOrMore(MOUSTACHE_ATTRIBUTE('moustache_attribute'))
FRAMEWORK_COMPONENT = Suppress('*core-') + DESCRIPTOR()('framework_component') + MOUSTACHE_ATTRIBUTES('moustache_attributes')
MOUSTACHE << Suppress('{') + EXPRESSION + Suppress('}')
SINGLE_QUOTED_MOUSTACHE = (Suppress("'") + MOUSTACHE + Suppress("'"))('quoted_moustache')
DOUBLE_QUOTED_MOUSTACHE = Suppress('"') + MOUSTACHE + Suppress('"')
# MODEL_INSTANTIATION = (Literal('+') + DESCRIPTOR('descriptor') + Optional(INLINE_CONTENT.leaveWhitespace() ^
ARGUMENT_EXPRESSION = (
    BOOLEAN ^ LITERAL ^ LIST ^ DICT ^ VALUE_ACCESSOR ^ FRAMEWORK_COMPONENT
    ^ RESOURCE_ACCESSOR
    ^ COMBINED_ACCESSOR ^ CONTEXT_ITEM
    ^ MODEL ^ COMPONENT_DESCRIPTOR ^ ARITH_EXPRESSION('arith_expression')
    ^ TRANSLATION_ACCESSOR('translation_accessor'))
ARGUMENT = (INLINE_CONTENT.leaveWhitespace() ^ ARGUMENT_EXPRESSION)('argument')
ATTRIBUTE_VALUE << (SINGLE_QUOTED_MOUSTACHE | NUMBER | SINGLE_QUOTED_STRING | EXPRESSION)('attribute_value')
KEYWORD_ARGUMENT = Suppress('#') + ATTRIBUTE_KEY('attribute_key') + Literal('=') + ATTRIBUTE_VALUE
# MODEL_INSTANTIATION = (Literal('+') + DESCRIPTOR('descriptor') + ZeroOrMore(ARGUMENT) + ZeroOrMore(KEYWORD_ARGUMENT))('model_instantiation')

MODEL_INSTANTIATION = (Literal('+') + DESCRIPTOR('descriptor') + ZeroOrMore(ARGUMENT)('arguments') +
                       ZeroOrMore(KEYWORD_ARGUMENT)('keyword_arguments'))('model_instantiation')

EXPRESSION << (
    BOOLEAN ^ LITERAL ^ LIST ^ DICT ^ VALUE_ACCESSOR ^ FRAMEWORK_COMPONENT ^ MODEL_INSTANTIATION
    ^ RESOURCE_ACCESSOR
    ^ COMBINED_ACCESSOR ^ CONTEXT_ITEM
    ^ MODEL ^ COMPONENT_DESCRIPTOR ^ ARITH_EXPRESSION('arith_expression')
    ^ TRANSLATION_ACCESSOR('translation_accessor'))

INLINE_SEMANTIC_ATTRIBUTE_VALUE = DOUBLE_QUOTED_MOUSTACHE('quoted_moustache') | NUMBER | DOUBLE_QUOTED_STRING('quoted_string') | EXPRESSION
ATTRIBUTE = (ATTRIBUTE_KEY('attribute_key') + Optional(Suppress('=') + ATTRIBUTE_VALUE))('attribute')
INLINE_SEMANTIC_ATTRIBUTE = ATTRIBUTE_KEY('attribute_key') + Optional(Suppress('=') + INLINE_SEMANTIC_ATTRIBUTE_VALUE('attribute_value'))
INLINE_SEMANTICS_ATTRIBUTES = ZeroOrMore(INLINE_SEMANTIC_ATTRIBUTE('attribute'))
INLINE_SEMANTICS_CONTENT = ZeroOrMore(UNQUOTED_WORDS.leaveWhitespace())('inline_semantic_content_words') | TRANSLATION_ACCESSOR('translation_accessor') | MOUSTACHE
INLINE_SEMANTICS_ELEMENT = DESCRIPTOR()('descriptor') + Optional(' ') + ID_CLASSES + Optional(' ')
INLINE_SEMANTICS_ELEMENT += Optional(INLINE_SEMANTICS_ATTRIBUTES)('attributes') + Optional(' ')
INLINE_SEMANTICS_ELEMENT += Optional(COLON)('colon') + Suppress(Optional(' ')) + INLINE_SEMANTICS_CONTENT('inline_semantics_content')

INLINE_SEMANTICS = Suppress('<') + INLINE_SEMANTICS_ELEMENT('inline_semantics_element') + Optional(' ') + Suppress('>') + Optional(' ')('trailing_space')

INLINE_CONTENT_SEGMENT = (OneOrMore(LineEnd())('inline_content_newlines_prefix') | (
    INLINE_SEMANTICS.leaveWhitespace()('inline_semantics') + Optional(LineEnd())('inline_content_newlines_trailing')
    ^ UNQUOTED_WORDS.leaveWhitespace()('inline_content_words') + Optional(LineEnd())('inline_content_newlines_trailing')
    ^ EMPTY() + LineEnd()('inline_content_newlines_trailing')
    ^ MOUSTACHE()('moustache') + Optional(LineEnd())('inline_content_newlines_trailing')
))('inline_content_segment')

INLINE_CONTENT << \
    ((Suppress("'")  # + ZeroOrMore(LineEnd())('inline_content_newlines')
      + OneOrMore(INLINE_CONTENT_SEGMENT)('inline_content_segments') + Suppress("'")) | SLOT_NODE_INLINE('slot_node'))('inline_content')
ATTRIBUTES << Optional(ZeroOrMore(ATTRIBUTE))('attributes')

# instruction semantics
FILENAME = DESCRIPTOR()('filename')
URL = Word(printables, excludeChars='* "  : # { }' + "'")

RESOURCE = Suppress('@') + DESCRIPTOR()('resource') + COLON + "'" + (URL | DESCRIPTOR)('source') + "'"

INHERIT = Literal('%')('glyph') + Literal('inherit')('instruction')
INHERIT += FILENAME('documentfile') | RESOURCE_ACCESSOR

IMPORT = Literal('%')('glyph') + Literal('import')('instruction')
IMPORT += FILENAME('documentfile') | RESOURCE_ACCESSOR('resource_accessor')

INCLUDE = Literal('%')('glyph') + Literal('include')('instruction')
INCLUDE += FILENAME('documentfile')

NAMESPACE = Literal('%')('glyph') + Literal('namespace')('instruction')
NAMESPACE += DESCRIPTOR()('namespace') + '=' + URL

INSTRUCTION = INHERIT | IMPORT | INCLUDE | NAMESPACE


# route semantics
url_chars = alphanums + '-_.~%+'
PATH_SEGMENT = Word(url_chars)
PATH_VARIABLE = Suppress('{') + DESCRIPTOR()('variable_descriptor') + Suppress('}')
PATH_ITEM = Suppress(Optional('/'))('leading_slash') + (PATH_SEGMENT.setParseAction(named('path_segment')) | PATH_VARIABLE.setParseAction(named('path_variable')))
PATH_ITEMS = ZeroOrMore(PATH_ITEM('path_item'))
ROUTE_PATH = PATH_ITEMS('path_items')
ROUTE_PATH += Optional('/')('trailing_slash')
ROUTE = DESCRIPTOR()('descriptor') + COLON + Optional(' ') + Suppress("'") + ROUTE_PATH('route_path') + Suppress("'")


# code semantics
SOMETHING = Suppress('%') + Word(printables + ' ')('some_thing')
ITERATOR = COMBINED_ACCESSOR | CONTEXT_ITEM | DATA_NODE_ACCESSOR
IF_STATEMENT = Suppress('%') + Suppress('if') + EXPRESSION + Suppress(':')
FOR_LOOP = Suppress('%') + Suppress('for') + DESCRIPTOR()('variable') + Suppress('in')
FOR_LOOP += ITERATOR('iterator') + Suppress(':')
CODE = INHERIT | IMPORT | INCLUDE | NAMESPACE | IF_STATEMENT('if_statement') | FOR_LOOP('for_loop') | SOMETHING('some_thing')

COMPONENT_CALL_BODY = DESCRIPTOR()('namespace') - Suppress('-') - DESCRIPTOR()('component_descriptor')
COMPONENT_CALL = COMPONENT_CALL_BODY + ZeroOrMore(ATTRIBUTE)('attributes')
COMPONENT_CALL += Optional(COLON)('colon') + Optional(' ') + Optional(INLINE_CONTENT.leaveWhitespace() ^ EXPRESSION)
EGG = Optional(ALL_NO_COLON('node_key')) + Optional(COLON)('colon') + Optional(ALL('node_value'))

# list items
LIST_ITEM = Literal('-')('list_item_glyph') + Optional(" ") + Optional(INLINE_CONTENT.leaveWhitespace())

# ASSIGNMENT_VALUE = Optional(EXPRESSION ^ INLINE_CONTENT.leaveWhitespace())
ASSIGNMENT_VALUE = (EXPRESSION ^ INLINE_CONTENT.leaveWhitespace())('assignment_value')
# ASSIGNMENT = (Optional(GLYPH) + DESCRIPTOR()('descriptor') + COLON('colon') + Optional(' ') +
ASSIGNMENT = (GLYPH + DESCRIPTOR()('descriptor') + COLON('colon') + Optional(' ') +
              ASSIGNMENT_VALUE)('assignment')
# we have to definde DATA_NODE_VALUE containig INLINE_CONTENT here (not using Forward definition for INLINE_CONTENT,
# because using Forward definition seem to cause missing items in named label "inline_content" in parseResults

DATA_NODE_EXPRESSION = copy.copy(EXPRESSION)

DATA_NODE_VALUE = Optional(DATA_NODE_EXPRESSION.addParseAction(named('expression'))('expression') ^ INLINE_CONTENT.leaveWhitespace())

DATA_NODE = \
Literal('#')('glyph') \
+ DESCRIPTOR()('data_node_descriptor') \
+ COLON.addParseAction(named('colon'))('colon') \
+ Optional(' ').addParseAction(named('space'))('space') \
+ DATA_NODE_VALUE.addParseAction(named('data_node_value'))('data_node_value')

EDITOR_LINE = DATA_NODE | ASSIGNMENT

# reintroduce newline to whitespace after last usage of INLINE_CONTENT, as INLINE_CONTENT is the only place where we use newlines in syntax
# ParserElement.setDefaultWhitespaceChars(" \n\t")

URL_PATH_VARIABLE = Suppress('{') + DESCRIPTOR()('descriptor') + Suppress('}')
URL_PATH = Suppress(Optional('/')) + ZeroOrMore(DESCRIPTOR()('segment') + Suppress(Optional('/')))('segments')
url_chars = alphanums + '-_.~%+'
fragment = Combine((Suppress('#') + Word(url_chars)))('fragment')
scheme = oneOf('http https ftp file')('scheme')
host = Combine(delimitedList(Word(url_chars), '.'))('host')
port = Suppress(':') + Word(nums)('port')
user_info = (Word(url_chars)('username') + Suppress(':') + Word(url_chars)('password') + Suppress('@'))

query_pair = Group(Word(url_chars) + Suppress('=') + Word(url_chars))
query = Group(Suppress('?') + delimitedList(query_pair, '&'))('query')

path = Combine(Suppress('/') + OneOrMore(~query + Word(url_chars + '/')))('path') + Optional(query) + Optional(fragment)

url_parser = (Optional(path) + Optional(query) + Optional(fragment))

# ELEMENT = Optional(GLYPH) + Optional(DESCRIPTOR()('descriptor') ^ NAMESPACE_DESCRIPTOR) + ID_CLASSES
COMPONENT_DEFINITION = (Literal('*') + (DESCRIPTOR()('descriptor') ^ NAMESPACE_DESCRIPTOR) +
                        ZeroOrMore(Suppress('#') + DESCRIPTOR)('arguments') +
                        ZeroOrMore(KEYWORD_ARGUMENT)('keyword_arguments'))('component_definition')

ELEMENT = (MODEL_DEFINITION | FIELD_DEFINITION | ASSIGNMENT | COMPONENT_DEFINITION | Optional(GLYPH) + Optional((DESCRIPTOR()('descriptor') ^ NAMESPACE_DESCRIPTOR) + ID_CLASSES + ATTRIBUTES))
# ELEMENT += ATTRIBUTES + Optional(COLON)('colon') + Optional(' ')
# TODO: remove this Optional from colon and make parser elements with explicit colon and explicit missing colonb
# in order to differentiate between defitinitions and accessors
ELEMENT += Optional(COLON)('colon') + Optional(' ')
ELEMENT += Optional(INLINE_CONTENT.leaveWhitespace()) ^ EXPRESSION

LINE = LIST_ITEM_LINE | ((NAMESPACE_DESCRIPTOR | INSTRUCTION) ^ ELEMENT)
BEGIN_MULTILINE_STRING = Combine(ALL_NO_COLON + COLON + Optional(' ') + Literal("'") + LineEnd())
END_MULTILINE_STRING = Literal("'") + LineEnd()
