import requests

from orijin_sdk.defaults import ENDPOINTS

def login_full(email: str, password: str, endpoint = ENDPOINTS.brand_login):
    """
    Request a login token to the Orijin system.
    Returns a json of the response, which if successful should include a user token at ["data"]["token"]
    """
    r = requests.post(url=endpoint, json={"email":email, "password":password})
    return r.json()

def login(email: str, password: str, endpoint) -> str | None:
    """
    Request a login token to the Orijin system.
    Same as login_full(), but only the auth token is returned.
    """
    try:
        return login_full(email, password, endpoint = ENDPOINTS.brand_login)["data"]["token"]
    except:
        return None

def register(
    email: str,
    phone: str,
    password: str,
    register_url: str = ENDPOINTS.consumer_register,
    firstName: str = "Made By",
    lastName: str = "Orijin-SDK (Python)",
    referralCode: str = "",
    purchaseToken: str = "",
    productRegisterID: str = "",
):
    response = requests.post(register_url, json={
        'email': email,
        'phone': phone,
        'password': password,
        'register_url': register_url,
        'firstName': firstName,
        'lastName': lastName,
        'referralCode': referralCode,
        'purchaseToken': purchaseToken,
        'productRegisterID': productRegisterID,
    })
    return response.json()