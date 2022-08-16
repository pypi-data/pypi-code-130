import logging
from urllib.parse import urlparse

import requests


class HedgeDoc:

    def __init__(self, base_url: str, email: str = None, password: str = None, username: str = None):
        self.url = base_url
        self.session = requests.Session()
        if email or username:
            self.login(email, username, password)

    def login(self, email: str = None, username: str = None, password: str = None):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if email:
            response = self.session.post(
                f"{self.url}/login",
                data={"email": email, "password": password},
                headers=headers,
            )
        else:
            response = self.session.post(
                f"{self.url}/auth/ldap",
                data={"username": username,
                      "password": password},
                headers=headers,
            )
        if response.ok:
            logging.info("logged in to hedgedoc")
        else:
            logging.error(response.text)
            logging.error(response.status_code)
            logging.error(response.headers)
            raise Exception(response.text)

    def create_note(self, text: str):
        response = self.session.post(
            f"{self.url}/new",
            data=text.encode("utf8"),
            headers={"Content-Type": "text/markdown; charset=UTF-8"},
        )
        if response.ok:
            logging.info(f"Note created url={response.url}")
            return response.url
        else:
            logging.error(response.text)
            logging.error(response.status_code)
            logging.error(response.headers)
            raise Exception(response.text)

    def get_note(self, url: str):
        parsed_url = urlparse(url)
        note_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if not note_url.endswith("/download"):
            note_url += "/download"
        response = self.session.get(note_url)
        if response.ok:
            return response.text
        else:
            logging.error(response.text)
            logging.error(response.status_code)
            logging.error(response.headers)
            raise Exception(response.text)
