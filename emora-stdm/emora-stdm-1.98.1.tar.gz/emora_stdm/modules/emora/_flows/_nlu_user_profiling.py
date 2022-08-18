
_nlu_user_profiling = {

    # # User job
    # '{'
    # '[{i am, im} a #ONT(job)], '
    # '[i #ONT(job) {for a living, for work, professionally, as a job, for a job}], '
    # '[my {job, work} #ONT(job)], '
    # '[i {work, take jobs, have a job} #ONT(job)]'
    # '}':{
    #
    # },
    #
    # # User is a __
    # '{'
    # '[{im, i am} #ONT(persontype)]'
    # '}':{
    #
    # },

    # # todo - make sure no crude words are given
    # # User likes
    # '[!-#NEGATION {'
    # '[i {like, love} $user_likes=#ONT(likable)?]'
    # '}]':{
    #     '`Me too! What do you like the most about it?`': {
    #         'state': 'returning_from_global_like',
    #
    #         '#UNX': {'#GRET': 'SYSTEM:root'}
    #     }
    # },

    # # User currently feels __
    # '{'
    # '[{im, i feel, ive been, i am} #ONT(feeling)]'
    # '}':{
    #
    # },
    #
    # # User went __
    # '{'
    # '[{i, we, me and, and me} went]'
    # '}':{
    #
    # },
    #
    # # User thinks ___
    # '{'
    # '[#NOT(i think so) [i, think]]'
    # '}':{
    #
    # },

    #
}