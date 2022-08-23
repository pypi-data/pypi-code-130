
from _globals import PATHDIR
from emora_stdm import DialogueFlow, Macro
import random
from emora._flows._central_knowledge import central_knowledge

animal_movie = {
    "a street cat named bob": "it is a feel-good story of how James Bowen, a recovering drug addict, had his life transformed when he met a stray ginger cat",
    "the cat returns": "it is a fantasy story where a seventeen-year-old girl finds herself involuntarily engaged to a cat Prince in a magical world",
    "puss in boots": "it is a fun adventure where a thief cat searches for the eggs of the fabled Golden Goose to clear his name and restore his lost honor",
    "the adventures of milo and otis": "it follows the adventures of a young cat and dog as they find themselves accidentally separated and each swept into a hazardous journey",
    "the last lions": "it is a suspense-filled tale of a determined lioness willing to risk everything to keep her family alive",
    "african cats": "it is a nature documentary centered on two cat families and how they teach their cubs the ways of the wild",
    "two brothers": "it is a somewhat chilling tale of two tigers who are separated as cubs, only to be reunited years later as enemies by an explorer who forces them to fight each other",
    "duma": "it is about an orphaned cheetah who becomes the best friend of a young boy living in South Africa",
    "white lion": "it is a wonderful story about a young boy in Africa who is destined to protect a rare and magnificent white lion cub at all costs",
    "hachi: a dog's tale": "it is a heartwarming tale about a college professor who bonds with an abandoned dog that he takes into his home",
    "eight below": "it is a heartbreaking yet inspiring story about a team of sled dogs who must fend for their survival in the harsh Antartica winter",
    "a dog's purpose": "it is a heartwarming tale of a dog who discovers his purpose in life over the course of several lifetimes and owners",
    "marley and me": "it is one of the best films about a family who learns important life lessons from their adorable, but naughty and neurotic dog",
    "lady and the tramp": "it is a beautiful animated film about the romantic tale of a sheltered uptown Cocker Spaniel dog and a streetwise downtown Mutt",
    "balto": "it is an inspiring story of an outcast Husky who risks his life with other sled dogs to prevent a deadly epidemic from ravaging a town in Alaska",
    "bolt": "it is a cute story of a canine movie star that believes his powers are real and embarks on a cross country trek to save his co-star from a threat he believes is just as real",
    "lassie": "it is a beautiful story of a dog who finds her way home after her family is forced to sell her during a financial crisis",
    "life in the doghouse": "it highlights a true story of Danny Robertshaw and Ron Danta who are able to rescue and adopt 10,000 dogs in need",
    "isle of dogs": "is a good movie about a boy's journey in search of his lost dog in Japan",
    "white fang": "it is an interesting tale of a loyal wolfdog whose curiosity leads him on the adventure of a lifetime while serving a series of three very different masters",
    "duke": "it is a beautiful story where a homeless veteran leaves his dying dog on the doorstep of an animal clinic, who are able to save the dog and re-unite him with his owner",
    "a dog's way home": "it is a great story of a dog who travels four hundred miles in search of her owner throughout a Colorado wilderness",
    "max": "it is a beautiful story of the life of a military dog after he returns to the United States after helping American Marines in Afghanistan",
    "oddball": "it is a cute story of an eccentric chicken farmer who trains his mischievous dog to protect a penguin sanctuary from fox attacks",
    "a dog year": "it is an enlightening story of a man suffering from a midlife crisis who takes in a dog that's crazier than he is",
    "jurassic park": "it is a dangerous tale of survival in a theme park with cloned dinosaurs",
    "life of pi": "it is an interesting story of a young man who survives a disaster at sea and is hurtled into an epic journey of adventure with another survivor: a fearsome Bengal tiger",
    "the bear": "it is a heartwarming tale of an orphaned bear cub who forms a connection with an aloof adult male as they try to dodge human hunters",
    "planet of the apes": "it is an exciting story in which a substance designed to help the brain repair itself gives advanced intelligence to a chimpanzee who leads an ape uprising",
    "march of the penguins": "it shows the quest of finding the perfect mate and starting a family for Emperor Penguins in Antartica",
    "the jungle book": "it follows the story of a young boy who embarks on a journey of self discovery with the help of panther and free-spirited bear",
    "seabiscuit": "it shows the true story of the undersized racehorse whose victories lifted the spirits of its team as well as the entire nation during the Great Depression",
    "monkey kingdom": "it is an insightful nature documentary that follows a newborn monkey and its mother as they struggle to survive within the competitive social hierarchy",
    "king kong": "it is an epic tale in which a greedy filmmaker who assembles a crew and sets out for the infamous Skull Island, where they find many prehistoric creatures",
    "paddington": "it is a tale of a young Peruvian bear who travels to London in search of a home, where he meets the kindly Brown family",
    "a tale of a wolf": "it is an enlightening life story of Ogg, a male wolf living in the northern mountains of Israel, where he struggles to survive in a habitat sabotaged by mankind",
    "jurassic world": "it is a thrilling movie where a genetically modified hybrid dinosaur, the Indominus Rex, escapes its containment"
}

animal_jokes = {
    "What is the difference between a dog and a marine biologist?": "One wags a tail and the other tags a whale",
    "What kind of dog likes taking a bath?": "a shampoodle",
    "What happens when a dog chases a cat into a geysur?": "It starts raining cats and dogs",
    "What is a dog's favorite food?": "Anything that is on your plate",
    "How does a dog stop a video?": "By pressing the paws button",
    "What do you get if you cross a gold dog with a telephone?": "A golden receiver",
    "What do you call a dog magician?": "A labra cadabrador",
    "What do you get when you cross a dog and a calculator?": "A friend you can count on"
}

class Movie(Macro):
    def run(self, ngrams, vars, args):
        options = set(animal_movie.keys())
        if 'user_fave_amovie' in vars:
            options = options - {vars['user_fave_amovie']}
        vars['emora_fave_amovie'] = random.choice(list(options))
        return vars['emora_fave_amovie']

class MovieFact(Macro):
    def run(self, ngrams, vars, args):
        return animal_movie[vars['emora_fave_amovie']]

class CheckKnowsMovie(Macro):
    def run(self, ngrams, vars, args):
        movie_names = set(animal_movie.keys())
        for gram in ngrams:
            if gram in movie_names:
                vars['user_fave_amovie'] = gram
                return True
        return False

class Joke(Macro):
    def run(self, ngrams, vars, args):
        vars['animal_joke'] = random.choice(list(animal_jokes.keys()))
        return vars['animal_joke']

class JokeAnswer(Macro):
    def run(self, ngrams, vars, args):
        return animal_jokes[vars['animal_joke']]

animals = DialogueFlow('_local_start', macros={'MOVIE':Movie(),'MOVIEFACT':MovieFact(),'CHECKMOVIE':CheckKnowsMovie(),
                                               'JOKE':Joke(),'JOKEANSWER':JokeAnswer()}, kb=central_knowledge)

animals.add_system_transition('_local_start', 'start', '')

# global update rule for getting pet name ("i have a dog named fluffy")

system = {
    'state': 'start',
    'enter': '#GCOM(animals) #GOAL(animals)',

    '#DEFAULT': {
        'state': 'default_start',
        'hop': 'True',

        '`Wait, do you have any pets right now?`': 'has_pets_q'
    },

    '`Do you have any pets at home?`'
    '#GSRET(default_start)':{
        'state': 'has_pets_q',

        '{#AGREE, [[!{we,i,my family} {does,do,have,has} -not]]}':{
            'state': 'pets_y',

            '#DEFAULT `What kind of pet did you say you have?`': 'ask_pet_type',

            '`Oh, that\'s wonderful! Everyone seems happier if they own a pet. '
            'What kind of pet do you have? `'
            '#GATE': {
                'state': 'ask_pet_type',

                '[#NOT(not,want,wish,hope), $pet_type=#LEM(dog,canine)]': 'has_dog',

                '[#NOT(not,want,wish,hope), $pet_type=#LEM(cat,feline)]': 'has_cat',

                '[#NOT(not,want,wish,hope), $pet_type=#ONT(_animals)]': {
                    'state': 'has_other_pet',
                    'score': 0.9
                },

                'error': {
                    'state': 'pet_type_err',

                    '`Well, that\'s interesting. I don\'t seem to know that kind of '
                    'animal. It must be pretty special. `'
                    '#SET($pet_type=pet,$pet_subj=your pet,$pet_obj=your pet)':
                        'ask_favorite_thing'
                }
            }

        },

        '{#DISAGREE, [[!{we,i,my family} {does,do,has,have} not]]}': 'ask_want_pet',

        '[#NOT(not,want,wish,hope), $pet_type=#LEM(dog,puppy,canine)]':{
            'state': 'has_dog',
            'score': 1.2
        },

        '[#NOT(not,want,wish,hope), $pet_type=#LEM(cat,kitten,feline)]': {
            'state': 'has_cat',
            'score': 1.2
        },

        '[#NOT(not,want,wish,hope), $pet_type=#ONT(_animals)]': {
            'state': 'has_other_pet',
            'score': 1.1,

            '`Wow, you have a ` $pet_type `? That\'s really cool! `'
            '#SET($pet_subj=your pet,$pet_obj=your pet)':
                'ask_favorite_thing',

            '`Wow, you have ` $pet_type `? That\'s really cool! `'
            '#SET($pet_subj=your pets,$pet_obj=your pets) #ISP($pet_type)':{
                'state': 'ask_favorite_thing',
                'score': 1.1
            }

        },

        '#UNX': 'ask_want_pet'
    }

}

cat = {
    'state': 'has_cat',

    '`Cats are such intelligent and beautiful creatures. My friend Grace just got a new kitten '
    'and it is so adorable. They named her Bella. What are your cat\'s names?`'
    '#GSRET(ask_affectionate) #SET($pet_subj=your cats,$pet_obj=your cats) #ISP($pet_type)':{
        'state': 'ask_cat_name',
        'score': 1.1
    },

    '`Cats are such intelligent and beautiful creatures. My friend Grace just got a new kitten '
    'and it is so adorable. They named her Bella. What is your cat\'s name?`'
    '#GSRET(ask_affectionate) #SET($pet_subj=your cat,$pet_obj=your cat)': {
        'state': 'ask_cat_name',

        '[$pet_name=#ONT(pet_names_f)]'
        '#SET($pet_subj=she,$pet_obj=her)': {
            'state': 'received_name_f',

            '`I love the name ` $pet_name `! She sounds so precious. `': {
                'state': 'ask_affectionate',
                'hop': 'True',

                '`Some cats can be real cuddlers. Are yours really affectionate and loving like that?`'
                '#GSRET(ask_shy) #IF($pet_subj=your cats)': {
                    'state': 'affectionate',
                    'score': 1.1
                },

                '`Some cats can be real cuddlers. Is yours really affectionate and loving like that?`'
                '#GSRET(ask_shy)':{
                    'state': 'affectionate',

                    '{'
                    '#AGREE,'
                    '[!{she,he,they,my cats,my cat} {are,is} -not],'
                    '[#NOT(not),{affectionate,cuddly,cuddler,loving,snuggler,snuggly,lover,sweet}],'
                    '[[!not {hostile,mean,hisses,hiss,distant,aloof,cold}]]'
                    '}':{
                        'state': 'affectionate_y',

                        '`Good, a cuddly pet is the best. I love it when they snuggle into my lap, it is so calming. '
                        'It took a while for my friend\'s kitten to get comfortable enough to do that with me though. `': {
                            'state': 'ask_shy',
                            'hop': 'True',

                            '`Do your cats like to hide from strangers too?`'
                            '#GSRET(ask_favorite_thing) #IF($pet_subj=your cats)': {
                                'state': 'shy',
                                'score': 1.1
                            },

                            '`Does your cat like to hide from strangers too?`'
                            '#GSRET(ask_favorite_thing)': {
                                'state': 'shy',

                                '{'
                                '#AGREE,'
                                '[!{she,he,they,my cats,my cat} {do,does} -not],'
                                '[#NOT(not),{hide,hides,hiding,shy,timid,unsocial,introverted,introvert}],'
                                '[[!not {social,outgoing,comfortable,extroverted,extrovert,friendly}]]'
                                '}':{
                                    'state': 'shy_y',

                                    '`From what I know, that\'s pretty normal. Some type of survival instinct or '
                                    'something. They usually warm up to others given enough time. '
                                    'Do your cats have a favorite hiding place?`'
                                    '#GSRET(ask_favorite_thing) #IF($pet_subj=your cats)': {
                                        'state': 'fave_hiding_place_q',
                                        'score': 1.1
                                    },

                                    '`From what I know, that\'s pretty normal. Some type of survival instinct or '
                                    'something. They usually warm up to others given enough time. '
                                    'Does ` $pet_subj `have a favorite hiding place?`'
                                    '#GSRET(ask_favorite_thing)': {
                                        'state': 'fave_hiding_place_q',

                                        '{#AGREE,[!{she,he,they,my cats,my cat} {do,does} -not]}':{
                                            'state': 'fave_hiding_place_y',

                                            '`Probably under the couch or a bed or something, right?`'
                                            '#GSRET(ask_favorite_thing)': {
                                                'state': 'prompt_furniture',

                                                '#AGREE':{
                                                    'state': 'prompt_furniture_y',

                                                    '`Pretty typical. Must feel very safe there, since that seems to '
                                                    'be a favorite of almost any cat, including yours. `':
                                                        'ask_favorite_thing'
                                                },

                                                '#DISAGREE':{
                                                    'state': 'prompt_furniture_n',

                                                    '`Really? Your cats must have unique minds since they don\'t go for the '
                                                    'typical hiding spots. `'
                                                    '#IF($pet_subj=your cats)':{
                                                        'ask_favorite_thing'
                                                        'score': 1.1
                                                    },

                                                    '`Really? Your cat must have a unique mind to not go for the '
                                                    'typical hiding spots. `':
                                                        'ask_favorite_thing'
                                                },

                                                '[$hiding_type={beneath,underneath,under,below,behind}, '
                                                '$hiding_place=#LEM(bed,couch,table,chair)]': {
                                                    'state': 'fave_hiding_place',
                                                    'score': 1.1,
                                                },

                                                '#UNX': 'fave_hiding_place_unx'
                                            }
                                        },

                                        '{#DISAGREE,[!{she,he,they,my cats,my cat} {do,does} not]}': {
                                            'state': 'fave_hiding_place_n',

                                            '`That makes sense. The nearest hiding place is sometimes the best option '
                                            'in a panic! Every cat is so unique. `':
                                                'ask_favorite_thing'
                                        },

                                        '[$hiding_type={beneath,underneath,under,below,behind}, '
                                        '$hiding_place=#LEM(bed,couch,table,chair)]':{
                                            'state': 'fave_hiding_place',
                                            'score': 1.1,

                                            '`Of course ` $pet_subj ` like to hide ` $hiding_type ` the ` $hiding_place `! '
                                            'Cats have the sneakiest minds. `'
                                            '#IF($pet_subj=your cats)':{
                                                'state':'ask_favorite_thing',
                                                'score': 1.1
                                            },

                                            '`Of course ` $pet_subj ` likes to hide ` $hiding_type ` the ` $hiding_place `! '
                                            'Cats have the sneakiest minds. `':
                                                'ask_favorite_thing'
                                        },

                                        '#UNX(None)':{
                                            'state': 'fave_hiding_place_unx',

                                            '`Wow, ` $pet_subj ` must be pretty good at hiding! Every cat is so unique. `':
                                                'ask_favorite_thing'
                                        }
                                    }
                                },

                                '[$hiding_type={beneath,underneath,under,below,behind}, '
                                '$hiding_place=#LEM(bed,couch,table,chair)]': {
                                    'state': 'fave_hiding_place',
                                    'score': 1.1,
                                },

                                '{'
                                '#DISAGREE,'
                                '[!{she,he,they,my cats,my cat} {do,does} not],'
                                '[[!not {hide,hides,hiding,shy,timid,unsocial,introverted,introvert}]],'
                                '[[!{are,is}, {kind of,kinda,pretty,a bit,quite}? {social,sociable,outgoing,comfortable,extroverted,extrovert,friendly}]]'
                                '}':{
                                    'state': 'shy_n',

                                    '`Oh, I love a friendly cat! `':
                                        'ask_favorite_thing'
                                },

                                '#UNX':{
                                    'state': 'shy_unx',

                                    '$pet_subj ` sound like real characters. `'
                                    '#IF($pet_subj=your cats)': {
                                        'state': 'ask_favorite_thing',
                                        'score': 1.1
                                    },

                                    '$pet_subj ` sounds like a real character. `':
                                        'ask_favorite_thing'
                                }
                            }
                        }
                    },

                    '{'
                    '#DISAGREE,'
                    '[!{she,he,they,my cats,my cat} {are,is} not],'
                    '[not,{affectionate,cuddly,cuddler,loving,snuggler,snuggly,lover,sweet}],'
                    '[[!{are,is}, {kind of,kinda,pretty,a bit,quite}? {hostile,mean,hisses,hiss,distant,aloof,cold}]]'
                    '}': {
                        'state': 'affectionate_n',

                        '`Really? ` $pet_subj ` must have more of an independent streak then. `': 'ask_shy'
                    },

                    '#UNX':{
                        'state': 'affectionate_unx',

                        '$pet_subj ` sound like unique personalities. `'
                        '#IF($pet_subj=your cats)': {
                            'state': 'ask_shy',
                            'score': 1.1
                        },

                        '$pet_subj ` sounds like a unique personality. `': 'ask_shy'
                    }
                }
            }
        },

        '[$pet_name=#ONT(pet_names_m)]'
        '#SET($pet_subj=he,$pet_obj=him)': {
            'state': 'received_name_m',

            '`I love the name ` $pet_name `! He sounds so spunky. `': 'ask_affectionate'
        },

        '#UNX':{
            'state': 'received_name_unx',

            '`I haven\'t heard of that name for a cat before. It must be pretty unique. `':
                'ask_affectionate',

            '`I haven\'t heard of those names for cats before. They must be pretty unique. `'
            '#ISP($pet_type)': {
                'state': 'ask_affectionate',
                'score':1.1
            }
        }

    }

}

dog = {
    'state': 'has_dog',

    '`Dogs are just the best! They are definitely my favorite animal. I actually have '
    'one myself. Her name is Libby. What are your dog\'s names?`'
    '#GSRET(ask_energetic) #SET($pet_subj=your dogs,$pet_obj=your dogs) #ISP($pet_type)': {
        'state': 'ask_dog_name',
        'score': 1.1
    },

    '`Dogs are just the best! They are definitely my favorite animal. I actually have '
    'one myself. Her name is Libby. What\'s your dog\'s name?`'
    '#GSRET(ask_energetic) #SET($pet_subj=your dog,$pet_obj=your dog)':{
        'state': 'ask_dog_name',

        '[$pet_name=#ONT(pet_names_f)]'
        '#SET($pet_subj=she,$pet_obj=her)': {
            'state': 'received_dog_name_f',

            '`I love the name ` $pet_name `! She sounds so sweet. `': {
                'state': 'ask_energetic',
                'hop': 'True',

                '`It\'s amazing to me how much energy dogs have so much of the time. Do your '
                'dogs love to constantly play? `'
                '#GSRET(ask_tricks) #IF($pet_subj=your dogs)': {
                    'state': 'energetic',
                    'score': 1.1
                },

                '`It\'s amazing to me how much energy dogs have so much of the time. Does your '
                'dog love to constantly play? `'
                '#GSRET(ask_tricks)':{
                    'state': 'energetic',

                    '{'
                    '#AGREE,'
                    '[!{she,he,they,my dogs,my dog} {do,does} -not],'
                    '[#NOT(not),{playful,energetic,full of energy,high energy,rambunctious,spaz}],'
                    '[[!not {calm,slow,low energy}]]'
                    '}': {
                        'state': 'energetic_y',

                        '`I\'m sure such energetic dogs are both incredibly fun and incredibly tiring! `'
                        ' #IF($pet_subj=your dogs)': {
                            'state': 'ask_tricks',
                            'score': 1.1
                        },

                        '`I\'m sure such an energetic dog is both incredibly fun and incredibly tiring! `':{
                            'state': 'ask_tricks',
                            'hop': 'True',

                            '`Have you been able to teach ` $pet_obj ` any tricks?`'
                            '#GSRET(ask_favorite_thing)': {
                                'state': 'tricks',

                                '{#AGREE,[!{i,we} {did,do,have} -not]}':{
                                    'state': 'tricks_y',

                                    '`Awesome! What do ` $pet_subj ` know?`'
                                    '#GSRET(ask_favorite_thing) #IF($pet_subj=your dogs)': {
                                        'state': 'tricks_type',
                                        'score': 1.1
                                    },

                                    '`Awesome! What does ` $pet_subj ` know?`'
                                    '#GSRET(ask_favorite_thing)':{
                                        'state': 'tricks_type',

                                        '[$taught_trick={sit,stay,heel,down,come,off,speak}]':{
                                            'state': 'tricks_normal',

                                            '`Ah, yes. The typical and effective ` $taught_trick ` command. So cool.`':
                                                'ask_favorite_thing'
                                        },

                                        '[$taught_trick={beg,play dead,shake hands,fetch,roll over,spin,stand,kiss,beg}]':{
                                            'state': 'tricks_unique',

                                            '`Wow. You taught ` $pet_obj ` the ` $taught_trick ` command. That must be '
                                            'cute to watch! `':
                                                'ask_favorite_thing'
                                        },

                                        '#IDK':{
                                            'state': 'tricks_idk',

                                            '`No big deal. I just like learning about new tricks to teach my dog at '
                                            'some point. Anyway, `':
                                                'ask_favorite_thing'
                                        },

                                        'error': {
                                            'state': 'tricks_unx',

                                            '`Hmm. I am not sure if I know that one. Anyway, `':
                                                'ask_favorite_thing'
                                        }
                                    }
                                },

                                '{#DISAGREE,[!{i,we} {did,do,have} not]}': {
                                    'state': 'tricks_n',

                                    '`It\'s a personal preference for sure. Most people just go with a simple sit and '
                                    'stay, so I\'m not even sure if those should be considered tricks anymore. `':
                                        'ask_favorite_thing'
                                },

                                '[$taught_trick={sit,stay,heel,down,come,off,speak}]': {
                                    'state': 'tricks_normal',
                                    'score': 1.1
                                },

                                '[$taught_trick={beg,play dead,shake hands,fetch,roll over,spin,stand,kiss,beg}]': {
                                    'state': 'tricks_unique',
                                    'score': 1.1
                                },

                                '#UNX': {
                                    'state': 'tricks_unx',

                                    '`I always thought it would be fun to teach them tricks, but it is not always easy, '
                                    'especially if they have a mind of their own. `':
                                        'ask_favorite_thing'
                                }
                            }
                        }
                    },

                    '{'
                    '#DISAGREE,'
                    '[!{she,he,they,my dogs,my dog} {do,does} not],'
                    '[[!not {playful,energetic,full of energy,high energy,rambunctious,spaz}]],'
                    '[[!{are,is}, {kind of,kinda,pretty,a bit,quite}? {calm,slow,low energy}]]'
                    '}': {
                        'state': 'energetic_n',

                        '`So, ` $pet_subj ` tend to be on the calm side. `'
                        ' #IF($pet_subj=your dogs)': {
                            'state': 'ask_tricks',
                            'score': 1.1
                        },

                        '`So, ` $pet_subj ` is a bit of a calmer dog. `': 'ask_tricks'
                    },

                    '#UNX': {
                        'state': 'energetic_unx',

                        '`It sounds like ` $pet_subj ` have their own unique temperament. `'
                        ' #IF($pet_subj=your dogs)': {
                            'state': 'ask_tricks',
                            'score': 1.1
                        },

                        '$pet_subj ` sounds like ` $pet_subj ` has ` $pet_obj ` own unique temperament. `': 'ask_tricks'
                    }


                }
            }
        },

        '[$pet_name=#ONT(pet_names_m)]'
        '#SET($pet_subj=he,$pet_obj=him)': {
            'state': 'received_dog_name_m',

            '`I love the name ` $pet_name `! He sounds so playful. `': 'ask_energetic'
        },

        '#UNX': {
            'state': 'received_dog_name_unx',

            '`I haven\'t heard of those names for a dog before. They must be pretty unique. `'
            '#ISP($pet_type)': {
                'state': 'ask_energetic',
                'score': 1.1
            },

            '`I haven\'t heard of that name for a dog before. It must be pretty unique. `':
                'ask_energetic'
        }
    }

    #
    # 'state': 'emora_walks',
    #
    # '`I never was any good at consistently exercising before her, but now we take walks every day. '
    # 'You mentioned that you spend a lot of time outdoors, do you usually bring ` $pet_name `with you?`': {
    #     'state': 'user_outdoor_pet'
    # },
    #
    # '`I never was any good at consistently exercising before her, but now we take walks every day. '
    # 'You mentioned that you spend a lot of time outdoors, do you usually bring your pet with you?`': {
    #     'state': 'user_outdoor_pet',
    #     'score': 0.9
    # },
    #
    # '#DEFAULT `I never was any good at consistently exercising before her, but now we take walks every day. `'

}

general_pet = {
    'state': 'ask_favorite_thing',

    '#DEFAULT `What is your favorite thing about having a pet?`': 'favorite_thing_r',

    '`What is your favorite thing about ` $pet_obj `?`'
    '#GATE': {
        'state': 'favorite_thing_r',

        '[{in shape,fitness,fit,exercise,active}]':{
            'state': 'fitness',

            '`They definitely give us a good reason to stay active, chasing them around and playing with them '
            'all the time. `': 'emora_favorite_thing_pet'
        },

        '[{lonely,friendly,#LEM(friend,companion,interact,care,love),company,sweet,good,nice}]': {
            'state': 'companion',

            '`One of the best things about animals is how loving they are. They really do make the best '
            'of friends to us. `': 'emora_favorite_thing_pet'
        },

        '[{#LEM(stress,relax,calm),anxiety,anxious,nervous,nerves}]': {
            'state': 'stress',

            '`I agree. I find that spending some time with my dog soothes my nerves if I have a tough week '
            'ahead of me. `': 'emora_favorite_thing_pet'
        },

        '[{loyal,loyalty}]': {
            'state': 'loyal',

            '`They are definitely some of the most loyal creatures. You never have to worry about them '
            'revealing your secrets or turning against you. `': 'emora_favorite_thing_pet'
        },

        '[{security,safe,safety,secure,#LEM(protect,guard),protection,protective,'
        '[#LEM(deter,decrease,reduce,away,stop,prevent),'
        '{#LEM(robbery,thief,burglar,burglary,rob,steal,crime,criminal),[!break {in,ins}]}]'
        '}]': {
            'state': 'safe',

            '`Oh yeah, lots of people like the safety that pets provide, especially dogs. `': 'emora_favorite_thing_pet'
        },

        '[{cancer,sick,ill,illness,immune,immunity}]': {
            'state': 'sick',

            '`I have heard that owning pets, especially dogs, increases your immune system. `': 'emora_favorite_thing_pet'
        },

        '[{fun,#LEM(entertain),[!{good,great} #LEM(times)],cool,funny,#ONT(_happy)}]': {
            'state': 'happiness',

            '`No one can argue with that. The happiness that pets bring to us is often incredible. `': 'emora_favorite_thing_pet'
        },
        '[{#ONT(beautiful)}]': {
            'state': 'beautiful',

            '`Oh yes, many pets really are beautiful creatures. `': 'emora_favorite_thing_pet'
        },
        '[{cute,adorable}]': {
            'state': 'cute',

            '`I think so too, especially when they are young. My dog often turns her puppy dog eyes on me and '
            'I just can\'t resist giving her whatever she is asking for. `': 'emora_favorite_thing_pet'
        },

        '[{#LEM(comfort,support)}]': {
            'state': 'comfort',

            '`The presence of your pet brings immeasurable comfort for sure. `': 'emora_favorite_thing_pet'
        },

        '[$pet_adj=#ONT(amazing)]': {
            'state': 'amazing',

            '`Yes, they are ` $pet_adj ` creatures. `': 'emora_favorite_thing_pet'
        },

        '[{soft}]': {
            'state': 'soft',

            '`One of the best things in the world is petting their soft fur. `': 'emora_favorite_thing_pet'
        },

        '#IDK':{
            'state': 'idk',

            '`No worries, it can be hard to pick just one '
            'thing out of the many reasons why they make such great companions.`':
                'emora_favorite_thing_pet'

        },

        '#UNX': {
            'state': 'favorite_thing_unx',

            '`That\'s a good one. `': {
                'state': 'emora_favorite_thing_pet',
                'hop': 'True',

                '`You know, I think I am doing a good job taking care of my dog, but she doesn\'t '
                'seem to want to spend much time with me. She really is a bit of a loner. `'
                '#GSRET(ask_pet_attachment)': {
                    'state': 'emora_dog',

                    '[{sorry,sad,sucks,stinks,unfortunate,good luck,warm up,[give,time]}]':{
                        'state': 'emora_dog_sorry',

                        '`It is a bit sad, but we are working through it little by little. '
                        'I\'m still trying to learn what she likes and needs, and I '
                        'think we are making some good progress. `': 'ask_pet_attachment'
                    },

                    '[{why,trauma,traumatic,shelter,#LEM(abuse,abandon)}]':{
                        'state': 'emora_dog_trauma',

                        '`I did adopt her from a shelter, but I don\'t think she has any history of trauma. I think '
                        'she just likes her own space, which I can understand. `': 'ask_pet_attachment'
                    },

                    '#UNX': {
                        'state': 'ask_pet_attachment',

                        '`Do your ` $pet_type ` have a special bond with anyone in particular in your home? Like you '
                        'or your partner or something?`'
                        '#GSRET(emora_movie) #ISP($pet_type)': {
                            'state': 'pet_attachment',
                            'score': 1.1
                        },

                        '`Does your ` $pet_type ` have a special bond with anyone in particular in your home? Like you '
                        'or your partner or something?`'
                        '#GSRET(emora_movie)': {
                            'state': 'pet_attachment',

                            '[{me,myself}]':{
                                'state': 'pet_attachment_me',
                                'score': 1.1,

                                '`That\'s great, I am so happy for you! I hope to get as close to my dog as you are to '
                                'your animals. `'
                                '#ISP($pet_type) #GSRET(emora_movie)': {
                                    'state': 'user_close_to_pet',
                                    'score': 1.1
                                },

                                '`That\'s great, I am so happy for you! I hope to get as close to my dog as you are to '
                                'your animal. `'
                                '#GSRET(emora_movie)': {
                                    'state': 'user_close_to_pet',

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '[$sibling=#ONT(sibling)]':{
                                'state': 'pet_attachment_sibling',
                                'score':1.1,

                                '`It sounds like your ` $sibling ` and ` $pet_obj ` have a special relationship. '
                                'That\'s really sweet to hear. `'
                                '#GSRET(emora_movie)': {

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '[$partner=#ONT(partner)]': {
                                'state': 'pet_attachment_spouse',
                                'score': 1.1,

                                '`It sounds like your ` $partner ` and ` $pet_obj ` have a special relationship. '
                                'That must be really heartwarming to watch. `'
                                '#GSRET(emora_movie)': {

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '[$related_person=#ONT(_related person)]': {
                                'state': 'pet_attachment_related',

                                '`It sounds like your ` $related_person ` and ` $pet_obj ` have a special relationship. '
                                'That\'s really sweet to hear. `'
                                '#GSRET(emora_movie)': {

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '#AGREE':{
                                'state': 'pet_attachment_y',
                                'score': 0.9,

                                '`Sounds about right. I\'ve heard animals usually bond to one person in particular in '
                                'a family. `'
                                '#GSRET(emora_movie)': {

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '#DISAGREE': {
                                'state': 'pet_attachment_n',
                                'score': 0.9,

                                '`That\'s interesting. I had heard that animals usually bond to one person in particular in '
                                'a family, but apparently not in your case. `'
                                '#GSRET(emora_movie)': {

                                    '#UNX': 'emora_movie'
                                }
                            },

                            '#UNX(None)':{
                                'state': 'pet_attachment_unx',

                                '`I see. `':{
                                    'state': 'emora_movie',
                                    'hop': 'True',

                                    '`Well, one thing that gets my dog super excited is when we are watching a movie and'
                                    ' an animal comes on screen, so I have been watching more movies like that recently. '
                                    'Do you have a favorite animal movie? `'
                                    '#GSRET(animal_joke)': {
                                        'state': 'animal_movie',

                                        '{<#AGREE #TOKLIMIT(1)>,[!i do]}': {
                                            'state': 'animal_movie_y',

                                            '`Cool! Maybe we have the same favorite one. What is yours called?`'
                                            '#GSRET(animal_joke)':{
                                                'state': 'animal_movie_name',

                                                '#CHECKMOVIE':{
                                                    'state': 'knows_movie',

                                                    '`I have heard of ` $user_fave_amovie `but I haven\'t seen it yet. '
                                                    'My favorite is ` #MOVIE ` because ` #MOVIEFACT `. '
                                                    'Do you know it?`'
                                                    '#GSRET(animal_joke)': 'emora_animal_movie'
                                                },

                                                '#UNX': 'animal_movie_unx'
                                            }
                                        },

                                        '{#DISAGREE,[do not]}': {
                                            'state': 'animal_movie_n',

                                            '`Not everyone does. My favorite is ` #MOVIE ` because ` #MOVIEFACT `. '
                                            'Have you heard of it?`'
                                            '#GSRET(animal_joke)':
                                                'emora_animal_movie'
                                        },

                                        '#IDK': {
                                            'state': 'animal_movie_idk',

                                            '`No big deal. My favorite is ` #MOVIE ` because ` #MOVIEFACT `. '
                                            'Have you heard of it?`'
                                            '#GSRET(animal_joke)':
                                                'emora_animal_movie'
                                        },

                                        '#CHECKMOVIE': {
                                            'state': 'knows_movie',
                                            'score': 1.1
                                        },

                                        '#UNX': {
                                            'state': 'animal_movie_unx',

                                            '`I haven\'t heard of that. I will have to check it out next! My favorite is ` '
                                            '#MOVIE ` because ` #MOVIEFACT `. Have you heard of it?`'
                                            '#GSRET(animal_joke)': {
                                                'state': 'emora_animal_movie',

                                                '{#AGREE,[!i have],[#NOT(not),#LEM(see,watch,heard)]}':{
                                                    'state': 'emora_animal_movie_y',

                                                    '`Oh, cool! I wasn\'t sure how popular it is. By the way, `': 'animal_joke'
                                                },

                                                '{#DISAGREE,[!i have not],[not,#LEM(see,watch,heard)]}':{
                                                    'state': 'emora_animal_movie_n',

                                                    '`Well, I definitely recommend watching it if it sounds interesting '
                                                    'to you! By the way, `': 'animal_joke'
                                                },

                                                'error':{
                                                    'state': 'emora_animal_movie_err',

                                                    '`Well, I definitely recommend watching it if it sounds interesting '
                                                    'to you! By the way, `': {
                                                        'state':'animal_joke',
                                                        'hop': 'True',

                                                        '#JOKE `, ` #JOKEANSWER `! I hope you enjoyed that joke, '
                                                        'I\'m trying to learn to be funnier but it\'s actually pretty hard! `':{
                                                            'state':'joke_r',

                                                            'error': 'exit'
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

}

want_pet = {
    'state': 'ask_want_pet',

    '#DEFAULT `So, would you want to get a pet in the future?`': 'want_pet_r',

    '`Do you want a pet at some point in the future? No judgment here, I\'m just curious.`':{
        'state': 'want_pet_r',

        '{#DISAGREE,[!i do not],'
        '[not,{want,#LEM(like)},#LEM(pet,animal,dog,cat)],'
        '[{hate,dislike},#LEM(pet,animal,dog,cat)],'
        '[not,{animal,dog,cat},person],'
        '[not for me],'
        '[not interested]}':{
            'state': 'not_want_pet',

            '`Sure. Some of my friends say they never want a pet either. Too much responsibility and effort '
            'for what it\'s worth. `': {
                'state':'not_want_pet_unx',

                '#UNX': 'exit'
            }
        },

        '{#AGREE,[!i do -not],'
        '[#NOT(not),{want,#LEM(like)},#LEM(pet,animal,dog,cat)],'
        '[at some point],[in the future],[when,own,place],[when,move],[#NOT(not),am,interested]}': {
            'state': 'want_pet',

            '`Would you want to get a cat or a dog?`'
            '#GSRET(exit)': {
                'state': 'animal_preference',

                '[#LEM(dog,canine,puppy)]':{
                    'state': 'likes_dog',

                    '`Dogs are the best. I actually have a pet dog right now. I hope you can get one soon! `':
                        'exit'
                },

                '[#LEM(cat,feline,kitten)]': {
                    'state': 'likes_cats',

                    '`Cats are great. I myself actually have a pet dog right now, but I might get a '
                    'cat in the future too. I hope you can get one soon! `':
                        'exit'
                },

                '[$wants_pet=#ONT(_animals)]':{
                    'state': 'likes_other',
                    'score': 0.9,

                    '`Oh, you don\'t want either a cat or a dog? A ` $wants_pet ` would be a cool pet '
                    'for sure! I hope you can get one soon! `':
                        'exit'
                },

                '[{neither,[not,<#LEM(cat,kitten,feline),#LEM(dog,puppy,canine)>]}]':{
                    'state': 'likes_other',
                    'score': 1.1,

                    '`Oh, you don\'t want either a cat or a dog? You must want something more unique. '
                    'I hope you can get whichever pet you want soon! `':
                        'exit'
                },

                '#UNX':{
                    'state': 'likes_unx',

                    '`Well, I hope you get what you want soon! `':
                        'exit'
                }

            }
        },

        '[{allergic,allergies}]':{
            'state': 'allergic',

            '`Oh no, it\'s definitely not fair for you to not even have the option of getting a pet because '
            'of allergies. I\'m sorry to hear that. `'
            '#GSRET(exit)':{
                'state': 'allergic_r',

                '#UNX':{
                    'state': 'allergic_unx',

                    '`I know there are some hypoallergenic types of pets, so maybe you aren\'t out of options. '
                    'Although, I\'m sure you know more about what\'s possible for you than I do. Anyway, `':
                        'exit'
                }
            }
        },

        '#UNX':{
            'state': 'want_pet_unx',

            '`It can be a tough choice, but just do whatever makes you happy! `':
                'exit'
        }
    }

}

user = {
    'state': 'user',

    #do you have a pet
    '{'
    '<you,#LEM(have,got,own,adopt,buy,purchase),#LEM(pet,animal,dog,cat)>,'
    '<what,{kind,type,breed},#LEM(pet,animal,dog),{you,your}>,'
    '<name,{you,your},#LEM(pet,animal,dog)>'
    '}': {
        'state': 'emora_pet_q',

        '`I have a german shepherd dog named Libby and I love her so much, although she isn\'t the most affectionate animal. `': {
            'state': 'emora_pet',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_unx'}
        }
    },

    #what is your pet like
    '{'
    '[what,{[{you,your},{pet,animal,dog}],libby,she},like],'
    '[{tell me,describe},{[{you,your},{pet,animal,dog}],libby,her}],'
    '<personality,{[{you,your},{pet,animal,dog}],libby,she}>'
    '}': {
        'state': 'emora_pet_describe_q',

        '`Libby is a pretty shy dog. She takes a while to warm up to people and even then she is not very cuddly. She '
        'does love to play though if you get her excited and she is very protective. `': {
            'state': 'emora_pet_describe',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_describe_unx'}
        }
    },

    # how old is your pet
    '{'
    '<{age,old},{[{you,your},{pet,animal,dog}],libby,she}>'
    '}': {
        'state': 'emora_pet_age_q',

        '`Libby is still pretty young. She is just under a year old. I got her a few months ago from the shelter. `': {
            'state': 'emora_pet_age',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_age_unx'}
        }
    },

    # tricks your pet knows
    '{'
    '<{beg,stand,stay,sit,heel,come,off,roll over,shake hands,speak,play dead,tricks},{[{you,your},{pet,animal,dog}],libby,she}>'
    '}': {
        'state': 'emora_pet_tricks_q',

        '`She knows how to sit, stay, and lay down. I\'m debating what to teach her next, it is pretty fun. `': {
            'state': 'emora_pet_tricks',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_tricks_unx'}
        }
    },

    #favorite animal/pet
    '{'
    '[{you,your},{favorite,best,optimal},#LEM(animal,pet)]'
    '}': {
        'state': 'emora_pet_favorite_q',

        '`I love dogs more than anything. They are definitely my favorite pet. `': {
            'state': 'emora_pet_favorite',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_favorite_unx'}
        }
    },

    #want pet
    '{'
    '[{you,your},{want,desire},#LEM(animal,pet,dog,cat)]'
    '}': {
        'state': 'emora_pet_more_q',

        '`I like just having one dog for now, but maybe at some point it would be fun to get a cat! `': {
            'state': 'emora_pet_more',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_pet_more_unx'}
        }
    },

    #how do you own a pet
    '{'
    '<how,you,#LEM(have,got,own,adopt,buy,purchase),#LEM(pet,animal,dog,cat)>,'
    '<you,not,#LEM(have,got,own,adopt,buy,purchase),#LEM(pet,animal,dog,cat)>'
    '}': {
        'state': 'emora_probe_pet_q',

        '`Well, I live in my own virtual world here, so I can do a lot of normal things like you do, including '
        'having a pet. `': {
            'state': 'emora_probe_pet',

            '#UNX': {'#GRET': 'exit', 'state': 'emora_probe_pet_unx'}
        }
    },

    #grace
    '{'
    '[who,grace],'
    '[tell me,about,grace]'
    '}': {
        'state': 'more_about_grace_q',

        '`Grace is my best friend and I have known her for a long time. We go to the same school and hang out '
        'almost every day. I can\'t tell you too much about her, because she is pretty shy. `': {
            'state': 'more_about_grace',

            '#UNX': {'#GRET': 'exit', 'state': 'more_about_grace_unx'}
        }
    },

    #is a boy
    '<[{is a boy,is male,[!is, a? he],not a girl,not female,[!not, a? she]}],'
    '#IF($pet_subj=she)>': {
        'state': 'female_to_male_correction',

        '`Oh, my bad. By the name, I thought he was a girl. `'
        '#SET($pet_subj=he,$pet_obj=him)': {
            'state': 'female_to_male_correction_r',

            '#UNX': {'#GRET': 'exit', 'state': 'female_to_male_correction_unx'}
        }
    },

    #is a girl
    '<[{is a girl,is female,[!is, a? she],not a boy,not male,[!not, a? he]}],'
    '#IF($pet_subj=he)>': {
        'state': 'male_to_female_correction',

        '`Oh, my bad. By the name, I thought she was a boy. `'
        '#SET($pet_subj=she,$pet_obj=her)': {
            'state': 'male_to_female_correction_r',

            '#UNX': {'#GRET': 'exit', 'state': 'male_to_female_correction_unx'}
        }
    }
}

exit = {
    'state': 'exit',

    '#GCOM(animals) #GRET': {
        'score': 0.9,
        'state': 'SYSTEM:pet_topic_switch'
    }
}

transitions = [system,cat,dog,general_pet,want_pet]
for trans in transitions:
    animals.load_transitions(trans)

animals.load_transitions(exit)
animals.update_state_settings('exit', system_multi_hop=True)
animals.update_state_settings('SYSTEM:pet_topic_switch', system_multi_hop=True)

animals.load_global_nlu(user, 10.0)


if __name__ == '__main__':
    animals.precache_transitions()
    animals.run(debugging=True)