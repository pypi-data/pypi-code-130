# github_directory: sangria-graphql/sangria, stars: 1902, last_update: 2022-08-19
from graphdna.detectors.checkers import in_response_text
from graphdna.entities.interfaces.heuristics import IGQLQuery


class Sangria(IGQLQuery):

    score_factor = 0.53
    genetics = {
        'queryy { __typename }':
            in_response_text('Syntax error while parsing GraphQL query. Invalid input \\"queryy\\", expected ExecutableDefinition or TypeSystemDefinition'),
    }
