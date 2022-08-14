from http import HTTPStatus

import aiohttp
from utils.logging import get_logger

from stock_market.common.json_mixins import SingleAttributeJsonMixin
from stock_market.core import OHLC, OHLCFetcher, Ticker

logger = get_logger(__name__)


class ProxyOHLCFetcher(OHLCFetcher, SingleAttributeJsonMixin):
    JSON_ATTRIBUTE_NAME = "api_url"
    JSON_ATTRIBUTE_TYPE = "string"

    def __init__(self, api_url):
        super().__init__("proxy")
        self.api_url = api_url

    async def fetch_ohlc(self, requests):
        json_request = {
            "requests": [
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "ticker": {"symbol": ticker.symbol},
                }
                for start_date, end_date, ticker in requests
            ]
        }

        async with aiohttp.ClientSession() as client:
            response = await client.post(
                self.api_url,
                json=json_request,
            )
            if response.status != HTTPStatus.OK:
                logger.warning(f"No new ohlc data from proxy request: {json_request}")
                return None

            ohlc_data = await response.json()
        return [
            (Ticker.from_json(ticker), OHLC.from_json(ohlc))
            for ticker, ohlc in ohlc_data
        ]

    def __eq__(self, other):
        if not isinstance(other, ProxyOHLCFetcher):
            return False
        return self.api_url == other.api_url
