import requests
import json

from ..response import ok, error


class Refund:
    def __init__(self, url: str, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, payment_id: str, amount: float = None) -> dict:
        data = {
            'amount': round(amount, 2) * 100 if amount else amount
        }
        r = requests.post(self.url + f'/payments/{payment_id}/refunds', headers=self.headers, data=json.dumps(data))
        if r.status_code > 400:
            return ok(r.json(), r.status_code)
        return error(r.json(), r.status_code)

