# vim: set fileencoding=utf-8:


from coronado import TripleObject
from coronado.baseobjects import BASE_MERCHANT_CATEGORY_CODE_DICT
from coronado.baseobjects import BASE_MERCHANT_DICT

import json

import requests


# +++ constants +++

SERVICE_PATH = 'partner/merchants'


# *** classes and objects ***


class Merchant(TripleObject):
    """
    """
    allAttributes = TripleObject(BASE_MERCHANT_DICT).listAttributes()

    def __init__(self, obj = BASE_MERCHANT_DICT):
        """
        Create a new Merchant instance.

        spec:

        ```
        {
          "externalID": "string",
          "assumedName": "string",
          "address": {
            "completeAddress": "7370 BAKER ST STE 100\nPITTSBURGH, PA 15206",
            "line1": "7370 BAKER ST STE 100",
            "line2": "string",
            "locality": "PITTSBURGH",
            "province": "PA",
            "postalCode": "15206",
            "countryCode": "US",
            "latitude": 40.440624,
            "longitude": -79.995888
          },
          "merchantCategoryCode": {
            "code": "7998"
          },
          "logoURL": "string"
        }
        ```
        """
        TripleObject.__init__(self, obj)

