import mercadopago
from iso8601 import parse_date
from datetime import datetime
from ..response import ok, error


def _format_card(response):
    return {
        'id': response['card']['id'],
        'card_type': response['payment_type_id'],
        'last_four_digits': response['card']['last_four_digits'],
        'cardholder': {
            'name': response['card']['cardholder']['name']
        },
        'expiration_month': response['card']['expiration_month'],
        'expiration_year': response['card']['expiration_year'],
    }


def _format(response):
    return {
        'id': response['id'],
        'transaction_amount': response['transaction_amount'],
        'date_created': parse_date(response['date_created']),
        'status': response['status'],
        'status_detail': response['status_detail'],
        'card': _format_card(response),
        'processor': 'mercadopago',
        'payment_day':datetime.now()
    }


class Payment:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, payment_data: dict):
        payment_data = payment_data.copy()
        payment_data_mp = {
            "notification_url": None,
            "transaction_amount": round(payment_data['transaction_amount'], 2),
            "token": payment_data['token'],
            "installments": 1,
        }

        optional_fields = [
            'additional_info',
            'description',
            'external_reference',
            'point_of_interaction',
            'installments',
            'payment_method_id',
            'application_fee'
        ]
        for f in optional_fields:
            if f in payment_data:
                payment_data_mp[f] = payment_data[f]

        if 'payer' in payment_data:
            payment_data_mp["payer"] = {
                "first_name": payment_data['payer']["first_name"],
                "last_name": payment_data['payer']["last_name"],
                "address": None
            }
            if 'mercadopago_id' in payment_data['payer']:
                payment_data_mp['payer']['id'] = payment_data['payer']["mercadopago_id"]
            elif 'email' in payment_data['payer']:
                payment_data_mp['payer']['email'] = payment_data['payer']["email"]

        payment_response = self.sdk.payment().create(payment_data_mp)
        if payment_response['status'] < 400:
            return ok(_format(payment_response['response']))

        payment_response['response']['processor'] = 'mercadopago'
        return error(payment_response['response'])

    def get(self, payment_id: int):
        payment_response = self.sdk.payment().get(payment_id)
        if payment_response['status'] < 400:
            return ok(payment_response['response'])

        return error(payment_response['response'])
