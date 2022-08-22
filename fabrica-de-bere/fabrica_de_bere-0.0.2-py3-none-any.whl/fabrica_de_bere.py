import logging
from datetime import datetime
from functools import wraps
from typing import Iterator
from urllib import response
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

import fabrica_de_bere.config as config
from fabrica_de_bere.beer import Beer
from fabrica_de_bere.cache import CallsCache

LOGGER = logging.getLogger("fabrica_de_bere")


class FabricaDeBere:
    """Wrapper for the Punk API."""

    def __init__(self, base_url=config.PUNK_API_BASE_URL):
        self.base_url = urljoin(base_url, "beers/")
        self.calls_cache = CallsCache()

    @staticmethod
    def raise_for_status_with_message(response: response):
        """
        Raises an error with a detailed message
        if the response status is between 400 and 599.
        """
        if 400 <= response.status_code < 500:
            msg = "Client Error: "
        elif 500 <= response.status_code < 600:
            msg = "Server Error: "
        else:
            return

        msg += response.json().get("message", "")
        for error_data in response.json().get("data", []):
            msg += "\n" + error_data.get("param") + ": " + error_data.get("msg")

        if msg:
            raise ValueError(msg)

    def check_cache(f):
        @wraps(f)
        def inside(self, *args, **kwargs):
            if kwargs.get("params"):
                function_params = (args, frozenset(kwargs.get("params").items()))
            else:
                function_params = (args, frozenset())
            result = self.calls_cache.search_call(function_params)
            if result:
                LOGGER.warning("Found in cache...")
                return result
            else:
                LOGGER.warning("Not found in cache... making the call")
                result = f(self, *args, **kwargs)
                self.calls_cache.add_call(function_params, result)
                return result

        return inside

    @check_cache
    def get_request(self, url, params: dict = None):
        """Returns the response of the get request for the given url and parameters."""
        with requests.Session() as ses:
            if params:
                LOGGER.warning(f"Getting the request from {url} with {params}")
            else:
                LOGGER.warning(f"Getting the request from {url}")
            retries = Retry(
                total=config.RETRY_TOTAL,
                backoff_factor=config.RETRY_BACKOFF,
                status_forcelist=config.RETRY_FORCELIST,
            )
            ses.mount("https://", HTTPAdapter(max_retries=retries))

            response = ses.get(
                url,
                params=params,
            )
            FabricaDeBere.raise_for_status_with_message(response)

            return response.json()

    def clear_cache(self):
        self.calls_cache.clear_cache()

    def get_beers(
        self,
        page: int = 1,
        per_page: int = None,
        abv_gt: float = None,
        abv_lt: float = None,
        ibu_gt: int = None,
        ibu_lt: int = None,
        ebc_gt: int = None,
        ebc_lt: int = None,
        beer_name: str = None,
        yeast: str = None,
        brewed_before: datetime = None,
        brewed_after: datetime = None,
        hops: str = None,
        malt: str = None,
        food: str = None,
        ids: list[int] = None,
    ) -> Iterator[Beer]:
        """
        The function gets the beers,
        filtering them out based on the given parameters.
        """
        while True:
            param = {
                "page": page,
                "per_page": per_page,
                "abv_gt": abv_gt,
                "abv_lt": abv_lt,
                "ibu_gt": ibu_gt,
                "ibu_lt": ibu_lt,
                "ebc_gt": ebc_gt,
                "ebc_lt": ebc_lt,
                "beer_name": beer_name,
                "yeast": yeast,
                "hops": hops,
                "malt": malt,
                "food": food,
            }
            if ids:
                param["ids"] = "|".join(map(str, ids))
            if brewed_before:
                param["brewed_before"] = f"{brewed_before.month}-{brewed_before.year}"
            if brewed_after:
                param["brewed_after"] = f"{brewed_after.month}-{brewed_after.year}"

            logging.info(f"Getting beers with the given params: {param.items()}")

            response = self.get_request(self.base_url, params=param)
            if not response:
                break
            for beer in response:
                beer = Beer(beer)
                LOGGER.info(beer)
                yield beer
            page += 1

    def get_all_beers(self) -> Iterator[Beer]:
        """The function gets all the beers."""
        logging.info("Getting all beers..")
        return self.get_beers(per_page=config.MAX_BEERS_PER_PAGE)

    def get_beer_by_id(self, beer_id: int) -> Beer:
        """Returns a beer object with the given id."""
        LOGGER.info(f"Getting beer with id {beer_id}")
        url = urljoin(self.base_url, str(beer_id))
        response_json = self.get_request(url)

        beer = Beer(response_json[0])
        LOGGER.info(beer)

        return beer

    def get_random_beer(self) -> Beer:
        """Returns a random beer object."""
        LOGGER.info("Getting a random beer..")

        url = urljoin(self.base_url, "random")
        response_json = self.get_request(url)

        beer = Beer(response_json[0])
        LOGGER.info(beer)

        return beer
