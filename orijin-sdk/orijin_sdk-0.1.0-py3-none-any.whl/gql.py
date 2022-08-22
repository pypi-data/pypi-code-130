"""These helper functions are designed to work like the Apollo React Hooks of the same name, simply because that's what I'm used to using."""

import sys
import requests
from .helpers.formatting import to_json

def useQueryAsOn(query: str, variables, token: str, gql_endpoint: str):
    variables = to_json(variables)
    r = requests.post(
        url=gql_endpoint, 
        headers={'authorization': token},
        json={'query': query, 'variables': variables}, 
    )

    response = r.json()

    if 'errors' in response:
        for error in response['errors']:
            print(error, file=sys.stderr)

    return response

def useMutationAsOn(mutation: str, input, token: str, gql_endpoint: str):
    """The only difference between this and useQuery is the input is the only variable expected is the input."""
    return useQueryAsOn(mutation, {'input': to_json(input)}, token, gql_endpoint)

