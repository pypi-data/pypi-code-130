# github_directory: graphql-go/graphql, stars: 8727, last_update: 2022-08-19
from graphdna.detectors.checkers import in_response_text
from graphdna.entities.interfaces.heuristics import IGQLQuery


class GraphQLGo(IGQLQuery):

    score_factor = 0.64
    genetics = {
        '': in_response_text('Must provide an operation.'),
        'query  { __typename {}': in_response_text('Unexpected empty IN'),
        'query { __typename }': in_response_text('RootQuery'),
    }
