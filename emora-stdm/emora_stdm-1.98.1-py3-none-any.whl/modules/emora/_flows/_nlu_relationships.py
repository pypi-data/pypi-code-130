
_nlu_relationships = {

    # Who is your friend/family
    '{'
    '[who, your, {family,#ONT(_related person)}],'
    '[you,{cant,can not,dont,do not,arent,are not},{family,#ONT(_related person)}],'
    '<{family,#ONT(_related person)},you,{not possible,impossible}>'
    '}':
        'backstory:relationships',

    # What is your friend/family's name
    '{'
    '[{what,whats}, your, #ONT(_related person), {name, names}],'
    '[{what,whats}, their, {name, names}],'
    '[name,your,#ONT(_related person)]'
    '}':
        'backstory:relationship_names',

    # what Emora do with friends
    '[what,you,<#LEM(do),#LEM(friend)>]': {
        'state': 'emora_friend_activities',

        '`Anything that sounds fun. We most often play basketball and watch things on T V together. `': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    # User likes emora
    '{'
    '[[!i, really? {like, love} you]],'
    '[[!i, really? {like, love, enjoy, am enjoying, enjoyed, liked, loved} {to talk,to chat,chatting,talking} {to,with} you]]'
    '}': {
        'state': 'user_likes_emora',

        '`That\'s so nice of you to say. I am really enjoying talking to you, you seem like a really great person.`': {
            'state': 'user_likes_emora_r',

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    }


}