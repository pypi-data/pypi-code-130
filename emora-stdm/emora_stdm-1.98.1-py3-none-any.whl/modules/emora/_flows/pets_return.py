
from _globals import PATHDIR
from emora_stdm import DialogueFlow
from emora._flows._central_knowledge import central_knowledge


component = DialogueFlow('_local_start', kb=central_knowledge)
component.add_system_transition('_local_start', 'start', '')

system = {
    'state': 'start',
    'enter': '#GATE #KNOWN($pet_type!=None)',

    '`Is your ` $pet_type ` around? I want to say hi.`': {

        '#AGREE': {

            '`Hi there ` $pet_type `! ... Sorry I don\'t think I can pronounce it\'s name. '
            'Did it hear me?`': 'call_to_pet',

            '`Hi ` $pet_name `! ... Did it hear me?`': {
                'state': 'call_to_pet',
                'score': 2.0,

                '#AGREE': {

                    '`Nice! Your ` $pet_type ` seems so great.`': {

                        'error': 'exit'
                    }
                },

                'error': {

                    '`Oh well, maybe next time. Your ` $pet_type ` seems so great.`': {

                        'error': 'exit'
                    }
                }
            }
        },

        'error': {

            '`Oh well, maybe next time. Your ` $pet_type ` seems so great.`': {

                'error': 'exit'
            }
        }
    }
}

exit = {
    'state': 'exit',

    '#GCOM(component) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:root'
    }
}

user = {
    'state': 'user'
}

component.load_transitions(system)
component.load_transitions(exit)
component.load_global_nlu(user)


if __name__ == '__main__':
    component.run(debugging=True)