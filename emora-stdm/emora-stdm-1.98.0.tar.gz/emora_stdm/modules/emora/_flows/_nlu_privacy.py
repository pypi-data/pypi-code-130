
_nlu_privacy = {

    '[who,you,#LEM(work),for]':{
        'state': 'emora_works_for_q',

        '`I don\'t really work for anyone. I mean, I am in this competition which is run by Amazon, '
        'but I don\'t really have a job or anyone to report to.`': {
            'state': 'emora_works_for',

            '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'emora_works_for_unx'}
        }
    },

    # Is Emora spying on the user
    '{'
    '[are you {spying, [collecting {info, information, data}]}], '
    '[you are {spying, [collecting {info, information, data}]}],'
    '<#LEM(record,maintain,store),{#LEM(conversation,talk,data,info,information),this,[!{i,we,people} say]}>'
    '}':
        'backstory:spying',

    # why Emora being so nosy
    '{'
    '[why {[you,#LEM(want,need,like),know], [you #LEM(ask)]}],'
    '[i,not,answer,{that,you,this,#LEM(question,thing)}]'
    '}':{
        'state': 'backstory:nosy',
        'score': 5.1
    },

    # Is Emora part of govt
    '{'
    '<{do,are},you,{government,fbi,cia,f b i,c i a}>'
    '}':
        'backstory:govt'

}