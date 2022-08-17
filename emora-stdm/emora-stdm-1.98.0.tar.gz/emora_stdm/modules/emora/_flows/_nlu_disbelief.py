
_nlu_disbelief = {

    '{'
    '[{are you, are not you, you are} '
    '{robot, ai, a i, software, bot, chatbot, artificial intelligence, '
    'program, electronic, electric, human, person, living, alive, real}]'
    '}':
        'backstory:virtual',

    # Does Emora have something humanlike
    '{'
    '[you have, $q_body=#ONT(body)], '
    '[you, not, have, $q_body=#ONT(body)]'
    '}'
    '#SCORE(1.1)':
        'backstory:body',


    # User dislikes emora
    '[{'
    '[{this is, you are, your, [why, {you,this}]}, #NOT(not), #ONT(_insults)],'
    '[{this is, you are, your}, #NOT(not), {difficult,hard,bad}, {talk,conversation,discuss,understand}],'
    '[{do not, dont, cannot, cant}, {talk,conversation,discuss,understand}, you],'
    '[why, you, not, {smart, intelligent, better, capable, understandable, easier}],'
    '[why, <you,not>, brain],'
    '[you, piece, {garbage,shit}],'
    '[i, {hate,dislike,not impressed,[not,like]}, you],'
    '[<{are,arent,are not},you>,#LEM(listen),me]'
    '}]':
        'backstory:user_dislikes_emora',

    '[not,believe,you]':
        'world:user_in_disbelief',

    '#NOT(not) {[you,{lying,liar}],[{[was that],[did you],[that is]},lie]}':{
        'state': 'accused_lying',

        '`I\'m a little hurt that you think I would lie to you. Why do you think I am lying?`':{
            'state': 'lying_r',

            '{[i,{do not,did not},{say,think},you,{lying,lie,liar}],[!i do not]}': {
                'state': 'not_lying',

                '`Oh, okay. I guess I misunderstood what you meant. Anyways, ` #GRET': 'SYSTEM:root'
            },

            'error': {
                'state': 'lying_err',

                '`I\'m sorry if you think I was lying. '
                'I thought we were getting to know one another pretty well but maybe I\'m wrong. Anyways, `'
                '#GRET':
                    'SYSTEM:root'

            }
        }
    }

}