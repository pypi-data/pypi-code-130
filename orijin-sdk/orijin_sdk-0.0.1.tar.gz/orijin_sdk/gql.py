import requests
from .helpers.formatting import to_json

def useQueryAsOn(query: str, variables, token: str, gql_endpoint: str):
    variables = to_json(variables)
    r = requests.post(
        url=gql_endpoint, 
        headers={'authorization': token},
        json={'query': query, 'variables': variables}, 
    )
    return r.json()

def useMutationAsOn(mutation: str, input, token: str, gql_endpoint: str):
    variables = {'input': to_json(input)}
    r = requests.post(
        url=gql_endpoint, 
        headers={'authorization': token},
        json={'query': mutation, 'variables': variables}, 
    )
    return r.json()
