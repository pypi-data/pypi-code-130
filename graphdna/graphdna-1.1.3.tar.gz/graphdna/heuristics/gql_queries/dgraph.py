# github_directory: dgraph-io/dgraph, stars: 18351, last_update: 2022-08-19
from graphdna.detectors.checkers import in_response_text
from graphdna.entities.interfaces.heuristics import IGQLQuery


class DGraph(IGQLQuery):

    score_factor = 0.8
    genetics = {
        'query { __typename }':
            in_response_text([
                'Not resolving __typename. There\'s no GraphQL schema in Dgraph. Use the /admin API to add a GraphQL schema',
                'Dgraph',
            ]),
    }
