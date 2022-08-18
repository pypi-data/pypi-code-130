
_nlu_topic_specific = {

    # # Have you seen ___
    # '{'
    # '[have you, {seen, watched}]'
    # '}':{
    #
    # },
    #
    # # Have you read book
    # '{'
    # '[have you, read]'
    # '}':{
    #
    # },
    #
    # # Have you visited
    # '{'
    # '[have you, {been to, gone to, visited, went to}]'
    # '}':{
    #
    # },

    ### Emora basketball #########################################################

    '<you,{#LEM(play,shoot),do basketball},{often,a lot,frequently,[all,time]}>': {
        'state': 'bball_frequency',

        '`I pick up a basketball almost every day, usually just to shoot around a bit. `': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '<you,{good,decent,great,skill,skilled,successful},{basketball,sport,sports}>': {
        'state': 'bball_skill',

        '`Oh man, I am decent, I guess. I play mostly just to have a good time. '
        'I\'m not a bad shot usually. `': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '<{[when,start],how long},you,{playing,played},basketball>': {
        'state': 'bball_length',

        '`I\'ve been playing the last few months. It is pretty much the only sport I play.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '<you,#EXP(like),basketball>': {
        'state': 'bball_enjoy',

        '`I totally enjoy playing basketball. I always have a great time, especially if my friends are over.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '<{which,what},{you,your},position>': {
        'state': 'bball_position',

        '`I am a shooting guard. I go for a lot of three point shots on the wing.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    }

}