
from emora_stdm import Macro
from emora_stdm.state_transition_dialogue_manager.macros_common import IsPlural

class ChildrenLogic(Macro):

    def __init__(self):
        self.isplural = IsPlural().run

    def run(self, ngrams, vars, args):
        if 'children' in vars and vars['children']:
            s = vars['children']
            for entry in s:
                if self.isplural(None, None, [entry]):
                    vars['multiple_children'] = 'True'
            if 'boy' in s and 'girl' in s \
                    or 'baby' in s and 'toddler' in s \
                    or 'toddler' in s and 'teenager' in s:
                vars['multiple_children'] = 'True'


macros = {
    'CHILDREN': ChildrenLogic(),
}