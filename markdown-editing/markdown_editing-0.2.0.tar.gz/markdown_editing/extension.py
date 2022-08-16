import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


COMMENT_RE = r'''
(                                # Whole comment block
\((?P<comment>(                  # A comment containing
    (?<=\\)[()]                  #   Any escaped paren
    |                            #   or
    [^()]                        #   Any non-paren
)+                               #   one or more
)                                # End of comment
(\ \(                            # Whole attribution block
(?P<attribution>                 # An attribution of e.g: a name containing
    [^()]+?                      #   one or more non-parens non-greedy
)                                # End attribution name
(                                # Either
\ (?P<date>                      # A date containing
\d\d\d\d-\d\d-\d\d)              #   YYYY-MM-DD)
)?                               # End either
\))?                             # End of attribution (optional)
\))?                             # End of comment (optional)
'''

TYPE_MAP = {
    '+': 'addition',
    '-': 'deletion',
    '~': 'substitution',
    '?': 'selected',
    '!': 'comment',
    'c': 'comment',
    'a': 'attribution',
    'd': 'date',
}



class EditingExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'type_map': [
                TYPE_MAP,
                'dict mapping edit type to css class ("c", "a", and "d" entries'
                ' map to comment, attribution, and date segments)'],
        }
        super(EditingExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        type_map = self.getConfig('type_map')
        comment_item_processor = CommentItemProcessor(type_map, md)
        md.inlinePatterns.register(comment_item_processor, 'commentitemedit', 75)
        single_item_processor = SingleItemProcessor(type_map, md)
        md.inlinePatterns.register(single_item_processor, 'singleitemedit', 75)
        dual_item_processor = DualItemProcessor(type_map, md)
        md.inlinePatterns.register(dual_item_processor, 'dualitemedit', 75)


def makeExtension(**kwargs):
    return EditingExtension(**kwargs)


class CommentItemProcessor(InlineProcessor):
    RE = r'''(?x)
    (?P<item>           # The item block
    (?P<type>!)\{       # An item
    (?P<contents> (     # containing
        (?<=\\)[{}]     #   Any escaped close brace
        |               #   or
        [^}]            #   Any non-brace
    )+)                 #   One or more
    \}                  # End of item
    (\(               # Whole attribution block
    (?P<attribution>    # An attribution of e.g: a name containing
        [^()]+?         #   one or more non-parens non-greedy
    )                   # End attribution name
    (                   # And maybe
    \ (?P<date>         # A date containing
    \d\d\d\d-\d\d-\d\d) #   YYYY-MM-DD)
    )?                  # End maybe
    \))?                # End of attribution (optional)
    )                   # End of item block
    '''

    def __init__(self, type_map, *args, **kwargs):
        self.type_map = type_map
        super(CommentItemProcessor, self).__init__(self.RE, *args, **kwargs)

    def handleMatch(self, match, data):
        el = etree.Element(
            'q',
            attrib={'class': self.type_map[match.group('type')]})
        el.text = match.group('contents')
        if match.group('attribution') is not None:
            a = etree.SubElement(
                el,
                'span',
                attrib={'class': self.type_map['a']})
            a.text = match.group('attribution')
        if match.group('date') is not None:
            d = etree.SubElement(
                el,
                'span',
                attrib={'class': self.type_map['d']})
            d.text = match.group('date')
        return el, match.start('item'), match.end('item')

class SingleItemProcessor(InlineProcessor):
    RE = r'''(?x)
    (?P<item>           # The item block
    (?P<type>[-+?])\{  # An item
    (?P<contents> (     # containing
        (?<=\\)[{}]     #   Any escaped close brace
        |               #   or
        [^}]            #   Any non-brace
    )+)                 #   One or more
    \}?                  # End of item
    ''' + COMMENT_RE + ')'
    
    def __init__(self, type_map, *args, **kwargs):
        self.type_map = type_map
        super(SingleItemProcessor, self).__init__(self.RE, *args, **kwargs)

    def handleMatch(self, match, data):
        tag = 'mark'
        if match.group('type') == '+':
            tag = 'ins'
        if match.group('type') == '-':
            tag = 'del'
        el = etree.Element(
            tag, 
            attrib={'class': self.type_map[match.group('type')]})
        el.text = match.group('contents')
        comment = _build_comment(match, self.type_map)
        if comment is not None:
            el.append(comment)
        return el, match.start('item'), match.end('item')


class DualItemProcessor(InlineProcessor):
    RE = r'''(?x)
    (?P<item>
    (?P<type>~)\{    # A substitution (deletion first)
    (?P<deletion> (  # deletion containing
        (?<=\\)[{}]  #   Any escaped close brace
        |            #   or
        [^}]         #   Any non-brace
    )+)              #   One or more
    \}               # End of deletion
    \{               # (then substitution)
    (?P<addition> (  # addition containing
        (?<=\\)[{}]  #   Any escaped close brace
        |            #   or
        [^}]         #   Any non-brace
    )+)              #   One or more
    \}               # End of deletion
    ''' + COMMENT_RE + ')'
    
    def __init__(self, type_map, *args, **kwargs):
        self.type_map = type_map
        super(DualItemProcessor, self).__init__(self.RE, *args, **kwargs)

    def handleMatch(self, match, data):
        el = etree.Element(
            'span',
            attrib={'class': self.type_map['~']})
        d = etree.SubElement(el, 'del')
        d.text = match.group('deletion')
        i = etree.SubElement(el, 'ins')
        i.text = match.group('addition')
        comment = _build_comment(match, self.type_map)
        if comment is not None:
            el.append(comment)
        return el, match.start('item'), match.end('item')


def _build_comment(match, type_map):
    if match.group('type') != '!' and match.group('comment') is not None:
        el = etree.Element(
            'q',
            attrib={'class': type_map['c']})
        el.text = match.group('comment').strip()
        if match.group('attribution') is not None:
            a = etree.SubElement(
                el,
                'span',
                attrib={'class': type_map['a']})
            a.text = match.group('attribution')
        if match.group('date') is not None:
            d = etree.SubElement(
                el,
                'span',
                attrib={'class': type_map['d']})
            d.text = match.group('date')
        return el
    else:
        return None
