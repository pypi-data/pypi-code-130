
from _globals import PATHDIR
from emora_stdm import DialogueFlow
from emora._flows._central_knowledge import central_knowledge


movies_return = DialogueFlow('_local_start', kb=central_knowledge)
movies_return.add_system_transition('_local_start', 'start', '')

system = {
    'state': 'start',
    'enter': '#GATE #KNOWN($favorite_movie!=None)',

    '`Oh by the way, I wanted to share with you that I just watched ` $favorite_movie `. '
    'I see why you said it was your favorite, I really liked it.`': {

        '#UNX': {

            '`I thought the acting was great, and I loved the ending. Anyway, `': 'exit'
        }
    }
}

exit = {
    'state': 'exit',

    '#GCOM(movies_return) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:root'
    }
}

user = {
    'state': 'user'
}

movies_return.load_transitions(system)
movies_return.load_transitions(exit)
movies_return.load_global_nlu(user)


if __name__ == '__main__':
    movies_return.run(debugging=True)