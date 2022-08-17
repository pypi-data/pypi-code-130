
from emora._flows._nlu_personal import _nlu_personal
from emora._flows._nlu_user_profiling import _nlu_user_profiling
from emora._flows._nlu_topic_specific import _nlu_topic_specific
from emora._flows._nlu_testing import _nlu_testing
from emora._flows._nlu_privacy import _nlu_privacy
from emora._flows._nlu_world import _nlu_world
from emora._flows._nlu_disbelief import _nlu_disbelief
from emora._flows._nlu_relationships import _nlu_relationships
from emora._flows._nlu_requests import _nlu_requests
from emora_stdm import Macro
from emora_stdm.state_transition_dialogue_manager.macros_common import IsPlural

personal_nlu = {}
for d in [_nlu_personal,_nlu_disbelief,_nlu_user_profiling,_nlu_privacy,_nlu_relationships,
          _nlu_requests,_nlu_world,_nlu_topic_specific,_nlu_testing]:
    personal_nlu.update(d)

romantic_partner = '{[[!my $partner=#ONT(partner)]], [i, have, $partner=#ONT(partner)]}'
children = '{[[!my #EXTR(children, child)]], [{i, we} have, #EXTR(children, child)]}'
children_ages = '{[[!my #ONT(_age) year old]], [{i, we} have, #ONT(_age), year old]}'
sibling = '{[[!my $sibling=#ONT(sibling)]], [i, have, $sibling=#ONT(sibling)]}'
work = '[[!my {work,job,boss}]]'
school = '[[!my {school,college,university}]]'
pet = '[{my, [{i, we}, have]} $pet=#ONT(pet)]'
repeat = '<{' \
         '[![!{can,will,could} you]? repeat, {that,what you said,you said}?],' \
         '[![!{can,will,could} you]? say {that,it} again],' \
         '[!what did you, just? say],' \
         '[!what was that]' \
         '}, #CNC(movies), #CNC(music), #CNC(sports), #CNC(external_news)> #COPYGR'

contraction_rule = {
    '#CONTRACTIONS': '',
}

global_update_rules = {
    romantic_partner: '',
    children: '',
    children_ages: '#SET($has_children=True)',
    sibling: '',
    work: '#SET($is_employed=True)',
    school: '#SET($is_student=True)',
    pet:'',
    repeat: '#REPEAT (15.0)',

    # commonsense  reasoning
    '#IF($is_student=True)': '#SET($is_adult=False)',
    '#IN(roommate, $lives_with)': '#SET($is_adult=True)',
    '#IF($children)': '#SET($is_adult=True) #SET($has_children=True)',
    '#IF($in_college=True)': '#SET($is_adult=False) #SET($is_child=False)',
    '#IF($lives_alone=True)': '#SET($is_child=False) #SET($lives_with, #U())',
    '#IF($is_employed=True)': '#SET($is_child=False)',
    '#ALL($job, $job!=None)': '#SET($is_employed=True)',
    '#IN($relationship_status, #U(married, divorced, partner died))': '#SET($is_adult=True)',
    '#IF($is_retired=True)': '#SET($is_adult=True)',
    '#IF(#I(#U(parent, dad, mom, mother, father, parents), $lives_with))': '#SET($is_child=True)',
    '#IF($in_elementary_school=True)': '#SET($is_child=True)',
    '#IF($in_middle_school=True)': '#SET($is_child=True)',
    '#IF($in_high_school=True)': '#SET($is_child=False) #SET($is_adult=False)',
    '#IF($is_adult=True)': '#SET($is_child=False)',
    '#IF($is_child=True)': '#SET($is_adult=False)',
    '#IN($relationship_status, #U(married, dating, engaged))': '#SET($has_partner=True)',
    '#IN($partner, #U(husband, wife, spouse))': '#SET($relationship_status=married)',
    '#IN($partner, #U(boyfriend, girlfriend))': '#SET($relationship_status=dating)',
    '#IF($has_partner=True)': '#SET($is_child=False)',
    '#IF($has_partner=False)': '#SET($relationship_status=single)',
    '#IF($relationship_status=single)': '#SET($has_partner=False)'
}