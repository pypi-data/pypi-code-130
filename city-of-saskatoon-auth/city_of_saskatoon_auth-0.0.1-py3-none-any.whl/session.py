import requests
import pickle

from .cos_login import cos_login
from .smart_util_login import smart_util_login

class Session:
    sess = requests.session()

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @classmethod
    def from_archive(cls, archive: bytes):
        unpickled = pickle.loads(archive)
        session = cls(unpickled['username'], unpickled['password'])
        cookie_jar = requests.cookies.RequestsCookieJar()
        cookie_jar._cookies = pickle.loads(unpickled['cookies'])
        session.sess.cookies = cookie_jar
        return session


    def to_archive(self) -> bytes:
        cookies = pickle.dumps(self.sess.cookies._cookies)
        return pickle.dumps({
            'username': self.username,
            'password': self.password,
            'cookies': cookies
        })

    # Authenticate with the main City of Saskatoon website
    def login(self) -> None:
        cos_login(self)
    
    # Authenticate with the MySmartUtil service
    # Must first authenticate with the main website using login()
    def smart_util_login(self) -> None:
        smart_util_login(self)

    # Makes a GET request with the current session
    def get(self, *args, **kwargs):
        print(f'GET {args[0]}')
        resp = self.sess.get(*args, **kwargs)
        self._print_resp(resp)
        return resp

    # Makes a POST request with the current session
    def post(self, *args, **kwargs):
        print(f'POST {args[0]}')
        resp = self.sess.post(*args, **kwargs)
        self._print_resp(resp)
        return resp

    def _print_resp(self, resp: requests.Response) -> None:
        print(f'Status Code: {resp.status_code}')