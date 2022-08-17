import json

from typing import Union
from requests import Session
from bs4 import BeautifulSoup
from datetime import datetime

class InvalidCookie(Exception):
    def __init__(self) -> None:
        super().__init__('Cookie is invalid')


class Textnow:
    def __init__(self, sid_cookie, csrf_cookie) -> None:
        self.sid_cookie = sid_cookie
        self.csrf_cookie = csrf_cookie

        self.cookies = {
            '_csrf': csrf_cookie,
            'connect.sid': sid_cookie
        }

        self.session = Session()
        self.username, self.csrf_header = self.get_data()

        self.session.headers.update(
            {
                'x-csrf-token': self.csrf_header
            }
        )

    def get_data(self) -> Union[str, None]:
        response = self.session.get('https://www.textnow.com/messaging', cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            token = soup.find('meta', {'name': 'csrf-token'}).get('content')
        except AttributeError:
            raise InvalidCookie

        for line in response.text.splitlines():
            if 'window.sessionUsername = ' in line:
                username = line.split('"')[1]

        return (username, token)

    def send_sms(self, number, message) -> bool:
        data = {
            'json': json.dumps(
                {
                    'from_name': '',
                    'has_video': 'false',
                    'contact_value': f'+1{number.replace("+1", "")}',
                    'contact_type': 2,
                    'message': message,
                    'read': 1,
                    'message_direction': 2,
                    'message_type': 1,
                    'new': True,
                    'date': datetime.utcnow().isoformat()
                }
            )
        }

        response = self.session.post(f'https://www.textnow.com/api/users/{self.username}/messages', cookies=self.cookies, data=data)

        if '"id"' in response.text:
            return True

        else:
            return False

