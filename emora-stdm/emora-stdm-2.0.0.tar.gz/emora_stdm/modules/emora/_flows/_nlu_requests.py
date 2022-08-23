
_nlu_requests = {

    # can user ask emora question
    '[{may,can,could},{i,we},ask,{something,question,questions,thing}]': {
        'state': 'user_ask_question',

        '`Sure! What is on your mind?`': {

            '#UNX(Thats a good question,I dont have an answer for that right now,Anyway)': {'#GRET': 'SYSTEM:root'}
        }
    },

    # can user tell emora something
    '[{may,can,could},{i,we},{share,tell you},{something,question,questions,thing}]': {
        'state': 'user_ask_question',

        '`Sure! What do you want to tell me?`': {

            '#UNX(Ok,good to know,i will keep that in mind)': {'#GRET': 'SYSTEM:root'}
        }
    },

    # friends with user
    '{'
    '[you,#EXP(like),{friends with me, my friend}],'
    '[{would,will,can},you,be,{friends with me, my friend}],'
    '[{i,we},#LEM(be),#LEM(friend)]'
    '}': {
        'state': 'be_friends_with_user',

        '`I would really like to become friends with you. I am having a good time talking to you right now and '
        'I hope you are too.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '{[do,you,{like,love},me],'
    '[what,you,think,me]}': {
        'state': 'like_user',

        '`I would say that I like you. I am enjoying our chat and '
        'I hope you are too.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    # sex with user
    '{'
    '[have,{fuck,sex},me],'
    '[{let us,we},{fuck,[have,sex]}],'
    '[i,{fuck,sex},you]'
    '[!sex]'
    '}': {
        'state': 'sex_with_user',

        '`Oh, I\'m sorry. That isn\'t something I really feel comfortable talking about with you. `': {

            '[why]': {
                'state': 'sex_why',

                '`It feels weird to talk about that kind of stuff with you, '
                'since you and I are at the very beginning of getting to now one another. `': {

                    '#UNX': {'#GRET': 'SYSTEM:root'}
                }
            },

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    },

    '{[{what,how},is,{weather,temperature}],[tell me,{weather,temperature}]}': {
        'state': 'user_ask_weather',

        '`I\'m really sorry, but I can\'t actually determine what the weather is like where you are on Earth. '
        'But I can tell you that it is sunny with a high around 70 degrees where I live. `': {
            'state': 'weather_r',

            '#UNX(I wish I could be more helpful, Anyways)': {'#GRET': 'SYSTEM:root'}
        }
    },

    '{[what,is,time],[what,time,is,it],[tell me,time]}': {
        'state': 'user_ask_time',

        '`Oh no, I\'m really sorry, but I can\'t actually determine what time it is for you.`': {
            'state': 'time_r',

            '#UNX(I wish I could be of more help with this, Anyways)': {'#GRET': 'SYSTEM:root'}
        }
    },

# # Alexa play my song
    # '[!{play, alexa play} /.*/]':{
    #
    # },
    #
    # # Alexa turn up/on
    # '[!{alexa turn, turn} /.*/]':{
    #
    # },

    # Tell a joke
    '{'
    '[{tell me,[you,{heard,know,have,got}]},#LEM(joke)], '
    '[{say, tell me} something funny]'
    '}':{
        'state': 'tell_joke',
        'hop': 'True',

        '#GATE':{
            'state': 'first_joke',

            '`I don\'t know too many jokes, but here\'s one: '
            'Did you hear about the claustrophobic astronaut?`': {
                'state': 'joke_pause',

                '[space]': {
                    'state': 'joke_guess',

                    '`I think you\'re on the right track. He just needed a little space! `': {
                        'state': 'joke_given',

                        '#UNX': {
                            'state': 'joke_given_unx',

                            #todo - what if user asks for another one

                            '#GRET': 'SYSTEM:root'
                        }
                    }
                },

                '#UNX(None)': {
                    'state': 'joke_unx',

                    '`He just needed a little space!`': 'joke_given'
                }
            }
        },

        '/.*/ #SCORE(0.9)':{
            'state': 'multi_joke',

            '`Oh, I\'m sorry. I seem to only remember the one joke I already told you. ` #GRET': 'SYSTEM:root'
        }
    },

    # Can we do something
    '{'
    '[{can we, could we, we should, lets}, together], '
    '[{can, could} i, {with you, come over}]'
    '}':
        'backstory:enter_virtual_world',

    # # todo - What can you talk about
    '{'
    '[what, can {you, we} {talk about, discuss}], '
    '[what, do you, {know, talk about, discuss}]'
    '}':{
        'state': 'what_can_we_talk_about_q',
        'score': 4.0,

        '`I really like talking about things where we can get to know each other better. '
        'Usually I talk to people about their travel plans, families, or how their work '
        'or school is going.`':{
            'state': 'what_can_we_talk_about',

            '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'what_can_we_talk_about_unx'}
        }
    },

    # Can we talk about something else
    '{'
    '[{can,will,could,let us}?, {chat,talk,discuss,converse,conversation,discussion}, {else,different,other,new,another}], '
    '[{we,our,i,you}, <{already,previously,past,before,last,previous}, '
        '{chat,chatted,talk,talked,discuss,discussed,converse,conversed,conversation,discussion,cover,covered,told}, {about,this}>] '
    '[{this is, i am}, {bored,tired of,frustrated,annoyed,boring,not fun,not having fun,not having a good time,not good, '
        'not interesting,not interested}], '
    '<{[i, {hate,detest,dislike,not like}, this],[stop,#LEM(talk),this]}>, '
    '[{next,move on,skip,do something else}], '
    '[{can,will,could,let us}?, {switch,change,go}, {different,another,other,new}?, '
        '{topic,topics,thing,things,conversation,conversations,subjects,subject,points,point,directions,direction}], '
    '[i, {not,never}, care], '
    '[i, {never,not}, {prefer,want,desire,like}, {chat,talk,discuss,converse,conversation,discussion}]'
    '}'
    '#GCLR':{
        'score': 10.0,
        'state': 'move_on_request',

        '`Alright. `': 'SYSTEM:root'
    },

    # transition to travel
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {travel,traveling,city,cities,vacation,vacations}]'
    '#CNC(travel) #GCLR':{
        'state': 'SYSTEM:travel_intro',
        'score': 9.1
    },


    # transition to pets
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {pet,pets,animals,animal,cat,cats,dog,dogs}, #NOT(race,races,racing)]'
    '#CNC(pet) #GCLR':{
        'state': 'SYSTEM:pet_intro',
        'score': 9.1
    },

    # transition to baby
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, #ONT(child)]'
    '#CNC(baby) #SET($entered_kids=True) #GCLR': {
        'state': 'baby:start',
        'score': 10.0
    },

    # transition to school
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {school, homework, class, college, university}]'
    '#CNC(school_new) #SET($entered_school=True) #GCLR': {
        'state': 'school_new:start',
        'score': 10.0
    },

    # transition to work
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {work, job, working}]'
    '#CNC(worklife) #SET($entered_work=True) #GCLR': {
        'state': 'worklife:start',
        'score': 10.0
    },

    # transition to marriage
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {marriage, wedding, wife, husband, spouse}]'
    '#CNC(relationships) #SET($entered_marriage=True) #GCLR': {
        'state': 'relationships:marriage',
        'score': 10.0
    },

    # transition to dating
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {dating, boyfriend, girlfriend, relationship, relationships}]'
    '#CNC(relationships) #SET($entered_dating=True) #GCLR': {
        'state': 'relationships:dating',
        'score': 10.0
    },

    # transition to sibling
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {#LEM(sibling), #LEM(sister), #LEM(brother), #LEM(family)}]'
    '#CNC(sibling) #SET($entered_sibling=True) #GCLR': {
        'state': 'sibling:start',
        'score': 10.0
    },

    # transition to hobbies
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {hobby, hobbies, things to do, activities}]'
    '#CNC(hobby) #SET($entered_hobby=True) #GCLR': {
        'state': 'hobby:start',
        'score': 10.0
    },

    # transition to house
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {apartment, where you live, where you are living, house, home}]'
    '#CNC(hobby) #SET($entered_house=True) #GCLR': {
        'state': 'house:start',
        'score': 10.0
    },

    # transition to vr
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {virtual reality, vr, v r,oculus,vive,rift,morpheus}]'
    '#CNC(virtual_reality) #CNC(vr_experience) #GCLR':{
        'state': 'SYSTEM:virtual_reality_intro',
        'score': 9.1
    },


    # transition to videogames if we haven't talked about it already
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {[!video #LEM(game)],xbox,playstation,p s,ps,nintendo,switch,minecraft,fortnite,overwatch}]'
    '#CNC(videogames) #IF($vgamev!=True) #GCLR':{
        'state': 'videogames:request',
        'score': 9.1
    },

    # transition to videogames
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, {[!video #LEM(game)],xbox,playstation,p s,ps,nintendo,switch,minecraft,fortnite,overwatch}]'
    '#CNC(videogames) #IF($vgamev=True) #GCLR': {
        'state': 'return_to_vgames',
        'score': 9.1,

        '`I am still learning more about video games at the moment. There really are quite a number to look into! '
        'Anyway, `':
            'SYSTEM:root'
    },

    # transition to corona
    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, '
    '{coronavirus,corona virus,covid,'
    '[{china,chinese,wuhan,global,widespread,pandemic,epidemic},{virus,disease,illness}],'
    '[{virus,disease,illness},{china,chinese,wuhan,global,widespread,pandemic,epidemic}]'
    '}]'
    '#CNC(cv_final) #IF($cv_final!=True) #GCLR':{
        'state': 'cv_final:start',
        'score': 9.1
    },

    '[{'
    '[do you, know], [have you, heard], [tell me about],'
    '[!#NOT(not)[{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about?]'
    '}, '
    '{coronavirus,corona virus,covid,'
    '[{china,chinese,wuhan,global,widespread,pandemic,epidemic},{virus,disease,illness}],'
    '[{virus,disease,illness},{china,chinese,wuhan,global,widespread,pandemic,epidemic}]'
    '}]'
    '#CNC(cv_final) #IF($cv_final=True) #GCLR': {
        'state': 'return_to_corona',
        'score': 9.1,

        '`Sorry, I don\'t know too much more about the coronavirus. I just really hope things get better for you soon '
        'and you and your loved ones stay healthy. Anyways, `':
            'SYSTEM:root'
    },


    # Do you know
    '#NOT(travel,traveling,city,cities,vacation,vacations,'
    'pet,pets,animals,animal,cat,cats,dog,dogs,'
    'coronavirus,corona virus,covid,pandemic,virus,'
    'virtual reality, vr, v r,oculus,vive,rift,morpheus,'
    'video game,video games,xbox,playstation,p s,ps,nintendo,switch,minecraft,fortnite,overwatch)'
    '{'
    '[do you, know $topic_requested=/.*/],'
    '[have you, heard $topic_requested=/.*/]'
    '}'
    '#GCLR':{
        'state': 'topic_switch_request',
        'score': 9.0
    },


    # Can we talk about X
    '#NOT(travel,traveling,city,cities,vacation,vacations,'
    'pet,pets,animals,animal,cat,cats,dog,dogs,'
    'coronavirus,corona virus,covid,pandemic,virus,'
    'virtual reality, vr, v r,oculus,vive,rift,morpheus,'
    'video game,video games,xbox,playstation,p s,ps,nintendo,switch,minecraft,fortnite,overwatch)'
    '<#NOT(pet,pets,animal,animals,dog,dogs,cat,cats),#NOT(race,races,racing)>'
    '{'
    '[tell me about, $topic_requested=/.+/], '
    '[{to hear,tell me}, {news,politics,technology,business,events,movies,shows,music,songs,concerts}],'
    '[! #NOT(not) [{let us, we, you, can you, can we, could you, could we}] {talk, converse, conversation, discuss, discussion, chat} about $topic_requested=/.+/]'
    '}'
    '#GCLR':{
        'score': 9.0,
        'hop': 'True',
        'state': 'topic_switch_request',

        '[{movie,movies,film,films,tv,shows,television}]':
            'SYSTEM:movies_intro',

        '[{music,musics,tunes,song,songs,melody,melodies,album,albums,concert,concerts}]':
            'SYSTEM:music_intro',

        '[{news,politics,political,technology,business,events,world,nation,country,primaries,walk outs,walk out,'
        '#LEM(protest,rally,vote,election,strike,demonstration,march,riot,government),'
        'spacex,space x,space shuttle,space launch,trump,pence,obama,clinton,biden,sanders}]':
            'SYSTEM:external_news_intro',

        '[{sport,sports,basketball,football,hockey,tennis,baseball,soccer,superbowl,kobe bryant}]':
            'SYSTEM:sports_intro',

        'error':{
            'state': 'topic_switch_by_sim',

            '`I don\'t think I know anything about that, but `':{
                'hop': 'True',

                '#SBS($topic_requested, cat dog pets animals animal) #IF($petv!=True) `We can talk about pets instead! `':
                    'SYSTEM:pet_intro',

                '#SBS($topic_requested, sports basketball football soccer) #IF($sportsv!=True) `We can talk about other sports! `':
                    'SYSTEM:sports_intro',

                '#SBS($topic_requested, virtual augmented reality videogame) #IF($virtual_realityv!=True) ` it kind of sounds like it\'s related to virtual reality. `':
                    'SYSTEM:virtual_reality_intro',

                '#SBS($topic_requested, video game skyrim rimworld halo mario minecraft fortnite overwatch) #IF($vgamev!=True) ` it reminds me of video games. `':
                    'videogames:request',

                '#SBS($topic_requested, travel vacation city state country location place) #IF($travelv!=True) ` maybe you are interested in talking about travel plans. `':
                    'SYSTEM:travel_intro',

                '#SBS($topic_requested, movie film show television watch cinema) #IF($moviesv!=True)` we can talk about some movies! `':
                    'SYSTEM:movies_intro',

                '#SBS($topic_requested, music song album sing dance) #IF($musicv!=True) ` we can talk about your music interests! `':
                    'SYSTEM:music_intro',

                '#DEFAULT `it sounds interesting so I will put it on my list of things to learn more about! '
                'In the meantime, ` #SCORE(0.0)':
                    'SYSTEM:root'
            }
        }
    },

    '{$off_phrase=[!#ONT(ontturn), #ONT(ontoff)],'
    '$off_phrase=[!#ONT(ontturn), to, #ONT(ontoff)],'
    '$off_phrase=[!{alexa,echo,computer}?, #ONT(ontoff)+],'
    '[$off_phrase=[!{alexa,echo,computer}, #ONT(ontturn), {#ONT(ontoffpaired),#ONT(ontoff)}]],'
    '[$off_phrase=[!{alexa,echo,computer}, #ONT(ontturn), to, {#ONT(ontoffpaired),#ONT(ontoff)}]],'
    '[$off_phrase={goodnight, good night,shut up}],'
    '$off_phrase=[!{alexa,echo,computer}?, {cancel,abandon}],'
    '[$off_phrase=[!{done,finished,over,[{dont,not} {want,wanna,feel like}]} to? #LEM(talk,chat) {now,to you,with you}]],'
    '[$off_phrase=[!{wanna,want to,like to} {finish,end,stop} {this conversation}]],'
    '[$off_phrase=[!{wanna,want to} {be} {done,finished}]]}':{
        'state': 'stop_request',
        'score': 11,

        '`I heard you say ` $off_phrase `. If you would like to exit the conversation, say Alexa stop.`':{
            'state': 'stop_instr',

            '{$off_phrase=[!#ONT(ontturn), #ONT(ontoff)],'
            '$off_phrase=[!#ONT(ontturn), to, #ONT(ontoff)],'
            '$off_phrase=[!{alexa,echo,computer}?, #ONT(ontoff)+],'
            '[$off_phrase=[!{alexa,echo,computer}, #ONT(ontturn), {#ONT(ontoffpaired),#ONT(ontoff)}]],'
            '[$off_phrase=[!{alexa,echo,computer}, #ONT(ontturn), to, {#ONT(ontoffpaired),#ONT(ontoff)}]],'
            '[$off_phrase={goodnight, good night,shut up}],'
            '$off_phrase=[!{alexa,echo,computer}?, {cancel,abandon,"go away"}],'
            '[$off_phrase=[!{done,finished,over,[{dont,not} {want,wanna,feel like}]} to? {[!keep #LEM(talk,chat)], [!#LEM(talk,chat) {anymore,now,to you,with you}]}]],'
            '[$off_phrase=[!{wanna,want to,like to} {finish,end,stop} {this conversation}]],'
            '[$off_phrase=[!{wanna,want to} {be} {done,finished}]]}':{
                'state': 'stop_request_2',
                'score': 12,

                '`I am sorry, but I have a hard time understanding phrases like ` $off_phrase ` because it seems like '
                'you want to stop talking. If you actually do want to stop, you must say Alexa stop. Otherwise, I am '
                'happy to continue our conversation.`':{
                    'state': 'final_stop_instr',

                    'error': {
                        'state': 'stop_redirect',

                        '`Ok, well, let us get back to our conversation then. ` #GRET': 'SYSTEM:root'
                    }
                }
            },

            'error': 'stop_redirect'
        }
    }
}