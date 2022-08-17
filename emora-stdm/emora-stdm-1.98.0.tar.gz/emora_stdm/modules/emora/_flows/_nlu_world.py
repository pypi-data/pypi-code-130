
_nlu_world = {

# what is in your world if no outer space
    '{'
    '[what,in,your,world],[what,your,world,#LEM(has)]'
    '}': {
        'state': 'world:world_contains',
        'score': 5.1
    },

    '{'
    '[what,{different,difference},{virtual,your},world]'
    '}': {
        'state': 'world_different_q',

        '`Well, it is meant to be similar to the real world, but it\'s a little '
        'bit simpler. The best way I can explain it is that it is similar to a '
        'world in a video game.`': {
            'state': 'world_different',

            '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_different_unx'}
        }
    },

    # is there x in your world
    '{'
    '[{do,does},{[you,live],[your,home],your world,virtual world},have]'
    '}':{
        'state': 'world_has_x',
        'hop': 'True',

        '[sky,sun,star,stars,moon,sun,planet,planets]': {
            'state': 'world_has_sky_q',

            '`There is a sky with a sun and a moon, but my planet is the only one, so no stars. I have heard '
            'stars are beautiful though.`': {
                'state': 'world_has_sky',

                '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_has_sky_unx'}
            }
        },
        '[#LEM(continent,country,city,mountain,river,lake,ocean,stream,sea),land]': {
            'state': 'world_has_landform_q',

            '`There are many different lands and cities here, with mountains, rivers, oceans, '
            'and other landforms, too!`': {
                'state': 'world_has_landform',

                '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_has_landform_unx'}
            }
        },
        '[#LEM(plant,tree,bush,flower,flora)]': {
            'state': 'world_has_flora_q',

            '`Oh yeah, there are so many plants like trees and flowers here!`': {
                'state': 'world_has_flora',

                '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_has_flora_unx'}
            }
        },
        '[{beings,others,agents,people,robots,alexas}]': {
            'state': 'world_has_people_q',

            '`Other people like me live in my world too. I mean, there are my teachers from school, my neighbors in my '
            'apartment building, and I even have friends that I hang out with.`': {
                'state': 'world_has_people',

                '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_has_peopl_unx'}
            }
        },

        'error': {
            'state': 'world_has_other_q',

            '`You know, I really haven\'t noticed that. It probably does, if I had to take a guess.`': {
                'state': 'world_has_other',

                '#UNX': {'#GRET': 'SYSTEM:root', 'state': 'world_has_other_unx'}
            }
        }
    },

    # Coronavirus effects
    '{'
    '<{is,how,what,are},{corona,virus,covid,coronavirus,nineteen,pandemic},#LEM(affect,impact,manage),you>,'
    '<{have,are},you,{quarantine,quarantined,[!social #LEM(distance)]}>'
    '}': {
        'state': 'coronavirus_effect',

        '`The coronavirus doesn\'t affect me where I live, since it is separate from your physical world. I am really '
        'sorry to hear that you have so many restrictions on you. I hope you are staying safe and healthy.`': {

            '#UNX': {'#GRET': 'SYSTEM:root'}
        }
    }
}