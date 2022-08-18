import mercadopago

from ..response import ok, error


class CardToken:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, card: dict):
        if 'mercadopago_id' in card:
            card['id'] = card['mercadopago_id']

        data = {
            "card_id": card['id']
        }
        card_token_response = self.sdk.card_token().create(data)

        if card_token_response["status"] > 299:
            return error({'message': 'Falló la creación de token de la tarjeta.'}, card_token_response["status"])

        # Para estandarizar la response con decidir
        if 'first_six_digits' in card:
            card_token_response['response']['bin'] = card['first_six_digits']
        elif 'bin' in card:
            card_token_response['response']['bin'] = card['bin']
        card_token_response['response']['last_four_digits'] = card['last_four_digits']
        card_token_response['response']['expiration_month'] = card['expiration_month']
        card_token_response['response']['expiration_year'] = card['expiration_year']
        card_token_response['response']['cardholder'] = card['cardholder']
        return ok(card_token_response["response"], card_token_response["status"])
