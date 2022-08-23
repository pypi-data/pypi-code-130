import requests


class TLY_EXCEPTION(Exception):
    def __init__(self, message="An error occurred. Contact the developer of this package mailto:priom@priomdeb.com"
                               " or the t.ly support team mailto:support@t.ly"):
        self.message = message
        super().__init__(self.message)


class tly_shorturl:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        self.__MY_API_TOKEN = ""
        self.INCLUDE_QR_CODE = False
        self.MY_SHORT_URL = ""
        self.UPDATE_SHORT_URL_ID = ""

        self.SHORT_URL_STATS = "Call short_url_stats() to get stats"
        """SHORT_URL_STATS is a dictionary populated with numerous stats of the short url. You can get information 
from the dictionary using the following keys. 
        **Keys:** 'clicks', 'unique_clicks', 'browsers', 'countries', 'referrers', \n
        'platforms', 'daily_clicks', 'data'.

**'data'** key itself contain another dictionary. 
The keys of this dictionary are 'long_url', 'smart_urls', 'short_url', 'created_at', 'last_clicked',
'total_clicks_last_thirty_days'
        """

        self.SHORT_URL_INFO = "Call get_short_url_info() to get information about the short link"
        """SHORT_URL_INFO is a dictionary populated with information regarding the short url. \n
        **Keys:** 'short_url', 'long_url', 'domain', 'short_id', 'expire_at_views', 
        'expire_at_datetime', 'public_stats', 'description', 'qr_code_url', 'qr_code_base64'
        """

    # Initializing with setting up the API token
    def initialize(self, api_token):
        self.__MY_API_TOKEN = api_token
        return self.__MY_API_TOKEN

    # Creating short url
    def create_short_url(self, long_url=""):
        """Pass a long url into this method to create a short link of it"""

        # Checking the if an empty url is passed or not
        if long_url == "":
            raise TLY_EXCEPTION("create_short_url(long_url='?') No valid url is passed in the method!")

        url = 'https://t.ly/api/v1/link/shorten'
        payload = {
            "long_url": long_url,
            "domain": "https://t.ly/",
            "include_qr_code": False
        }
        params = {
            'api_token': self.__MY_API_TOKEN,
        }

        response = requests.request('POST', url, headers=self.headers, json=payload, params=params)
        return response.json()['short_url']

    # Get short url stats
    def short_url_stats(self, short_url=None, short_url_id=None):
        """Pass a short url or the id of a short url to see the stats of the short url.
        Please pass any 1 argument. Argument must be a string.
        """
        if short_url:
            params_short_url = short_url
        elif short_url_id:
            params_short_url = f"https://t.ly/{short_url_id}"
        else:
            raise TLY_EXCEPTION("short_url('?') nor short_url_id('?') No short url or short url id is passed!")

        url = 'https://t.ly/api/v1/link/stats'
        params = {
            'api_token': self.__MY_API_TOKEN,
            'short_url': params_short_url
        }

        response = requests.request('GET', url, headers=self.headers, params=params)

        try:
            if response.json()["message"] == "Short link not found":
                return "Short link not found"
        except KeyError:
            pass

        self.SHORT_URL_STATS = response.json()
        return response.json()

    # Get short url information
    def get_short_url_info(self, short_url):
        url = 'https://t.ly/api/v1/link'
        params = {
            'api_token': self.__MY_API_TOKEN,
            'short_url': short_url,
        }

        response = requests.request('GET', url, headers=self.headers, params=params)
        self.SHORT_URL_INFO = response.json()
        return response.json()

    # Edit short url settings
    def edit_url_settings(self,
                          current_short_url,
                          edit_short_id=None,
                          edit_long_url="",
                          edit_expire_at_datetime="",
                          edit_expire_at_views="",
                          edit_description="",
                          edit_public_stats=True,
                          edit_password="",
                          edit_include_qr_code=False
                          ):
        """By calling edit_url_settings() method you can change the settings of your short urls. \n
        You can edit url_short_id, long_id, expire_at_datetime, expire_at_views, description, public_stats,
        password, include_qr_codes. \n

        **The correct format for expire_at_datetime = 'YEAR-MONTH-DAY HOURS:MINUTES:SECONDS'** \n
        Date: Year 4 digits, month 2 digits and day 2 digits \n
        Time: 23 hours time and 2 digits for hours, 2 digits for minutes and 2 digits for seconds \n
        \n
        **For example, edit_expire_at_datetime='2022-08-30 15:00:00'**
        \n
        :returns updated/edited url info
        """

        url = 'https://t.ly/api/v1/link'
        payload = {
            "short_url": current_short_url,
            "short_id": edit_short_id,
            "long_url": edit_long_url,
            "expire_at_datetime": edit_expire_at_datetime,
            "expire_at_views": edit_expire_at_views,
            "description": edit_description,
            "public_stats": edit_public_stats,
            "password": edit_password,
            "include_qr_code": edit_include_qr_code
        }
        params = {
            'api_token': self.__MY_API_TOKEN,
        }

        response = requests.request('PUT', url, headers=self.headers, json=payload, params=params)
        return response.json()

    # Delete existing short url
    def delete_short_url(self, short_url):
        """This method will delete your existing short url. \n
        :return None
        """

        url = 'https://t.ly/api/v1/link'
        payload = {
            "short_url": short_url
        }
        params = {
            'api_token': self.__MY_API_TOKEN,
        }

        response = requests.request('DELETE', url, headers=self.headers, json=payload, params=params)
        return

    # Return the original long url and expiration status
    def expand(self, short_url, password=""):
        """This method returns the original long url and expiration status \n
        :return tuple(long_url, expired)
        """

        url = 'https://t.ly/api/v1/link/expand'
        payload = {
            "short_url": short_url,
            "password": password
        }
        params = {
            'api_token': self.__MY_API_TOKEN,
        }

        response = requests.request('POST', url, headers=self.headers, json=payload, params=params)
        response.json()
        return response.json()['long_url'], response.json()['expired']

