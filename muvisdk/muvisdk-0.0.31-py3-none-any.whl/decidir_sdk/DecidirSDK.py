from .Customer import Customer
from .Card import Card
from .CardToken import CardToken
from .Payment import Payment
from .Refund import Refund


class DecidirSDK:
    def __init__(self, merchant: dict, merchant_cadena: dict = None):
        credentials = merchant['credentials']['decidir']
        self.url = 'https://developers.decidir.com/api/v2'
        self.private_key = credentials['access_token']
        self.public_key = credentials['public_key']
        self.merchant_name = merchant['name']
        self.site_ids = credentials['site_ids']     # distributed, cobro_por_uso, checkout, cobros_recurrentes
        self.site_ids_cadena = merchant_cadena['credentials']['decidir']['site_ids'] if merchant_cadena else None

    def customer(self):
        return Customer(self.url, self.private_key, self.public_key)
    
    def card(self):
        return Card(self.url, self.private_key, self.public_key)

    def card_token(self):
        return CardToken(self.url, self.private_key, self.public_key)

    def payment(self):
        return Payment(self.url, self.private_key, self.public_key, self.merchant_name, self.site_ids,
                       self.site_ids_cadena)

    def refund(self):
        return Refund(self.url, self.private_key, self.public_key)

    def ok(self):
        return self.private_key and self.public_key
