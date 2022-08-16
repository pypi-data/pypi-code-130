from .mercadopago_sdk.MercadoPagoSDK import MercadoPagoSDK
from .decidir_sdk.DecidirSDK import DecidirSDK


class SDK:
    def __init__(self, merchant: dict, processor: str = None, merchant_cadena: dict = None):
        # Si se le indica el procesador
        self.processor = processor
        if processor == 'mercadopago' and merchant['credentials']['mercadopago']['active']:
            self._sdk = MercadoPagoSDK(merchant)
            return
        elif processor == 'mp_marketplace' and merchant['credentials']['mp_marketplace']['active']:
            self._sdk = MercadoPagoSDK(merchant, marketplace=True)
            return
        elif processor == 'decidir' and merchant['credentials']['decidir']['active']:
            self._sdk = DecidirSDK(merchant, merchant_cadena)

    def customer(self):
        return self._sdk.customer()

    def card(self):
        return self._sdk.card()

    def card_token(self):
        return self._sdk.card_token()

    def payment(self):
        return self._sdk.payment()

    def refund(self):
        return self._sdk.refund()

    def which(self):
        return self.processor

