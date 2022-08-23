import json
import time

import google.auth.crypt
import google.auth.jwt
import requests

from sfkit.protocol.utils import constants
from sfkit.protocol.utils.helper_functions import confirm_authentication


def website_get(request_type: str, params: dict) -> requests.Response:
    _, _, sa_keyfile = confirm_authentication()
    url = f"{constants.WEBSITE_URL}/{request_type}"
    headers = {
        "Authorization": f"Bearer {generate_jwt(sa_keyfile).decode('utf-8')}",
        "content-type": "application/json",
    }
    return requests.get(url, headers=headers, params=params)


def get_doc_ref_dict(study_title: str) -> dict:
    response = website_get("get_doc_ref_dict", {"study_title": study_title.replace(" ", "").lower()})
    return response.json()


def get_study_options_for_sa_email(sa_email: str) -> list:
    response = website_get("get_study_options_for_sa_email", {"sa_email": sa_email})
    return response.json().get("options")


def update_firestore(msg: str) -> bool:
    response = website_get("update_firestore", {"msg": msg})
    return response.status_code == 200


def get_github_token() -> dict:
    response = website_get("get_github_token", {})
    return response.json()


def generate_jwt(sa_keyfile, expiry_length=3600):

    """Generates a signed JSON Web Token using a Google API Service Account."""

    with open(sa_keyfile, "r") as f:
        data = json.load(f)
        sa_email = data["client_email"]

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + expiry_length,
        "iss": sa_email,
        "sub": sa_email,
        "email": sa_email,
    }

    signer = google.auth.crypt.RSASigner.from_service_account_file(sa_keyfile)
    jwt = google.auth.jwt.encode(signer, payload)

    return jwt
