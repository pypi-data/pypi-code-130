DEFAULT_DAYS = 10
DATE_FORMAT = "%Y-%m-%d"
DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_URL = "https://www.zomato.com/merchant-api/orders/fetch-orders-by-states"
DEFAULT_HEADERS = {
    "x-zomato-app-version": "2",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-ch-ua-platform": '"macOS"',
    "origin": "https://www.zomato.com",
    "content-type": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "accept": "application/json, text/plain, */*",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Referer": "https://www.zomato.com/partners/onlineordering/orderHistory/",
    "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}

__all__ = (
    "DATE_FORMAT",
    "DEFAULT_URL",
    "DEFAULT_DAYS",
    "DEFAULT_HEADERS",
    "DEFAULT_CONFIG_FILE",
)
