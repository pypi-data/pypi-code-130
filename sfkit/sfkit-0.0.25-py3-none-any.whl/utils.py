import requests
from sfkit.protocol.utils import constants


def get_doc_ref_dict(study_title: str) -> dict:
    url = f"{constants.WEBSITE_URL}/get_doc_ref_dict"
    params = {"study_title": study_title.replace(" ", "").lower()}
    response = requests.get(url, params=params)
    return response.json()


def get_study_options_for_sa_email(sa_email: str) -> list:
    url = f"{constants.WEBSITE_URL}/get_study_options_for_sa_email"
    params = {"sa_email": sa_email}
    response = requests.get(url, params=params)
    return response.json().get("options")


def update_firestore(msg: str) -> bool:
    url = f"{constants.WEBSITE_URL}/update_firestore"
    params = {"msg": msg}
    response = requests.get(url, params=params)
    return response.status_code == 200
