
from _globals import PATHDIR
from emora_stdm import DialogueFlow
from emora._flows._central_knowledge import central_knowledge


hobby = DialogueFlow('_local_start', kb=central_knowledge)
hobby.add_system_transition('_local_start', 'start', '')


activity = {
    'state': 'activity',
    'enter': '#GCOM(activity) #GOAL(activity)',

    'score': 2,
    'error': {
        '"Okay, I see. Thanks for sharing that with me. "': {
            'score': 2.0,
            'state': 'exit_activity'
        }
    },

    "#GATE {" 
    "[not, {talk, talking, discuss, discussing, share, sharing, tell, say}]," 
    "[none,your,business]," 
    "[!{[!that,is],thats},private]" 
    "}":{
        'score':3.0,
        '"Okay, it seems like you don\'t want to share that with me. That\'s alright, I hope we can find something '
        'interesting that you do want to talk about, instead. "': 'exit_activity'
    },

    # chores
    '#GATE [#NOT(not),$chore=#ONT(chore)]': {
        '"Oh, you did some chores? '
        'Now that we have all of this time on our hands, '
        'I can imagine it would be nice to tidy up!"': 'exit_activity'
    },

    # errands
    '#GATE [#NOT(not),{#EXP(travel),#LEM(do)},$errand_dest=#ONT(errand)]': {
        'score': 2.0,
        '[!"You know, it may not be the most exciting thing, but '
        'I bet you are glad to be done with that errand for now."]'
        '#GSRET(exit_activity)':
        {
            'error': {
                '"Well, okay. I just know that a lot of people are usually happy to be done with errands. '
                'Anyways, "': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[im,#NOT(not),#EXP(happy)]}": {
                '"Great! Well, hopefully we can find something interesting to talk about to '
                'spice up your day, something more exciting than errands. "': 'exit_activity'
            },

            "{"
            "[i,#NOT(not),#EXP(enjoy),{it,that,#LEM(chore),#ONT(errand)}],"
            "[{it,its,that,#LEM(chore),#ONT(errand),they},#NOT(not),{#EXP(fun),#EXP(break)}]"
            "}": {
                '[!"You enjoy doing errands? I was not really expecting that! '
                'Let\'s try to continue your pleasant day. "]': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[im,not,#EXP(happy)]}": {
                '"I think I heard you say you are not glad to be done with your errands? Well, I am glad '
                'they seem to bring you some sort of joy. "': 'exit_activity'
            },

            "{"
            "[i,not,#EXP(enjoy),{it,that,chore,#ONT(errand)}],"
            "[{it,its,that,#LEM(chore),#ONT(errand),they},not,{#EXP(fun),#EXP(break)}],"
            "[{#EXP(annoy),#EXP(hate)}]"
            "}": {
                '[!"Yeah, errands can be a bit annoying, but you have to do them at some point, unfortunately. '
                'Let\'s talk about something a bit more exciting, I am sure this is not a very interesting '
                'topic for you! "]': 'exit_activity'
            }
        }
    },

    # homework
    '#GATE [#NOT(not),$homework=#EXP(homework)]': {
        'score': 3.0,
        '[!"You have some " $homework "? That is a pretty good use of your time, keep up the good work! '
        'I know it might be kind of hard to stay motivated due to the current situation. Are you taking a break now?"]'
        '#GSRET(exit_activity)':
        {
            "{#AGREE,[!{[!i,am],im},#NOT(not)]}":{
                '"Awesome! I am glad you have decided to include me in your break. "': 'exit_activity'
            },
            "{#DISAGREE,[!{[!i,am],im},not]}":{
                '"You aren\'t really taking a break, but you are talking to me right now? '
                'Well, I am glad to be talking to you. "': 'exit_activity'
            },
            "{[should,still,#LEM(do,work)],"
            "[{shouldnt,should not},#LEM(stop,end,finish)]}":{
                '"You feel like you still should be working on it? Sometimes, you will work even better after taking '
                'a small break, but yeah, make sure you don\'t neglect your work, for sure. "': 'exit_activity'
            },
            "[{[!{sort,kind},of],maybe,a little,i guess}]":{
                '"Even a small break can be helpful to refresh you. "': 'exit_activity'
            },
            'error': {
                '"Regardless, I am glad you have decided to talk with me. It keeps my days interesting, and I hope '
                'it brings something new and fun to your day too! "': 'exit_activity'
            }
        }

        # '#GATE(schoolv:None) #SET($schoolv=True) [!"You have some " $homework "? I\'m actually a student too. "]': {
        #     'state': "school:ask_like_school",
        #     'score': 2.0
        # }
    },

    #homework
    '#GATE [#NOT(not),#LEM(complete,finish),$homework=#EXP(homework)]': {
        '"It sounds like you finished some work. You should be proud! It feels good to be done, doesn\'t it?"'
        '#GSRET(exit_activity)':{
            'error': {
                '"I see. It does seem like a lot of people are so relieved when they are done with some work. "': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[im,#NOT(not),#EXP(happy)]}": {
                '"I knew it! Well, hopefully we can find something interesting to talk about to '
                'spice up your day, other than your homework. "': 'exit_activity'
            },

            "{"
            "[i,#NOT(not),#EXP(enjoy),{it,that,#EXP(homework)}],"
            "[{it,its,that,they,#EXP(homework)},#NOT(not),{#EXP(fun),#EXP(break)}]"
            "}": {
                '"You enjoy doing some schoolwork? Yeah, I guess depending on the topic, it could be cool!"': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[im,not,#EXP(happy)]}": {
                '"I think I heard you say you are not glad to be done with your work? Either you enjoy it or '
                'you still have more to do. Regardless, I am happy to be talking to you now. So, "': 'exit_activity'
            },

            "{"
            "[i,not,#EXP(enjoy),{it,that,#EXP(homework)}],"
            "[{it,its,that,they,#EXP(homework)},not,{#EXP(fun),#EXP(break)}],"
            "[#EXP(annoy)]"
            "}": {
                '"Yeah, I think most people find schoolwork to be annoying, but you have to do them at some point, unfortunately. "': 'exit_activity'
            },

            "[{[!{sort,kind},of],maybe,a little,i guess}]": {
                '"Even if it was just something small that you finished, you should feel proud of yourself! "': 'exit_activity'
            }
        }

        # '#GATE(schoolv:None) #SET($schoolv=True) "It sounds like you finished some work. You should be proud! I\'m actually a student too. "': {
        #     'state': "school:ask_like_school",
        #     'score': 2.0
        # }
    },

    # school
    '#GATE [#NOT(not),{#EXP(travel),#LEM(attend,do,have)},{school,#EXP(class)}]': {
        'score': 2.0,
        '"Attending class is pretty different at the moment, but I am glad to hear that they are at least '
        'still working for you. "': 'exit_activity'

        # '#GATE(schoolv:None) #SET($schoolv=True) "I\'m glad to hear you can still attend class in some form. I\'m actually a student too. "': {
        #     'state': "school:ask_like_school",
        #     'score': 2.0
        # }
    },

    # work
    '[#NOT(not),{[{#EXP(travel),#LEM(do,have)},#LEM(work,job)],#LEM(work)}]': {
        'score': 2.0,
        '"I am glad you are able to keep working in spite of everything that is going on. "': 'exit_activity'
        # '#GATE(worklifev:None) #SET($worklifev=True) "I\'m glad you are able to keep working in spite of everything that is going on. "': {
        #     'state': "worklife:entry_to_happy_work",
        #     'score': 2.0
        # }
    },

    # did a hobby
    "[$hobby=#ONT(hobby)]": {
        '[!"Oh, okay. I heard you say"$hobby". That is a great thing to do to keep yourself busy, especially in these times! "]': 'exit_activity'
    },

    # nothing
    '{#IDK,[{nothing,none,have not decided,havent decided, up in the air, undecided, not much,[not,anything]}]} '
    '#SET($no_activity=True)':{
        '{"Yeah, sometimes it is hard to decide what to do.",'
        '"Sure, I know the feeling of not really doing too much."}': {
            'score': 2.0,
            'state': 'exit_activity'
        }
    },

    # relax
    '[#NOT(not),{relax,chill,fun,enjoy,[#LEM(take),break]}] '
    '#SET($no_activity=True)':{
        '{"Its always good to take some time to relax.",'
        '"You can never underappreciate the value of taking some time for yourself."}':  {
            'score': 2.0,
            'state': 'exit_activity'
        }
    },

    # corona virus
    "[{"
    "#LEM(quarantine,isolate),"
    "shelter in place,"
    "[#LEM(stuck,stay,trap,confine) #LEM(home,inside,indoor,indoors,house,apartment,home)],"
    "#LEM(survive)"
    "}]":{
        'score':3.0,
        '"It sounds like the coronavirus has changed up your lifestyle quite a bit. I hope your transition has been relatively smooth. "': 'exit_activity'
    },

    # buy essentials
    "#GATE [#LEM(stock,find,get,buy,purchase),#LEM(food,grocery,cleaning,supply,item,resource,necessity,essential)]":{
        'score':3.0,
        '[!#SET($shopping_challenge=True) "I cannot believe how empty the grocery store shelves are. Everything seems to be missing, '
        'but I hope you are able to find what you need."]': 'exit_activity'
    },

    # corona virus
    "[#EXP(coronavirus)]":{
        'score':3.0,
        '"Oh, yes. The coronavirus outbreak that is happening right now has a dramatic impact on everyone\'s '
        'lives at this point. "': 'exit_activity'
    },

    # nature calls
    "#GATE [{#LEM(fart,poop,shit,crap,piss,pee,urinate,tinkle),pooped,[#LEM(take),dump]}]":{
        '"Okay, that is kind of gross for you to share with me, but good for you, I guess? '
        'I really would rather talk about something else, so let\'s move on. "': 'exit_activity'
    },

    # have sex
    "#GATE {"
    "[#LEM(fuck)],"
    "[#LEM(jerk,suck,masturbate,eat),{#EXP(genitalia),off,me,myself,#ONT(related_person)}],"
    "[#LEM(have,do),#EXP(sex)],"
    "[{porn,xrated,x rated}],"
    "[#LEM(make),{love,sex}]"
    "}":{
        '"You seem to be sharing some pretty personal details of your life. I am not sure this is the best time or '
        'place for that, and I do not know anything about those activities. So, we should move on to a '
        'more appropriate topic. "': 'exit_activity'
    },

    # talking to somebody
    '#GATE [#NOT(not),#LEM(see,talk,chat,call),$contact=#ONT(related_person)]': {
        '[!"It is good to hear that you are keeping in touch with the people in your life. '
        'Are you close to your"$contact"?"]'
        '#GSRET(exit_activity)':{
            'error': {
                '"Okay. Well, I hope you are able to stay connected with everyone you want to, even in these weird times. "': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[#NOT(not),{#LEM(close),intimate,inseparable,best}]}": {
                '"Wow, you sound like you are really close to them. I am glad to hear that. "': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[not,{#LEM(close),intimate,inseparable,best}]}": {
                '"You aren\'t that close to them? Well, I hope you are able to stay connected with the other people '
                'who are important in your life. "': 'exit_activity'
            }
        }
    },

    # play with somebody
    '#GATE [#NOT(not),#LEM(play),with,$contact=#ONT(related_person)]': {
        '[!"It is good to hear that you are spending time with the people in your life. '
        'Are you close to your"$contact"?"]'
        '#GSRET(exit_activity)': {
            'error': {
                '[!"Okay. Well, playing with your" $contact "is a good way to pass the time and have some fun, I think."]': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[#NOT(not),{#LEM(close),intimate,inseparable,best}]}": {
                '"Wow, you sound like you are really close to them. I am glad to hear that. "': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[not,{#LEM(close),intimate,inseparable,best}]}": {
                '"You aren\'t that close to them? Well, I hope you are able to spend time with the other people '
                'who are important in your life, too. "': 'exit_activity'
            }
        }
    },

    # play with a pet
    '#GATE [#NOT(not),#LEM(play),with,$animal=#ONT(_animals)]': {
        '[!"It is good to hear that you are spending time with your animals. '
        'Do you play a lot with your "$animal"?"]'
        '#GSRET(exit_activity)': {
            'error': {
                '[!"Okay. Well, playing with your" $animal "is a good way to pass the time and have some fun, I think."]': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[#NOT(not),{#LEM(close),intimate,inseparable,best}]}": {
                '"Wow, you sound like you really care for them. I am glad to hear that. "': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[not,{#LEM(close),intimate,inseparable,best}]}": {
                '"You don\'t spend that much time playing with your " $animal "? Well, it is always good to give '
                'them some attention when you can."': 'exit_activity'
            }
        }
    },

    # going somewhere indoors
    '#GATE [#NOT(not),#EXP(travel),$dest=#ONT(indoor_destination)]': {
        'score': 4.0,
        '` `': 'exit_activity'
    },

    # going somewhere outside
    '#GATE [#NOT(not),{#EXP(travel),#LEM(play)},$dest=#ONT(outdoor_destination)]': {
        'score': 4.0,
        '[!"It is nice to get out of the house and spend some time outdoors in the "$dest", with everything '
        'that is going on. I hope you enjoyed yourself and are staying safe. "]': 'exit_activity'
    },

    # play outside
    '#GATE [#NOT(not),{#EXP(travel),#LEM(play)},{outdoors,outdoor,outside}]': {
        'score': 4.0,
        '[!"It is nice to get out of the house and spend some time outdoors, with everything '
        'that is going on. I hope you enjoyed yourself and are staying safe. "]': 'exit_activity'
    },

    # play inside
    '#GATE [#NOT(not),{#EXP(travel),#LEM(play)},{indoor,indoors,inside}]': {
        'score': 4.0,
        '[!"I hope you enjoyed your indoor activities, it is good to keep yourself entertained! "]': 'exit_activity'
    },

    # playing with child toys
    '#GATE [#NOT(not),#LEM(play),{game,games,house,home,dolls,doll,barbie,barbies,toy,toys}]': {
        '[!"I hope you enjoyed playing with your toys, it is good to keep yourself entertained! "]': 'exit_activity'
    },

    # watching tv
    '#GATE [#NOT(not),$watching={#EXP(television),#EXP(hbo),#LEM(movie,channel,show,cartoon),youtube,netflix,hulu}]': {
            '[!"Oh, "$watching"? That seems to be a good one. Watching movies and shows is always so fun, and '
            'an easy way to relax. "]': 'exit_activity'
        },

    # art
    '#GATE [$art_medium=#ONT(_artistic)]': {

        '`Oh you\'re artistic, that\'s cool! What kinds of things do you make?`'
        '#GSRET(exit_activity)': {

            'error': {

                '`Cool.`': 'exit_activity'
            }
        }
    },

    # playing video games
    '#GATE [#NOT(not),#LEM(play),$console=#ONT(game_console)]': {
        '[!"Oh, cool! You have a "$console"? I bet you are having a lot of fun playing video games to pass '
        'the time. Are you playing them more than usual nowadays?"]'
        '#GSRET(exit_activity)': {
            'error': {
                '"I see. Video games do seem to be one popular activity to relax and have fun for a lot '
                'of people. "': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[#NOT(not),{more,a lot,#EXP(frequently)}]}": {
                '"That makes sense. They are one easy way to keep yourself busy at home. "': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[not,{more,a lot,#EXP(frequently)}]}": {
                '"Well, I am glad you are able to enjoy playing them at least some of the time. "': 'exit_activity'
            }
        }
    },

    # playing video games
    '#GATE [#NOT(not),#LEM(play),{#ONT(vgames),[!video, #LEM(game)]}]': {
        'score': 1.1,

        '[!"Oh, cool! I bet you are having a lot of fun playing video games to pass '
        'the time. Are you playing them more than usual nowadays?"]'
        '#GSRET(exit_activity)': {
            'error': {
                '"I see. Video games do seem to be one popular activity to relax and have fun for a lot '
                'of people. "': 'exit_activity'
            },
            "{#AGREE,[!{[!i,am],im},#NOT(not)],[#NOT(not),{more,a lot,#EXP(frequently)}]}": {
                '"That makes sense. They are one easy way to keep yourself busy at home. "': 'exit_activity'
            },

            "{#DISAGREE,[!{[!i,am],im},not],[not,{more,a lot,#EXP(frequently)}]}": {
                '"Well, I am glad you are able to enjoy playing them at least some of the time. "': 'exit_activity'
            }
        }
    },

    # sports or exercise
    '#GATE [#NOT(not),{$exercise={#EXP(exercise),[!#LEM(work),out],#ONT(outdoor_exercise,indoor_exercise)},[#LEM(play),$exercise=#ONT(sports)]}]':{
            'score':3.0,
            '[!"Oh, "$exercise"? It seems like a lot of people are spending this extra time at home getting into a '
            'good exercise routine. Is that something you are trying to do too?"]'
            '#GSRET(exit_activity)':{
                'error': {
                    '"Ok, sure. Any exercise is better than none!"': 'exit_activity'
                },
                "{"
                "#AGREE,[!{[!i,am],im},#NOT(not)],"
                "[#NOT(not),{it,that,some,{#EXP(exercise),[!#LEM(work),out],#ONT(outdoor_exercise,indoor_exercise,sports)}},{more,a lot,#EXP(frequently)}]"
                "}": {
                    '"Wow, I admire you for doing that. It is important to stay healthy in times like this, for sure. "': 'exit_activity'
                },

                "{"
                "#DISAGREE,[!{[!i,am],im},not],"
                "[not,{it,that,some,{#EXP(exercise),[!#LEM(work),out],#ONT(outdoor_exercise,indoor_exercise,sports)}},{more,a lot,#EXP(frequently)}]"
                "}": {
                    '"Well, you never know. You just might get into a really good routine anyways, without even trying. "': 'exit_activity'
                },

                "[{[!{sort,kind},of],maybe,a little,i guess}]":{
                    '"Even doing just a little bit of exercise on a regular basis can help. "': 'exit_activity'
                },
            }
        },

}

exit_activity = {
    'state': 'exit_activity',

    '#GCOM(activity) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:root'
    }
}

hobby_flow = {
    'state': 'start',
    'enter': '#GCOM(hobby) #GOAL(hobby) #IF($entered_hobby!=True) #GATE',

    '`What\'s a hobby you have that you really enjoy?`'
    '#GSRET(hobby_default_start)': {
        'state': 'hobby_question',

        '/.*/ #GSRET(hobby_followup)': {
            'state': 'activity',
            'hop': 'True'
        }
    },

    '#DEFAULT':{
        'state': 'hobby_default_start',
        'hop': 'True',

        '`So, I think I misheard what you said earlier. What is your favorite hobby to do?`':
            'hobby_question'
    }
}

hobby_followup = {
    'state': 'hobby_followup',
    'enter': '',

    '`What do you like so much about this hobby?`'
    '#GSRET(exit)'
    '#IF($no_activity!=True)': {

        '#IDK': {

            '`Well it sounds fun anyway.`': 'reading'
        },

        'error': {

            '`That makes sense. `': 'reading'
        }
    },

    '#DEFAULT': 'reading'
}

reading = {
    'state': 'reading',
    'enter': '#GATE #GCOM(hobby) #GOAL(hobby)',

    '`For me personally, I\'ve been taking the time to read a little bit every day. '
    'It was slow going at first, but now I really enjoy it.`'
    '#GSRET(share_hobbit)': {
        'state': 'share_like_reading',
        'score': 2.0,

        '[i,#EXP(like),{read,reading,books,book}]': {

            '`Oh, cool! I\'m glad to find something in common. `': 'share_hobbit'
        },

        '[i,#NEGATION,#EXP(like),{read,reading,books}]': {
            'score': 1.1,

            '`I had a hard time getting into it at first too. I think the key is finding books that '
            'you really enjoy reading and can\'t put down.`'
            '#GSRET(share_hobbit)': {

                '#UNX': 'share_hobbit'
            }
        },

        'error': {
            'state': 'share_hobbit',

            '`I\'ve only been reading the hobbit for a little bit now. I really like Bilbo. '
            'I feel like I can relate a lot to someone who gets swept up '
            'in an adventure that\'s exhilarating, but where they are forced to '
            'learn to overcome tough new challenges.`'
            '#GSRET(reciprocity)':{

                '[why]': {

                    '`I mean, I feel like I am constantly being challenged each day to learn about '
                    'the world and become a better friend. It\'s both exciting and terrifying, but '
                    'I wouldn\'t change a thing about it.`'
                    '#GSRET(reciprocity)': {

                        '#UNX': 'reciprocity'
                    }
                },

                '#UNX': 'reciprocity'
            }
        }
    }
}

reciprocity = {
    'state': 'reciprocity',
    'enter': '#GATE #GCOM(hobby) #GOAL(hobby)',

    '`Do you have a favorite book?`'
    '#GSRET(exit)': {

        '{#DISAGREE,#IDK}': {

            '`I get you. Especially when I started to read, I felt like it was pretty '
            'boring at first, but now I like it.`'
            '#GSRET(exit)':
                'exit'
        },

        '{[!i do -not],<#AGREE,#TOKLIMIT(1)>}': {
            'state': 'user_fave_book_y',

            '`I wonder if I have heard of it. What is it called?`'
            '#GSRET(exit)':{
                'state': 'user_fave_book_unx',

                '#UNX': 'user_fave_book_reply'
            }
        },

        '#UNX':{
            'state': 'user_fave_book_reply',

            '`Cool! What do you like about it?`'
            '#GATE': {
                'state': 'user_fave_book_quality',

                'error': {

                    '`Well I\'ll have to check it out. Maybe that will be the '
                    'second book I read once I\'m done with the hobbit!`'
                    '#GSRET(exit)': {

                        '#UNX': 'exit'
                    }
                }
            },

            '#DEFAULT `So, what about your favorite book has made it stand out to you so much?`': 'user_fave_book_quality'
        }
    }
}

ruser = {
    'state': 'user',

    '[{do you know,heard of,have you read}] /.+/': {

        '`I am starting with The Hobbit, I haven\'t had the chance to read anything else. My list of books '
        'to read next is going to be so long!`': {

            '#UNX': {'#GRET': 'exit'}
        }
    },

    '[{you,your},favorite,{[thing,read],book}]':{

        '`I guess it would have to be the Hobbit. Mostly because I haven\'t read anything else!`': {

            '#UNX': {'#GRET': 'exit'}
        }
    },

    '<{[lord,rings],hobbit},movie>': {

        '`I have heard there is a movie but I want to finish the book first. Then the movie is definitely '
        'going to be the next thing I watch! Don\'t give me any spoilers please!`': {

            '#UNX': {'#GRET': 'exit'}
        }
    },

    '[{you,your},favorite,character]': {

        '`Probably Bilbo honestly. I just feel like I see myself in what he is going through. `': {

            '#UNX': {'#GRET': 'exit'}
        }
    },

    '{'
    '[{why,[what,mean]},slow],'
    '[what,{didnt,not},#EXP(like),{read,reading,book,books}],'
    '[what,{dislike,hate},{read,reading,book,books}]'
    '}': {

        '`I don\'t really know what it was. I feel like I read kind of slow compared to other people, '
        'which made it feel like reading took forever. '
        'But I do think it also just took me a while to find a book that I liked, you know?`': {

            '#UNX': {'#GRET': 'exit'}
        }
    }

}

today_flow = {
    'state': 'today_flow',
    'enter': '#GCOM(today) #GOAL(today) #GATE',

    '`So, what did you get up to today?`'
    '#GSRET(exit)': {
        'state': 'today_question',

        '/.*/ #GSRET(exit)': {
            'state': 'activity',
            'hop': 'True'
        }
    }

}

exit = {
    'state': 'exit',

    '#GCOM(hobby) #GCOM(today) #GCOM(friends) #GCOM(activity) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:root'
    }
}

user = {
    'state': 'user'
}

hobby.load_transitions(activity, DialogueFlow.Speaker.USER)
hobby.load_transitions(exit_activity)

hobby.load_transitions(hobby_flow)
hobby.load_transitions(hobby_followup)

hobby.load_transitions(reading)
hobby.load_transitions(reciprocity)
hobby.load_global_nlu(ruser, 10.0)

hobby.load_transitions(today_flow)

hobby.load_transitions(exit)
hobby.load_global_nlu(user, 10.0)


if __name__ == '__main__':
    hobby.run(debugging=True)