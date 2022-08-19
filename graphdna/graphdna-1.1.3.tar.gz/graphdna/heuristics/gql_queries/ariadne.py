# github_directory: mirumee/ariadne, stars: 1820, last_update: 2022-08-19
from graphdna.detectors import in_response_text
from graphdna.entities.interfaces.heuristics import IGQLQuery


class Ariadne(IGQLQuery):

    score_factor = 0.53
    genetics = {
        '': in_response_text('The query must be a string.'),
        'query { __typename @abc }': in_response_text('Unknown directive \'@abc\'.'),
    }
