
_nlu_testing = {

    # '{'
    # '[{talk about, conversation about, lets discuss, tell me} #ONT(all)]'
    # '}':{
    #
    # },

    '{[my name,is,not],[that,not,my name]}': 'wrong_name',

    '[{do you know, remember, what, whats, tell me, ask} my name]': {
        'state': 'test_user_name',

        '`It\'s` $username `, right?`': {

            '#UNX': {

                '#GRET': 'SYSTEM:root'
            },

            '{#DISAGREE,wrong,incorrect,false,is not}': {
                'state': 'wrong_name',

                '#DEFAULT `Oh, my bad. I guess I got it wrong. What is your name then?`': 'get_user_name',

                '`Oh, my bad. I was so sure you were` $username `, I\'m sorry. What is your name then?`'
                '#SET($username=None)': {
                    'state': 'get_user_name',

                    '{' 
                    '[$username=#ONT(_names)], ' 
                    '[! #ONT_NEG(_names), [name, is, $username=alexa]],' 
                    '[! my, name, is, $username=alexa],' 
                    '[! {can,may,should}, call, me, $username=alexa]' 
                    '}': {

                        '$username `? I\'ll try to remember that.`': {

                            '#DISAGREE'
                            '#SET($username=None)': {
                                'state': 'cant_hear_name',

                                '`Oh no! I think I\'m having trouble getting your name right. '
                                'Sometimes I can\'t hear certain names properly through the microphone, so I hope you '
                                'don\'t take it personally.`': {

                                    '#UNX(Sorry about it. Anyways )': {'#GRET': 'SYSTEM:root'}  # expand
                                }
                            },

                            '#UNX': {'#GRET': 'SYSTEM:root'}
                        }
                    },

                    '#UNX(None)': 'cant_hear_name'
                }
            },

            '#NOT(not) [{#AGREE, it is, right, correct, true}]': {

                '`You think I wouldn\'t remember your name? Anyway,` #GRET': 'SYSTEM:root'
            }
        },

        '`Hmm. I don\'t seem to remember your name. What would you like me to call you?`'
        '#UNSET(username)':
            'get_user_name'
    }
}