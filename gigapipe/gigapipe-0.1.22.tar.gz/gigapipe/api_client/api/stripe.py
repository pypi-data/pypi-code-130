import requests
from http import HTTPStatus
from typing import Dict
from requests import Response
from gigapipe.api_client.gigapipe_api import GigapipeApi
from gigapipe.api_client.api import Base
from gigapipe.exceptions import GigapipeServerError, GigapipeClientError


class Stripe(Base):
    """
    Stripe Class
    """

    def __init__(self, api):
        """
        Stripe Constructor
        :param api: The API instance
        """
        super(Stripe, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_tax_id(self) -> Response:
        """
        Obtains the TAX ID of the organization
        :return: A dictionary containing the tax info | Message response if there's no tax id
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/stripe/customers/tax-id"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def post_tax_id(self, tax_object: Dict[str, str]) -> Response:
        """
        Posts a company TAX ID
        :return: A message response or an error dict
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/stripe/customers/tax-id"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=tax_object)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        except TypeError:
            raise GigapipeClientError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Wrong Payload"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_tax_id(self) -> Response:
        """
        Deletes a company TAX ID
        :return: A message response or an error dict
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/stripe/customers/tax-id"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

