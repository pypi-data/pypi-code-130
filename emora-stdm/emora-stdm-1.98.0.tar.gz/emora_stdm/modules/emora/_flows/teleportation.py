from _globals import PATHDIR
from emora_stdm import DialogueFlow
from emora._flows._central_knowledge import central_knowledge

teleportation = DialogueFlow('_local_start', kb=central_knowledge)
teleportation.add_system_transition('_local_start', 'start', '')

cold_start = {
    'state': 'cold_start',
    'enter': '#GATE #GCOM(teleportation) #GOAL(teleportation)',

    '`So, this idea is relatively new to me. '
    'I just heard about it when my friends were talking about science fiction books, '
    'but what do you think about the possibility of teleportation?`'
    '#GSRET(default_start)':
        'teleportation_q'

}

system = {
    'state': 'start',
    'enter': '#GATE #GCOM(teleportation) #GOAL(teleportation)',

    '#DEFAULT': {
        'state': 'default_start',
        'hop': 'True',

        '`Wait, so what do you think about the possibility of teleportation?`':
            'teleportation_q'
    },
    '"What do you think about the possibility of teleportation?"'
    '#GSRET(default_start)': {
        'state': 'teleportation_q',

        '{'
        '[#NOT(is not),#ONT(_positive adj)],'
        '[#NEGATION,#ONT(_negative adj)],'
        '[#NOT(not),{should,easier,easy,looking forward,#ONT(_eager,_happy)}],'
        '[#NOT(not),#EXP(like),{it,teleportation,idea}]'
        '}':{
            'state': 'teleportation_good',

            '`It does sound pretty cool! `':{
                'state': 'ask_first_person',
                'hop': 'True',
                'enter': '#GATE',

                '`Would you be one of the first people to try it out?`'
                '#GSRET(next_question)': {
                    'state': 'first_person',

                    '{#AGREE,[#NOT(not), {[i, would], [i, think, so]}]}':{
                        'state': 'first_person_y',

                        '`You would volunteer so early? That is so courageous! '
                        'I don\'t think I could gather the courage to do that.`':
                            'next_question'
                    },

                    '{#DISAGREE,[i, would, not], [i, not, think, so]}': {
                        'state': 'first_person_n',

                        '`Just like you, I definitely need other people to test it out first. '
                        'Safety is important, for sure.`':
                            'next_question'
                    },

                    '{#IDK,#MAYBE}': {
                        'state': 'first_person_idk',

                        '`I understand the uncertainty. '
                        'There are so many unknowns about it, since it isn\'t real right now.`':
                            'next_question'
                    },

                    '#UNX': {
                        'state': 'first_person_unx',

                        '`I think its a pretty tough choice either way. `':
                            'next_question'
                    }
                }
            }
        },

        '{'
        '[#NEGATION,#ONT(_positive adj)],'
        '[should not],'
        '[#NOT(is not),#ONT(_negative adj,_worried,_confused_,_scared)],'
        '[#NEGATION,{looking forward,#ONT(_eager,_happy)}],'
        '[#NEGATION,#EXP(like),{it,teleportation,idea}]'
        '}': {
            'state': 'teleportation_scary',

            '`You bring up a good point. It might be dangerous, so we should be cautious. `':{
                'state': 'ask_scariest_part',
                'hop': 'True',
                'enter': '#GATE',

                '`I think the scariest part would be not making it to the destination in one piece. '
                'Are you scared of that too?`'
                '#GSRET(next_question)': {
                    'state': 'scariest_part',

                    '{#AGREE,[#NOT(not),i,am]}':{
                        'state': 'scariest_part_y',

                        '`Oh boy. It makes me shake just thinking about it! `':
                            'next_question'
                    },

                    '{#DISAGREE,[i, would, not], [i, not, think, so]}': {
                        'state': 'scariest_part_n',

                        '`Really? You are not scared of that? Maybe you know something I don\'t.`':
                            'next_question'
                    },

                    '{#IDK,#MAYBE}': {
                        'state': 'scariest_part_idk',

                        '`It is a weird thing to think about, but hopefully that would never happen! `':
                            'next_question'
                    },

                    '#UNX': {
                        'state': 'scariest_part_unx',

                        '`For me, even just the possibility is pretty unnerving to think about. `':
                            'next_question'
                    }
                }
            }
        },

        '[#NOT(is not), {difficult,hard,challenging,unlikely,impossible,[{not,never},{happen,happening,real,likely}]}]': {
            'state': 'teleportation_unlikely',

            '`You may be right. It is a very hard thing to do and it is just fiction right now, after all. `': {
                'state': 'ask_hardest_part',
                'hop': 'True',
                'enter': '#GATE',

                '`If you had to pick, what do you think is the biggest challenge for making a '
                'teleportation device?`'
                '#GSRET(next_question)': {
                    'state': 'hardest_part',

                    "{" 
                    "[#LEM(take), apart],"
                    "[#LEM(put), {back,together}],"
                    "[{deconstruct,deconstructing,construct,constructing,reconstruct,reconstructing,"
                    "#LEM(build,make,form,break,molecule,particle,atom,piece)}]"
                    "}":{
                        'state': 'hardest_part_construction',

                        '`That\'s what I was thinking. How to actually break down and then put things back together '
                        'must be very hard. `':
                            'next_question'
                    },

                    '[{teleport,teleportation,teleporting,complicated,hard,challenging,difficult,challenge}]': {
                        'state': 'hardest_part_all',
                        'score': 0.9
                    },

                    '[{everything,[{every,each,all},of it],[#LEM(get,make,go),#LEM(work)]}]': {
                        'state': 'hardest_part_all',
                        'score': 1.1,

                        '`The whole idea of teleportation in general is definitely challenging. I don\'t really even '
                        'know what it would take to make it, either! `':
                            'next_question'
                    },

                    '[{device,structure,electrical,technology,coding,code,#LEM(test,wire),knowledge,education,#LEM(know,understand)}]': {
                        'state': 'hardest_part_technical',

                        '`I agree. Whoever makes it happen will definitely have to be very knowledgeable about '
                        'technology and the physical world. `':
                            'next_question'
                    },

                    '[{impossible,[not,{real,possible}]}]': {
                        'state': 'hardest_part_impossible',

                        '`So, you really don\'t think it will ever happen? I guess '
                        'it does just seem like a fantasy, at least at the moment. `':
                            'exit'
                    },

                    '[{safe,legal,[not,dangerous],#LEM(use,adopt,accept,regulate)}]': {
                        'state': 'hardest_part_acceptance',
                        'score': 0.9,

                        '`Making it safe should be the number one priority for sure. And, '
                        'as long as that is proven without a doubt, I think people would start to use it. `':
                            'next_question'
                    },

                    "{" 
                    "[{transport,transporting,transportation,transfer,transferring,send,sending,mechanics,move,moving}]"
                    "}": {
                        'state': 'hardest_part_transfer',

                        '`Yes, it definitely seems crazy thinking about how to instantaneously send an item from one place '
                        'to another. II would imagine that it is a pretty big part of the challenge. `':
                            'next_question'
                    },

                    '#IDK': {
                        'state': 'hardest_part_idk',

                        '`No big deal. There are many difficult pieces in the puzzle of teleportation, '
                        'so we can just leave figuring all that out to the scientists. `':
                            'next_question'
                    },

                    '#UNX': {
                        'state': 'hardest_part_unx',

                        '`There are many difficult pieces in the puzzle of teleportation, '
                        'so we can just leave figuring all that out to the scientists. `':
                            'next_question'
                    }
                }
            }
        },

        '#IDK': {
            'state': 'teleportation_idk',

            '`I get it. It is hard to have an opinion on something that is still a bit out of reach. `':
                'next_question'

        },

        '#UNX':{
            'state': 'teleportation_unx',

            '`I think that it sounds cool, scary, and quite impossible, all at the same time! `':
                'next_question'
        }
    }
}

question_loop = {
    'state': 'next_question',

    '` `': 'ask_first_person',
    '`  `': 'ask_scariest_part',
    '`   `': 'ask_hardest_part',
    '`     `': {
        'state': 'before_exit',
        'score': 0.0
    }
}

before_exit = {
    'state': 'before_exit',

    '#UNX': 'exit'
}

exit = {
    'state': 'exit',

    '#GCOM(teleportation) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:teleportation_topic_switch'
    }
}

user = {
    'state': 'user',

    '{' 
    '[{[!{dont,do not}, know],not sure,unsure,uncertain}, what, {that,teleportation,it,teleport,you said}, {is,mean,means}],' 
    '[what,is,{that,teleportation,it,teleport,you said}],'
    '[what,does,{that,teleportation,it,teleport,you said},mean]'
    '}': {
        'state': 'what_is_teleportation',

        '`Teleportation is the process of moving an object from one location to another instantaneously and it is commonly '
        'referenced in science fiction.`': {
            'state': 'explain_teleportation',

            '#UNX': {'#GRET': 'exit', 'state': 'explain_teleportation_unx'}
        }
    }
}

teleportation.load_transitions(system)
teleportation.load_transitions(question_loop)
teleportation.load_transitions(cold_start)
teleportation.load_transitions(exit)
teleportation.load_transitions(before_exit, DialogueFlow.Speaker.USER)
teleportation.load_global_nlu(user)


if __name__ == '__main__':
    #teleportation.precache_transitions()
    teleportation.run(debugging=False)






