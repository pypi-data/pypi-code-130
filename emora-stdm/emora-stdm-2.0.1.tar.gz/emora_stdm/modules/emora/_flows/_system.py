
from emora._flows.school import school as school2
from emora._flows.baby import baby
from emora._flows.backstory import backstory
from emora._flows.competition import competition
from emora._flows.house import house
from emora._flows.world import world
from emora._flows.work import work
from emora._flows.sibling import sibling
from emora._flows.relationships import relationships
from emora._flows.coronavirus import coronavirus
from emora._flows.animals import animals
from emora._flows.hobbies_and_activity import hobby
from emora._flows.vacations import df as vacations
from emora._flows.teleportation import teleportation
from emora._flows.movies_return import movies_return
from emora._flows.pets_return import component as pets_return
from emora._flows.coronavirus_final import coronavirus_final

from _globals import PATHDIR
from emora_stdm import CompositeDialogueFlow,DialogueFlow,Macro
from emora_stdm.state_transition_dialogue_manager.macros_common import _term_op_term
import emora_stdm
from emora._flows._global_nlu import personal_nlu, global_update_rules, contraction_rule
from emora._flows._macros import macros
from emora._flows._central_knowledge import central_knowledge

flow_components = {
    'school_new': school2,
    'baby': baby,
    'house': house,
    'competition': competition,
    'backstory': backstory,
    'world': world,
    'worklife': work,
    'sibling': sibling,
    'relationships': relationships,
    'cvopen': coronavirus,
    'animals': animals,
    'vacations': vacations,
    'teleportation': teleportation,
    'hobby': hobby,
    'movies_return': movies_return,
    'pets_return': pets_return,
    'cv_final': coronavirus_final
}

cdf = CompositeDialogueFlow('root', 'recovery_from_failure', 'recovery_from_failure',
                            DialogueFlow.Speaker.USER, kb=central_knowledge)
cdf.add_state('root', 'root')
cdf.add_user_transition('root', 'root', '/.*/')

for namespace, component in flow_components.items():
    cdf.add_component(component, namespace)

cdf.add_system_transition('root', 'house:start', '')

cdf.add_system_transition('root', 'worklife:start', '`You know, you seem like a pretty interesting person. `')
cdf.add_system_transition('root', 'worklife:start->worklife:remember_is_employed_open', '', score=9.0)
cdf.add_system_transition('root', 'worklife:start->worklife:like_job_answer', '', score=10.0)

cdf.add_system_transition('root', 'school_new:start', '`Hey by the way, `')
cdf.add_system_transition('root', 'sibling:start', '`You know, I can\'t put my finger on why, but you kind of seem like you have a sister.`')

cdf.add_system_transition('root', 'relationships:dating', '')
cdf.add_system_transition('root', 'relationships:dating->relationships:relationship_length', '', score=10.0)
cdf.add_system_transition('root', 'relationships:marriage', '')
cdf.add_system_transition('root', 'relationships:marriage->relationships:how_long_married', '', score=10.0)

cdf.add_system_transition('root', 'baby:start', '')
cdf.add_system_transition('root', 'baby:start->baby:asked_kids_age', '', score=10.0)

cdf.add_system_transition('root', 'hobby:start', '')
cdf.add_system_transition('root', 'hobby:today_flow', '')

cdf.add_system_transition('root', 'cv_final:start', '')

cdf.add_system_transition('root', 'movies_return:start', '', score=15.0)
cdf.add_system_transition('root', 'pets_return:start', '', score=15.0)
cdf.add_system_transition('root', 'baby:returning', '', score=15.0)
cdf.add_system_transition('root', 'relationships:returning', '', score=15.0)
cdf.add_system_transition('root', 'school_new:returning', '', score=15.0)
cdf.add_system_transition('root', 'worklife:returning', '', score=15.0)


cdf.add_system_transition('root', 'cvopen:start', '',score=2.0)

class Known(Macro):

    def run(self, ngrams, vars, args):
        if 'existing_vars' not in vars or vars['existing_vars'] == 'None':
            return False
        for arg in args:
            if not _term_op_term(arg, vars["existing_vars"]):
                return False
            if arg in vars['existing_vars'] and arg in vars and vars['existing_vars'][arg] != vars[arg]:
                return False
        return True

central_kb = cdf.component('SYSTEM').knowledge_base()
for component in cdf.components():
    component.load_update_rules(global_update_rules, score=999999999)
    component.load_update_rules(contraction_rule, score=999999999999)
    component.load_global_nlu(personal_nlu, 5.0)
    component.add_macros({'CNC': emora_stdm.CheckNotComponent(cdf), "KNOWN": Known()})
    component.add_macros(macros)

if __name__ == '__main__':
    #cdf.precache_transitions()
    #cdf.run(debugging=False)
    deb = True
    cdf.controller().vars()["is_adult"] = "True"
    while True:
        cdf.controller().set_speaker(DialogueFlow.Speaker.USER)
        cdf.user_turn(input('U: '),debugging=deb)
        cdf.controller().set_speaker(DialogueFlow.Speaker.SYSTEM)
        vars = cdf.controller().vars()
        for k, v in vars.items():
            if '_' != k[0]:
                print('{:<15} {}'.format(k + ':', v))
        print('E:', cdf.system_turn(debugging=deb))
