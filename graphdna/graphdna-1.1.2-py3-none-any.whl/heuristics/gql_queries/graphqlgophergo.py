# github_directory: graph-gophers/graphql-go, stars: 4185, last_update: 2022-07-20
from graphdna.detectors.checkers import has_json_key
from graphdna.entities.interfaces.heuristics import IGQLQuery


class GraphQLGopherGo(IGQLQuery):

    score_factor = 0.75
    genetics = {
        'query {}': has_json_key('data'),
    }
