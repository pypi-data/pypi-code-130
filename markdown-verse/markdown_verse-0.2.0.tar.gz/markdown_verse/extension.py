import re
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor


TAG = 'div'
CLASS = 'verse'


class VerseExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'tag': [TAG,
                'The tag name used to wrap the verse block'],
            'tag_class': [CLASS,
                'The CSS class used on that tag'],
        }
        super(VerseExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            VerseProcessor(
                self.getConfig('tag'),
                self.getConfig('tag_class'),
                md.parser),
            'verse', 175)


class VerseProcessor(BlockProcessor):

    VERSE_RE = re.compile(r'''(^|\n)(?P<quotes>'{3})\n(?P<body>.*?)\n(?P=quotes)($|\n)''',
                          re.DOTALL | re.MULTILINE)
    START_RE = re.compile(r'''(^|\n)'{3}''', re.DOTALL | re.MULTILINE)
    QUOTES_RE = re.compile(r'''\n?'{3}\n?''')
    def __init__(self, tag, tag_class, *args, **kwargs):
        self.tag = tag
        self.tag_class = tag_class
        self.in_verse = False
        self.curr_verse = None
        super().__init__(*args, **kwargs)

    def test(self, parent, block):
        return self.in_verse or self.START_RE.search(block)

    def run(self, parent, blocks):
        was_in_verse = self.in_verse
        single_stanza = False
        sibling = self.lastChild(parent)
        block = blocks.pop(0)
        if block.endswith("'''"):
            if self.in_verse:
                self.in_verse = False
            else:
                single_stanza = True
        block = self.QUOTES_RE.sub('', block)
        if block:
            if not was_in_verse:
                el = etree.SubElement(parent, self.tag)
                el.text = ''
                if self.tag_class:
                    el.set('class', self.tag_class)
                if not single_stanza:
                    self.in_verse = True
            else:
                el = sibling
                el.text += '\n\n'
            el.text += block

def makeExtension(**kwargs):
    return VerseExtension(**kwargs)
