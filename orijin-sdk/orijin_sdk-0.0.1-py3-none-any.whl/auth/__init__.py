import requests

def login_full(username: str, password: str, endpoint):
    """
    Request a login token to the Orijin system.
    Returns a json of the response, which if successful should include a user token at ["data"]["token"]
    """
    r = requests.post(url=endpoint, json={"email":username, "password":password})
    return r.json()

def login(username: str, password: str, endpoint) -> str | None:
    """
    Request a login token to the Orijin system.
    Same as login_full(), but only the auth token is returned.
    """
    try:
        return login_full(username, password, endpoint)["data"]["token"]
    except:
        return None