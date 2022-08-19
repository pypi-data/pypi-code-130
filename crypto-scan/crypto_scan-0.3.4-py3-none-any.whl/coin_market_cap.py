import requests
import pandas as pd


class CoinMarketCap:

    def __init__(self, api_key):
        self.url = "https://pro-api.coinmarketcap.com/v1"
        # default parameters
        self.headers = {
            "X-CMC_PRO_API_KEY": api_key
        }
        self.default_parameters = {}

    def get_params(self, **kwargs):
        return {**self.default_parameters, **kwargs}

    def request_to_df(self, path, params={}):

        def _print_error(resp, e):
            print(f"ValueError: {e}")
            print(f"Resp: {resp}")
            print(f"Resp content: {resp.content}")
            print(f"Resp json: {resp.json()}")
            print("---" * 10)

        resp = requests.get(f"{self.url}{path}", params=self.get_params(**params), headers=self.headers)
        try:
            df = pd.DataFrame(list(resp.json()['data'].values()))
        except Exception as e:
            _print_error(resp, e)
            raise Exception(e)
        return df

    def get_latest_prices(self, tokens):
        path = "/cryptocurrency/quotes/latest"
        coin_price_df = self.request_to_df(path, params={
            "symbol": ','.join(tokens),
        })
        return coin_price_df
