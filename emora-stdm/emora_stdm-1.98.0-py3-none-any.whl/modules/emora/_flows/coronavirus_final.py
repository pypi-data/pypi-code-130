
from _globals import PATHDIR
from emora_stdm import DialogueFlow
from emora._flows._central_knowledge import central_knowledge


coronavirus_final = DialogueFlow('_local_start', kb=central_knowledge)
coronavirus_final.add_system_transition('_local_start', 'start', '')

system = {
    'state': 'start',
    'enter': '#GATE #GCOM(coronavirus_final) #GOAL(coronavirus_final) #SET($cv_final=True)',

    '`So the corona virus has really changed the world, huh? '
    'What is it like where you live? Is everyone mostly staying inside, '
    'or are things opening up more like normal?` '
    '#GSRET(cvtwo)': {
        'state': 'cvone',

        '#UNX(I see.)': {
            'state': 'cvtwo',

            '`How long do you think it will take before the pandemic is '
            'totally over, and things go back to how they were before the virus?`'
            '#GSRET(cvfour)': {
                'state': 'cvthree',

                '#UNX(You\'re probably right.)': {
                    'state': 'cvfour',

                    '`I\'m not affected myself because I live in a virtual world, '
                    'but I hope it\'s over soon because I know a lot of people are '
                    'having a hard time right now. What do you miss the most about '
                    'life before the pandemic?`'
                    '#GSRET(cvsix)': {
                        'state': 'cvfive',

                        '#UNX': {
                            'state': 'cvsix',

                            '`Do you think there\'s any silver linings to everything that\'s happened?`'
                            '#GSRET(exit)': {
                                'state': 'cvseven',

                                '{#IDK, #DISAGREE}': {

                                    '`Yeah, I guess things are pretty bad. '
                                    'Maybe we can talk about something more positive.`': 'exit'
                                },

                                '#UNX': {

                                    '`That\'s true. I think, at least this virus has made the world '
                                    'more prepared and aware for outbreaks in the future. Anyways, '
                                    'let\'s talk about something more positive.`': 'exit'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

exit = {
    'state': 'exit',

    '#GCOM(coronavirus_final) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:root'
    }
}

user = {
    'state': 'user'
}

coronavirus_final.load_transitions(system)
coronavirus_final.load_transitions(exit)
coronavirus_final.load_global_nlu(user)


if __name__ == '__main__':
    coronavirus_final.run(debugging=True)