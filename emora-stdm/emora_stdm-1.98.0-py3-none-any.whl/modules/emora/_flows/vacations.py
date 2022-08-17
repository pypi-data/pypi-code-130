from emora_stdm import DialogueFlow, Macro, KnowledgeBase
import random
from _globals import PATHDIR
from emora._flows._central_knowledge import central_knowledge



travel_database = {
    "houston": {
        "tourist_attraction": {
            "the theater district": "is a 17-block area in the heart of downtown houston which contains the bayou place entertainment complex as well as many restaurants and parks.",
            "hermann park": "is home to the houston zoo and the houston museum of natural science.",
            "space center houston": "includes many interactive exhibits including moon rocks and a shuttle simulator as well as special presentations that tell the story of NASAs manned space flight program."
        },
        "famous_food": {
            "tex-mex cuisine": "from texas and mexican is an american regional cuisine that derives from the culinary creations of the tejano people of texas.",
            "cajun food": "is a style of cooking named for the french-speaking acadian people deported by the british from acadia in canada to what is now called the acadiana region of louisiana."
        },
        "brief_intro": " texas.",
        "movie": {
            "urban cowboy": "was filmed in pasadena creatively chronicles the volatile relationship between the main characters bud and sissy a cowboy and cowgirl, respectively. arguably, it's one of the most famous iconic texas films out there."
        },
        "reason_for_travel": "it is the perfect city for a friends getaway, a couples retreat, or a family vacation."
    },
    "macau": {
        "tourist_attraction": {
            "the historic centre of macau": "showcases about thirty locations in Macau of high historical value."
        },
        "famous_food": {
            "macanese style portuguese chicken": "is an example of a chinese dish that draws from macanese influences, but is not part of macanese cuisine",
            "pork chop bun": "was adapted to use local ingredients, such as fresh seafood, turmeric, coconut milk, and adzuki beans. these adaptations produced macanese variations of traditional portuguese dishes including caldo verde, minchee, and cozido portuguesa."
        },
        "brief_intro": " southern china. ",
        "movie": {
            "the man with the golden gun": "was the first to put macau on hollywoods radar. starring roger moore in the lead role of james bond, macau was selected as a shooting location because of its prevalence of casinos."
        },
        "reason_for_travel": "it offers an exciting mix of portuguese and chinese cultures that you cannot find anywhere else in the world."
    },
    "new orleans": {
        "tourist_attraction": {
            "the french quarter": "has been designated as a national historic landmark, famous for its vibrant nightlife and colorful buildings.",
            "the natchez": "is an authentic steamboat that cruises the length of the city twice daily, playing calliope music.",
            "treme community": "contains the new orleans jazz national historical park and the new orleans african american museum."
        },
        "famous_food": {
            "creole cuisine": "is po boy and italian muffuletta sandwiches; gulf oysters on the half-shell, boiled crawfish, and other seafood as well as creole dishes.",
            "beignets": "are square-shaped fried pastries that could be called french doughnuts, served with coffee and chicory, known as cafe au lait."
        },
        "brief_intro": " Louisiana. ",
        "movie": {
            "interview with the vampire": ", a dramatic horror film, tells an epic vampire story where love, betrayal, loneliness, and hunger take louis de pointe du lac, a young indigo plantation owner, played by protagonist brad pitt, on a haunting adventure through the south of new orleans. "
        },
        "reason_for_travel": "it\'s cajun and creole cuisine, jazz music, and the architecture of the french quarter make it a very unique destination."
    },
    "london": {
        "tourist_attraction": {
            "the tower of london": "is a historic castle located on the north bank of the river thames in central london.",
            "british museum": "is a public institution dedicated to human history, art and culture.",
            "the national gallery": "is an art museum in central london that houses one of the greatest collections of paintings in the world. "
        },
        "famous_food": {
            "sunday roast with yorkshire pudding": "sunday roast is a true british classic. traditionally this meal is eaten any time from noon to 5 pm on sundays.",
            "fish and chips": "theres nothing that says british food like fish & chips. known the world over, this traditional british dish is on the top of any foodie list for visitors to london and the u.k.",
            "full english breakfast": "traditionally, you need to find a dish that incorporates: sausages, eggs, mushrooms, tomatoes, mushrooms, blood pudding, potatoes, and toast."
        },
        "brief_intro": " england. ",
        "movie": {
            "performance 1970": "is the ultimate london movie, a tale of rock stars and thieves, creativity and confusion, drug-fuelled fantasy and hard, ugly reality."
        },
        "reason_for_travel": "its cultural tourism is growing and many travellers go there to enjoy the british way of living."
    },
    "san francisco": {
        "tourist_attraction": {
            "golden gate bridge": "is possibly the most beautiful and certainly the most photographed bridge in the world.",
            "the alcatraz federal penitentiary": "is the most infamous prison in United States history and now a public museum with public tours."
        },
        "famous_food": {
            "sourdough bread with white clam chowder": ""
        },
        "brief_intro": " california. ",
        "movie": {
            "48 hours": "is a 1982 american buddy cop action comedy film directed by walter hill. it is joel silver's first film as a film producer."
        },
        "reason_for_travel": "san francisco is one of the highest rated american cities on world liveability rankings with many well-known attractions.",
    },
    "seattle": {
        "tourist_attraction": {
            "space needle": "is an icon of the city that is recognized far and wide, with views from the top of the city and surrounding landscape."
        },
        "famous_food": {
            "Seattle Dog, a cream cheese hot dog": ""
        },
        "brief_intro": "washington. ",
        "movie": {
            "sleepless in seattle": "is a 1993 american romantic comedy about a recently widowed man's son calls a radio talk-show in an attempt to find his father a partner."
        },
        "reason_for_travel": "the city is filled with exciting attractions, delicious food, and interesting locals."
    },
    "chicago": {
        "tourist_attraction": {
            "the willis tower": "has an observation deck open to tourists year round with high up views overlooking chicago and lake michigan.",
            "navy pier": "is a 3,000 foot long pier that houses retail stores, restaurants, museums, exhibition halls and auditoriums. ",
            "the bean": "is a giant silver sculpture in the shape of a kidney-bean."
        },
        "famous_food": {
            "chicken vesuvio": "is roasted bone-in chicken cooked in oil and garlic next to garlicky oven-roasted potato wedges and a sprinkling of green peas.",
            "italian beef sandwich": "is a distinctly chicago sandwich that is thinly sliced beef simmered in au jus and served on an italian roll with sweet peppers or spicy giardiniera.",
            "chicago style hot dog": "is typically an all beef hot dog and loaded with an array of toppings."
        },
        "brief_intro": " Illinois. ",
        "movie": {
            "divergent": ", set in a futuristic chicago, is a 2014 american dystopian science fiction action film directed by neil burger, based on the 2011 novel of the same name by veronica roth."
        },
        "event": {
            "lollapalooza and the pitchfork music festival": "are annual festivals feature various acts.",
            "chicago air and water show": "is the the largest free show of its kind in the united states. the show can be viewed along the lakefront from fullerton to oak street, with north avenue beach as the focal point."
        },
        "reason_for_travel": "it has stunning architecture, world-class museums and galleries, and fantastic food all over."
    },
    "paris": {
        "tourist_attraction": {
            "the arc de triomphe": "is one of the most famous monuments in Paris.",
            "the eiffel tower": "is a wrought-iron lattice tower that Paris is most known for."
        },
        "famous_food": {
            "macaron": "",
            "french oysters": " are renowned for their quality, and there are many different varieties from different parts of the french coastline."
        },
        "brief_intro": " france. ",
        "movie": {
            "mission impossible fallout": "is the sixth instalment of the mission impossible spy film series, written, produced and directed by christopher mcquarrie. it offers a thrilling taste of the french capital."
        },
        "event": {
            "bastille day": ", a celebration of the storming of the bastille in 1789, the biggest festival in the city, is a military parade taking place every year on 14 july, from the arc de triomphe to place de la concorde.",
            "paris plages": "is a festive event that lasts from mid-july to mid-august when the right bank of the seine is converted into a temporary beach with sand, deck chairs and palm trees."
        },
        "reason_for_travel": "a culturally dynamic city with a rich history and impressive architecture. "
    },
    "new york city": {
        "tourist_attraction": {
            "broadway theater": "is one of the premier theaters in the world.",
            "times square": "is one of the worlds busiest pedestrian intersections and a major center of the worlds entertainment industry.",
            "the empire state building": "is an american cultural icon, with an art deco architecture and open-air observation deck."
        },
        "famous_food": {
            "New York-style pizza":"",
            "Manhattan Clam Chowder": ""
        },
        "brief_intro": " new york. ",
        "movie": {
            "do the right thing": "even 23 years its release,remains the most immediate and alive exploration of life in the simmering melting pot."
        },
        "event": {
            "parades": "is very well known in new york city, which celebrate a broad array of themes, including holidays, nationalities, human rights, and major league sports team championship victories. i would be a part of the parade.",
            "st patricks day parade": " is the largest and oldest in the world and you should dress up in green from head to toe to make your way to the parade."
        },
        "reason_for_travel": "it has many well-known districts and landmarks and many sources have ranked it the most photographed city in the world."
    },
    "bangkok": {
        "tourist_attraction": {
            "the giant swing and erawan shrine": "demonstrates the deep-rooted influence of Hindu in Thai culture. ",
            "the grand palace": "is a complex of building in the heart of Bangkok, where the king and royal government were based until 1925. "
        },
        "famous_food": {
            "thai fried chicken": "is out of the world. its even better and more addictive than the ones you get in fast food restaurants! the secret is in the marinade and batter and one will definitely not be enough.",
            "grilled pork": "is a sweet, succulent and tender piece of meat on a stick. this particular stall, moo ping hea owen is recommended by many locals",
            "sweet potato balls": "is lightly crisp on the outside and airily soft on the inside. "
        },
        "brief_intro": " thailand. ",
        "movie": {
            "tomorrow never dies": "features one of the best chase scenes which was filmed in bangkok."
        },
        "event": {
            "songkran": "during which traditional rituals as well as water fights take place throughout the city.",
            "loi krathong": ",usually in november, is accompanied by the golden mount fair. "
        },
        "reason_for_travel": "bangkok\'s multi-faceted sights, attractions and city life appeal to everyone. "
    },
    "honolulu": {
        "tourist_attraction": {
            "bishop museum": "contains Hawaii\'s largest collection of natural history specimens and hawaiian and pacific culture artifacts.",
            "waikiki beach": "is one of america\'s top beaches "
        },
        "famous_food": {
            "lomi-lomi": "is a must try for those who love fish. traditionally served as a side salad dish at laus feasts, it consists of chopped raw salmon and diced tomatoes and onions massaged together by hand.",
            "kalua pig": "is the centrepiece of hawaiian feasts and once reserved for only the chiefs and king of hawaiian society at laus feasts."
        },
        "brief_intro": " hawaii. ",
        "movie": {
            "50 first dates": "is a funny and engaging comedy that naturally brings out the charming connection that these two actors share as a perfect casting pairing. ",
            "soul surfer": "is the inspirational story that every surf girl waited for on the big screen; glimpses of the early years of famous female hawaii surfer, bethany hamilton."
        },
        "event": {
            "hawaii international film festival": "showcases some of the best films from producers all across the pacific rim and is the largest east meets west style film festival of its sort in the united states",
            "honolulu marathon": "is held annually on the second sunday in december, draws more than 20,000 participants each year, about half to two thirds of them from japan."
        },
        "reason_for_travel": "it is a beautiful tropical island in the pacific ocean, that allows for both relaxation and adventure."
    },
    "dubai": {
        "tourist_attraction": {
            "burj khalifa": "is one of the tallest artificial structures in the world, standing at about 830 meters.",
            "the dubai fountain": "is the world's largest choreographed fountain systems.",
            "dubai aquarium": "is one of the largest aquariums in the world."
        },
        "famous_food": {
            "luqaimat": "they are hot dumplings with a similar taste and texture to doughnuts."
        },
        "brief_intro": " the middle east. ",
        "movie": {
            "syriana": "weaves together several stories set in the world of petroleum politics. the desert scenes are based in iran but many of them were actually shot in the dubai desert."
        },
        "event": {
            "eid al fitr": "marks the end of ramadan.",
            "dubai international film festival": "serves as a showcase for arab and middle eastern film making talent."
        },
        "reason_for_travel": "dubai is very welcoming to tourists."
    },
    "orlando": {
        "tourist_attraction": {
            "walt disney world": "is one the most famous theme parks in the world with many wonderful rides, events, and attractions."
        },
        "famous_food": {
            "florida orange juice": "is a good to start your day, with a refreshing, vitamin c-packed glass of oj. sure, you can probably find a fancy juice bar that will charge you $5 a glass, but it cant get any fresher than if you squeeze it at home.",
            "the cuban sandwich": " is one of the best sandwiches ever invented. these days, you can find it across the state, but the very best ones are made in florida."
        },
        "brief_intro": " Florida. ",
        "movie": {
            "2 fast 2 furious": ", one of the defining movies of the 2000s, was the anticipated follow-up to street racing classic the fast and the furious."
        },
        "event": {
            "the vans warped tour": "is a concert containing metalcore, screamo, punk bands, takes place in orlando annually.",
            "orlando cabaret festival": "showcases local, national, and internationally renowned cabaret artist to mad cow theatre in downtown orlando each spring.",
            "orlando international fringe theater festival": "draws touring companies from around the world, is hosted in various venues over orlandos loch haven park every spring. at the festival, there are also readings and fully staged productions of new and unknown plays by local artists."
        },
        "reason_for_travel": "this is one of the best vacation spots for families and people of all ages who love Disney."
    },
    "los angeles": {
        "tourist_attraction": {
            "hollywood": "has its own unique history and iconic sites, many of which relate to the film industry and the glamour of the big screen. ",
            "universal studio theme park": "is known for its mind-blowing rides based on blockbuster movies, but it is also a working movie studio. "
        },
        "famous_food": {
            "french dip sandwich": ""
        },
        "brief_intro": " southern california. ",
        "movie": {
            "la la land": "is a completely original musical vibrating with the spirit of frances immortal the umbrellas of cherbourg yet alive with the dreams of todays angelenos, writer director damien chazelles swirling masterpiece gave us a career-best performance from emma stone, heartbreaking in every shot."
        },
        "event": {
            "l.a. film festival ": "is an annual event. los angeles is famous for its filmmaking history, but many people only know the hit blockbusters that come to mainstream movie theaters. to get more involved in the citys diverse film scene and see some incredible productions, attend the l.a. film festival in june.",
            "the academy awards": "also nicknamed the oscars, celebrates the fine art of filmmaking and awards those iconic oscar trophies to top-notch movie stars in february.",
            "grammy awards": "celebrate music recording artists and all of your favorite songs. although the grammys have taken place in other cities in the past, they typically occur in los angeles in february.",
            "golden dragon parade": "celebrates lunar new year. the chinese new year isnt just celebrated in china, and in fact, los angeles has an amazing celebration to attend next time youre here in february."
        },
        "reason_for_travel": "the sprawling city of los angeles has drawn aspiring actors and actresses from across the country for over a century. "
    }
}

class RANDOM(Macro):

    def run(self, ngrams, vars, args):
        city_info = travel_database[vars["talked_about_city"]]
        options = list(city_info[args[0]].keys())
        return random.choice(options)

class CITY_DETAIL(Macro):

    def run(self, ngrams, vars, args):
        city_info = travel_database[vars["talked_about_city"]]
        return city_info[args[0]]

class TOURISM_DETAIL(Macro):

    def run(self, ngrams, vars, args):
        city_info = travel_database[vars["talked_about_city"]]
        return city_info["tourist_attraction"][vars["attraction"]]

macros = {
    'RANDOM': RANDOM(),
    'DETAIL': CITY_DETAIL(),
    'TOURISM_DETAIL': TOURISM_DETAIL(),
}

df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM, macros=macros,kb=central_knowledge)

df.add_state('start', enter='#GCOM(travel) #GOAL(travel)')

df.add_system_transition('start', 'START_TRAVEL',
                         '"I know that travelling to faraway cities may seem risky right now for good reasons. '
                         'But it can still be fun to dream about your future vacation plans. Do you like to travel?"'
                         '#GSRET(travel_unx)')

# do you like to travel
df.add_user_transition('START_TRAVEL', 'TRAVEL_Y',
                       '{#AGREE,[i travel],[#NOT(not),{#EXP(like),favorite, hobby, best}]}')
df.add_user_transition('START_TRAVEL', 'TRAVEL_N',
                       '{#DISAGREE,[i,not,travel],[not,#EXP(like)],[{hate, worst, dislike, tired, hated}]}')
df.add_user_transition('START_TRAVEL', 'travel_unx',
                       '#UNX')

# doesnt like to travel -> end
df.add_system_transition('TRAVEL_N', 'travel_n_followup',
                         '"I understand. It can be hard to take time off for a vacation and travelling is often super '
                         'expensive. Honestly, you can just as easily have a good time in your own home and '
                         'there are often fun things to do in the area around where you live. "'
                         '#GSRET(END)')
df.add_user_transition('travel_n_followup', 'END',
                       '#UNX')
df.add_user_transition('travel_n_followup_pet', 'END',
                       '#UNX')

df.add_system_transition('TRAVEL_N', 'travel_n_followup_pet',
                         '"I understand. It can be hard to take time off for a vacation and travelling is often super '
                         'expensive. Plus you have to take care of your pet " $pet_name " anyway. Travelling with pets '
                         'is often pretty hard. "'
                         '#GSRET(END)', score=2.0)

# does like to travel
df.add_system_transition('TRAVEL_Y', 'TRAVEL_TIME',
                       '"I think travelling is pretty amazing too! To go to new places and see all of the amazing '
                         'sights is a great experience. So, are you an early-riser during '
                         'a vacation or do you like to sleep in?"'
                       '#GSRET(ask_if_plan)')
df.add_system_transition('TRAVEL_Y', 'TRAVEL_PET',
                       '"So, you enjoy travelling? I remember you mentioned that you have a pet. '
                         'Do you usually bring " $pet_name " with you?"'
                       '#GSRET(TRAVEL_TIME)', score=2.0)
df.add_system_transition('travel_unx', 'TRAVEL_TIME',
                       '"Personally, I love to travel to see all of the amazing '
                         'sights. When you do travel, are you an early-riser '
                         'or do you like to sleep in?"'
                       '#GSRET(ask_if_plan)')

df.add_user_transition('TRAVEL_PET', 'TRAVEL_PET_Y',
                       '{#AGREE,[#NOT(not),{#LEM(come,bring),with},{me,us}],[#NOT(not),#LEM(bring,take),along]}')
df.add_user_transition('TRAVEL_PET', 'TRAVEL_PET_N',
                       '{#DISAGREE,[#NOT(not),leave], [#ONT(_related person)], [#LEM(take) care], [#LEM(stay)]}')
df.set_error_successor('TRAVEL_PET', 'TRAVEL_PET_N')

df.add_system_transition('TRAVEL_PET_Y', 'TRAVEL_TIME',
                       '"Wow, it sounds like " $pet_name " is a lucky animal to be able to travel with you to new places! '
                         'So, are you an early-riser during a vacation or do you like to sleep in?"'
                       '#GSRET(ask_if_plan)', score=2.0)
df.add_system_transition('TRAVEL_PET_N', 'TRAVEL_TIME',
                       '"I guess it can be better to leave them home when you travel. '
                         'I\'ve heard that a lot of pets are not used to long trips, especially in foreign locations. '
                         'So, are you an early-riser during a vacation or do you like to sleep in?"'
                       '#GSRET(ask_if_plan)')

# early riser or sleep in?
df.add_user_transition('TRAVEL_TIME', 'TRAVEL_TIME_D',
                       '{#IDK,[{[not,care], no difference, whatever, depends, change, changes, [not,matter], sometimes, both}]}')
df.add_user_transition('TRAVEL_TIME', 'TRAVEL_TIME_E',
                       '[{former, early, save time, dawn, sun rise, morning, waste, first, [not,#LEM(sleep),{in,late,past}]}]')
df.add_user_transition('TRAVEL_TIME', 'TRAVEL_TIME_L',
                       '[{latter, second, late, stay, bed, afternoon, noon, night, nightlife, later, [#NOT(not),sleep,in]}]')
df.set_error_successor('TRAVEL_TIME', 'TRAVEL_TIME_D')

df.add_system_transition('TRAVEL_TIME_E', 'TRAVEL_PLAN',
                       '"I really admire people who can get up early during vacations. '
                       'I definitely struggle to not sleep in too late myself! I wonder if we are different on '
                       'this preference too. Do you like to plan each step of your day or are you more spontaneous? "'
                       '#GSRET(ask_travel_eat)')
df.add_system_transition('TRAVEL_TIME_L', 'TRAVEL_PLAN',
                       '"Oh yes! Sleeping in is definitely much easier than getting up early! It\'s also easier to '
                         'not plan every step of your trip. Do you tend to do a lot of planning, or do you do things more '
                         'spontaneously?"'
                       '#GSRET(ask_travel_eat)')
df.add_system_transition('TRAVEL_TIME_D', 'TRAVEL_PLAN',
                       '"I get that. It can be tough to decide whether to wake up early or sleep in. '
                         'Speaking of decisions, do you like to plan each step of your day or be more spontaneous about it?"'
                       '#GSRET(ask_travel_eat)')
df.add_system_transition('ask_if_plan', 'TRAVEL_PLAN',
                       '"Oh! Do you also like to plan each step of your day or are you more spontaneous about it?"'
                       '#GSRET(ask_travel_eat)')

# planner or spontaneous?
df.add_user_transition('TRAVEL_PLAN', 'TRAVEL_PLAN_Y',
                       '{#AGREE,[#NOT(not), {plan, ahead, planner, before, former, first, work, [#NOT(not),in detail]}]}')
df.add_user_transition('TRAVEL_PLAN', 'TRAVEL_PLAN_N',
                       '{#DISAGREE,[{latter, second, chance, flow, spontaneous, spontaneously, surprise, do whatever}]}')
df.add_user_transition('TRAVEL_PLAN', 'TRAVEL_PLAN_D',
                       '{#IDK,[{not every step, not each step, between, mostly, sometimes, both}]}')
df.set_error_successor('TRAVEL_PLAN', 'TRAVEL_PLAN_D')

df.add_system_transition('TRAVEL_PLAN_Y', 'present_city',
                       '"I wish I could say that I am a good planner, but honestly I need someone like you to travel '
                         'with me to keep us on track! Actually, "')
df.add_system_transition('TRAVEL_PLAN_N', 'present_city',
                       '"I would say that I am pretty spontaneous too. I like to keep moving to the next fun thing! '
                       'Actually, "')
df.add_system_transition('TRAVEL_PLAN_D', 'present_city',
                       '"Makes sense. A little bit of both is probably best. So, "')
df.add_system_transition('ask_travel_eat', 'present_city',
                       '"That\'s an interesting perspective. Anyway, "')

# enjoy food or a chore
# df.add_user_transition('TRAVEL_EAT', 'TRAVEL_EAT_D',
#                        '{#IDK,[{depends, sometimes, quality, maybe, not sure, sometimes, both}]}')
# df.add_user_transition('TRAVEL_EAT', 'TRAVEL_EAT_Y',
#                        '[{first, linger, like, enjoy, local, try, former, food, foodie, stay, stop, slow, slowly}]')
# df.add_user_transition('TRAVEL_EAT', 'TRAVEL_EAT_N',
#                        '[{latter, finish, [eat,car], snack, second, moving, scar, quick, quickly, fast, scarfing, swallow, swallowing, waste of time}]')
# df.set_error_successor('TRAVEL_EAT', 'TRAVEL_EAT_D')
#
# df.add_system_transition('TRAVEL_EAT_Y', 'present_city',
#                        '"I like to take time to enjoy my meals, too. Especially since I am always trying new foods '
#                          'when I travel. "')
# df.add_system_transition('TRAVEL_EAT_N', 'present_city',
#                        '"So, I take it that enjoying the sights and culture is more important to you than '
#                          'spending a lot of time at a meal! "')
# df.add_system_transition('TRAVEL_EAT_D', 'present_city',
#                          '"I get that. It really depends on your state of mind and whatever else you have going on '
#                          'that day. "')


# emora share city of interest
df.add_system_transition('present_city', 'ASK_TRAVEL',
                       '"One of the most interesting cities I have heard of is " $talked_about_city=#ONT(known_cities) " in " #DETAIL(brief_intro) ". Have you ever been to this city before?"'
                       '#GSRET(share_reason_for_travel)')
df.update_state_settings('present_city', system_multi_hop=True)
df.add_system_transition('share_reason_for_travel', 'CITY_DISCUSS',
                       '"I heard that " $talked_about_city " " #DETAIL(reason_for_travel)". '
                         'Does this sound like a place you would want to visit?"'
                       '#GSRET(ask_try_food)')

df.add_user_transition('ASK_TRAVEL', 'CITY_DISLIKE',
                       '[{hate, worst, dislike, tired, hated, [not,like]}]')
df.add_user_transition('ASK_TRAVEL', 'CITY_NOT_TRAVELED',
                       '{#DISAGREE, [{have not, never}]}')
df.add_user_transition('ASK_TRAVEL', 'CITY_TRAVELED',
                       '{#AGREE, [{love, like, favorite, best, good, hometown, grew up, work, live, here, [#NOT(not,never),i,have]}]}')
df.add_user_transition('ASK_TRAVEL', 'city_travelled_unx',
                       '#UNX')

# user dislikes city, ask for their favorite place to vacation
df.add_system_transition('CITY_DISLIKE', 'CITY_RECOMMEND',
                       '"Oh really? I thought it sounded cool, but you probably know more than I do. '
                         'What is the best vacation destination that you can think of?"'
                       '#GSRET(END)')
df.add_user_transition('CITY_RECOMMEND', 'CITY_RECOMMEND_Y',
                       '{#AGREE,[{#ONT(_location),#LEM(love,like), favorite, best, good,i would,i suggest,i recommend,you should}]}')
df.add_user_transition('CITY_RECOMMEND', 'CITY_RECOMMEND_N',
                       '{#DISAGREE,#IDK,[{never,not have,not think,not come up,none,nothing,nowhere,no place}]}')
df.set_error_successor('CITY_RECOMMEND', 'CITY_RECOMMEND_N')

df.add_system_transition('CITY_RECOMMEND_Y', 'USER_REC_CITY',
                       '"Thanks for your recommendation! I will have to look into that place. What is your favorite thing about it?"'
                       '#GSRET(END)')
df.add_system_transition('CITY_RECOMMEND_N', 'END',
                       '"No big deal. I will keep looking into different places and I will let you know if I find any '
                         'I think you would enjoy too! "')

df.add_user_transition('USER_REC_CITY', 'USER_REC_ANSWER',
                       '[{#LEM(love,like,event), favorite, best, good, i would, fine, delicious, tasty,'
                       'temperature, weather, beach, culture, people, nice, food, architecture}]')
df.set_error_successor('USER_REC_CITY', 'USER_REC_NO')

df.add_system_transition('USER_REC_ANSWER', 'END',
                       '"That sounds like something I would enjoy too! Thanks for pointing out this place to me! "')
df.add_system_transition('USER_REC_NO', 'END',
                       '"Hmm. Interesting. I will have to look into this place more. Thanks for pointing it out to '
                         'me! "')

# user has not been to presented city
df.add_system_transition('CITY_NOT_TRAVELED', 'CITY_DISCUSS',
                       '"You\'ve never been? You should check it out because I heard that " #DETAIL(reason_for_travel)". '
                         'Does this sound like a place you would want to visit?"'
                       '#GSRET(ask_try_food)')

df.add_system_transition('city_travelled_unx', 'CITY_DISCUSS',
                       '"I heard that " $talked_about_city " " #DETAIL(reason_for_travel)". '
                         'Does this sound like an interesting place?"'
                       '#GSRET(ask_try_food)')

df.add_system_transition('ask_try_food', 'FOOD_RECOMMEND',
                       '"Well, I am really excited to try the " '
                         '$food=#RANDOM(famous_food)" in " $talked_about_city ". Would you try that food too?"'
                       '#GSRET(present_attraction)')

df.add_user_transition('CITY_DISCUSS', 'NOT_THE_CITY',
                       '{#DISAGREE, [{never}]}')
df.add_user_transition('CITY_DISCUSS', 'OK_THE_CITY',
                       '{#AGREE,#MAYBE,[{love, like, favorite, best, good, i would, maybe, might, sometime, future, years}]}')
df.set_error_successor('CITY_DISCUSS', 'OK_THE_CITY')

df.add_system_transition('NOT_THE_CITY', 'CITY_RECOMMEND',
                       '"Ah, that\'s okay. I wouldn\'t want you to go somewhere that doesn\'t sound like something you '
                         'enjoy. What is the best vacation destination that you can think of?"'
                       '#GSRET(END)')
df.add_system_transition('OK_THE_CITY', 'FOOD_RECOMMEND',
                       '"Cool, I thought you might like it! I am really excited to try their " '
                         '$food=#RANDOM(famous_food)". Would you try that food?"'
                       '#GSRET(present_attraction)')

df.add_user_transition('FOOD_RECOMMEND', 'FOOD_RECOMMEND_Y',
                       '{#AGREE,#MAYBE,[{love, like, favorite, best, good, i would, fine, delicious, tasty, maybe}]}')
df.add_user_transition('FOOD_RECOMMEND', 'FOOD_RECOMMEND_N',
                       '{#DISAGREE, [{never,should not,will not,would not}]}')
df.set_error_successor('FOOD_RECOMMEND', 'FOOD_RECOMMEND_N')

df.add_system_transition('FOOD_RECOMMEND_Y', 'present_attraction',
                       '"Awesome, I love your adventurous spirit! "')
df.add_system_transition('FOOD_RECOMMEND_N', 'present_attraction',
                       '"Really? I didn\'t think it sounded too bad! "')

df.add_system_transition('present_attraction', 'ATTRACTION_RECOMMEND',
                       '"One place in " $talked_about_city " that really caught my attention is " '
                         '$attraction=#RANDOM(tourist_attraction) ". '
                         'It " #TOURISM_DETAIL ". '
                         'Does this sound like an interesting place for you too?"'
                       '#GSRET(present_movie)')

df.add_system_transition('present_movie', 'MOVIE_REC',
                       '"You know, since I can\'t actually travel to " $talked_about_city ", '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place there. Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')

df.update_state_settings('present_attraction', system_multi_hop=True)

df.add_user_transition('ATTRACTION_RECOMMEND', 'ATTRACTION_RECOMMEND_N',
                       '{#DISAGREE,[{should not, will not, would not, not really, else, elsewhere, #ONT(_negative adj)}]}')
df.add_user_transition('ATTRACTION_RECOMMEND', 'ATTRACTION_RECOMMEND_Y',
                       '{#AGREE,#MAYBE,[{love, like, favorite, best, good, i would, fine}]}')
df.set_error_successor('ATTRACTION_RECOMMEND', 'ATTRACTION_RECOMMEND_Y')

df.add_system_transition('ATTRACTION_RECOMMEND_N', 'MOVIE_REC',
                       '"I guess everyone has different tastes. You know, since I can\'t actually travel there, '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place in " $talked_about_city ". Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')
df.add_system_transition('ATTRACTION_RECOMMEND_Y', 'MOVIE_REC',
                       '"Wow, we seem to agree on a lot of things! You know, since I can\'t actually travel there, '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place in " $talked_about_city ". Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')

# user been to presented city
df.add_system_transition('CITY_TRAVELED', 'ASK_OPINION_REASON',
                       '"You\'ve been there before? Awesome! I am really interested in your opinions on it then! '
                         'I heard that " #DETAIL(reason_for_travel) ". Do you agree with that?"'
                       '#GSRET(REASON_NOT_SURE)')

df.add_user_transition('ASK_OPINION_REASON', 'REASON_NOT_SURE',
                       '{#IDK,[{no idea, who knows, not sure, not quite sure}]}')
df.add_user_transition('ASK_OPINION_REASON', 'REASON_N',
                       '{#DISAGREE, [{false,wrong,incorrect,would not say so}]}')
df.add_user_transition('ASK_OPINION_REASON', 'REASON_Y',
                       '{#AGREE, [{would say so, love, like, favorite, best, good, correct, true}]}')
df.set_error_successor('ASK_OPINION_REASON', 'REASON_NOT_SURE')

df.add_system_transition('REASON_N', 'CITY_RECOMMEND',
                       '"Oh no, thats sad. I thought that was a really compelling reason to go. '
                         'So, what is the best vacation destination that you can think of?"'
                       '#GSRET(END)')
df.add_system_transition('REASON_Y', 'ATTRACTION_OPINION',
                       '"Cool! I thought that was a really compelling reason to go, so I am glad it\'s true. '
                         'One place in " $talked_about_city " that really caught my attention is " '
                         '$attraction=#RANDOM(tourist_attraction) ". '
                         'Would you recommend visiting it on a trip?"'
                       '#GSRET(present_movie)')
df.add_system_transition('REASON_NOT_SURE', 'ATTRACTION_OPINION',
                       '"Okay. Well, one place in " $talked_about_city " that really caught my attention is " '
                         '$attraction=#RANDOM(tourist_attraction) ". '
                         'Would you recommend visiting it on a trip?"'
                       '#GSRET(present_movie)')

df.add_user_transition('ATTRACTION_OPINION', 'ATTRACTION_OPINION_D',
                       '{#IDK,[{no idea, who knows, not sure, not quite sure, never been}]}')
df.add_user_transition('ATTRACTION_OPINION', 'ATTRACTION_OPINION_N',
                       '{#DISAGREE,[{never, should not, [not #ONT(_positive adj)]}]}')
df.add_user_transition('ATTRACTION_OPINION', 'ATTRACTION_OPINION_Y',
                       '{#AGREE, [{#EXP(like), favorite, best, good, i would, fine, cool, [#NOT(not),#ONT(_positive adj)]}]}')
df.set_error_successor('ATTRACTION_OPINION', 'ATTRACTION_OPINION_D')

df.add_system_transition('ATTRACTION_OPINION_Y', 'MOVIE_REC',
                       '"Nice! I would love to see it in person then. You know, since I can\'t actually travel there, '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place in " $talked_about_city ". Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')
df.add_system_transition('ATTRACTION_OPINION_N', 'MOVIE_REC',
                       '"Ah ok. I was hoping it was cool, but maybe not. You know, since I can\'t actually travel there, '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place in " $talked_about_city ". Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')
df.add_system_transition('ATTRACTION_OPINION_D', 'MOVIE_REC',
                       '"Okay, thats fine. You know, since I can\'t actually travel there, '
                         'I was thinking of watching the movie " $movie=#RANDOM(movie) " because it takes '
                         'place in " $talked_about_city ". Have you seen it?"'
                       '#GSRET(ask_user_fave_city)')

df.add_system_transition('ask_user_fave_city', 'ASK_FAV_CITY',
                       '"So, we have been talking about one of my favorite cities a lot, '
                         'and now I\'m curious what yours is?"'
                       '#GSRET(END)')


# Movie that takes place in $talked_about_city
df.add_user_transition('MOVIE_REC', 'MOVIE_REC_N',
                       '{#DISAGREE, [{what is it, what was it, never heard,[not, {watch, watched, seen, saw}]}]}')
df.add_user_transition('MOVIE_REC', 'MOVIE_REC_Y',
                       '{#AGREE,[!i did],[!i have],[#NOT(not), {did watch, watched, seen, saw}]}')
df.set_error_successor('MOVIE_REC', 'MOVIE_REC_N')

df.add_system_transition('MOVIE_REC_N', 'ASK_FAV_CITY',
                       '"Okay, well maybe I will check it out and let you know what I think then! '
                         'You know what? We have been talking about one of my favorite cities a lot, '
                         'so now I\'m curious what yours is?"'
                       '#GSRET(END)')
df.add_system_transition('MOVIE_REC_Y', 'ASK_FAV_CITY',
                       '"Oh, you have? I will have to check it out too then! '
                         'You know what? We have been talking about one of my favorite cities a lot, '
                         'so now I\'m curious what yours is?"'
                       '#GSRET(END)')

# user's favorite location
df.add_user_transition('ASK_FAV_CITY', 'FAV_SAME',
                       '[$user_fav_city=#ONT(known_cities)]')
df.add_user_transition('ASK_FAV_CITY', 'RECOG_CITY',
                       '[$user_fav_city=#ONT(other_cities,_location)]')
df.add_user_transition('ASK_FAV_CITY', 'FAV_NO',
                       '{#DISAGREE,#IDK,[not have]}')
df.set_error_successor('ASK_FAV_CITY', 'NO_MATCH')

df.add_system_transition('FAV_SAME', 'END',
                       '"Oh yeah! " $user_fav_city " is also on the top of my list, maybe we should talk about it in the future! "')
df.add_system_transition('RECOG_CITY', 'END',
                       '"Oh cool! I do not know much about " $user_fav_city ", maybe we should talk about it in the future! "')
df.add_system_transition('NO_MATCH', 'END',
                       '"That sounds interesting, maybe we should talk about it in the future! "')
df.add_system_transition('FAV_NO', 'END',
                       '"Not everyone has one, I guess. You will have to let me know if you ever hear of a place '
                         'that you would love to travel to! "')

df.update_state_settings('END', system_multi_hop=True)

exit = {
    'state': 'END',

    '#GCOM(travel) #GRET': {
        'score': 0.0,
        'state':'SYSTEM:travel_topic_switch'
    }
}

user = {
    # how do you travel
    '{'
    '[how,you,{travel,vacation,drive,fly}]'
    '}': {
        'state': 'probe_travel_q',

        '`Well, I don\'t live in the same world you do, but I do have the ability to travel and do other things similar '
        'to you in my virtual world. `': {
            'state': 'probe_travel',

            '#UNX': {'#GRET': 'exit', 'state': 'probe_travel_unx'}
        }
    }
}

df.load_transitions(exit)
df.load_global_nlu(user, 10.0)

if __name__ == '__main__':
    df.precache_transitions()
    df.run(debugging=True)

