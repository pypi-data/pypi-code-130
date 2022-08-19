# -*- coding: utf-8 -*-

# Make Imports
## Built Ins
import re

## Data Structures
import pandas as pd

## Finanzen-Fundamentals
from finanzen_fundamentals.exceptions import NoDataException
from finanzen_fundamentals.scraper import _make_soup
from finanzen_fundamentals.functions import parse_price, parse_timestamp, check_data
from finanzen_fundamentals.search import search


# Define Function to Extract Commodity Data
def get_info(commodity: str, output: str = "dataframe"):

    ## Transform User Input to Lower Case
    commodity = commodity.lower()
    output = output.lower()

    ## Check User Input
    output_allowed = ["dataframe", "dict"]
    if output not in output_allowed:
        msg_error = "Output must be either one of: {}".format(", ".join(output_allowed))
        raise ValueError(msg_error)

    ## Load Data
    soup = _make_soup("https://www.finanzen.net/rohstoffe/" + commodity)

    ## Check for Data
    if not check_data(soup):
        raise NoDataException("Could not find commodity: {}".format(commodity))

    ## Find Base Value
    try:
        base_header = soup.find("h2", text=re.compile("Einheitenumrechnung"))
        base = base_header.parent.find("td").get_text()
        base = re.search(r"(\d+) (.+) =", base)
        value = base.group(1)
        metric = base.group(2)
    except Exception:
        value = None
        metric = None

    ## Put into Dictionary
    result = {
        "Commodity": commodity,
        "Value": value,
        "Metric": metric
            }

    ## Convert to Pandas Dataframe
    if output == "dataframe":
        result = pd.DataFrame([result])

    ## Return Result
    return result


# Define Function to Get Current Price
def get_price(commodity: str, currency: str, output: str = "dataframe"):

    ## Transform Input to Lower Case
    commodity = commodity.lower()
    currency = currency.lower()
    output = output.lower()

    ## Check User Input
    ### Currency
    currency_allowed = ["eur", "usd", "chf", "gbp", "myr"]
    if currency not in currency_allowed:
        msg_error = "Currency must bei either one of: " + ", ".join(currency_allowed)
        raise ValueError(msg_error)

    ### Output
    output_allowed = ["dataframe", "dict"]
    if output not in output_allowed:
        msg_error = "Output must be either one of: " + ", ".join(output_allowed)
        raise ValueError(msg_error)

    ## Create URL
    url = f"https://www.finanzen.net/rohstoffe/{commodity}/{currency}"

    ## Create Soup
    soup = _make_soup(url)

    ## Check for Data
    if not check_data(soup):
        raise NoDataException("Could not find commodity: {}".format(commodity))

    ## Find Quote Box
    quoteboxes = soup.find_all("div", {"class": "quotebox"})
    quotebox = [x for x in quoteboxes if currency.upper() in x.get_text()]
    if len(quotebox) > 0:
        quotebox = quotebox[0]
    else:
        raise NoDataException("No data for currency " + currency.upper())

    ## Extract Current Price
    try:
        price = quotebox.find("div", {"class": "col-xs-5"}).get_text()
    except Exception:
        raise NoDataException("No price available")

    price_float, currency = parse_price(price)

    ## Get Timestamp
    timestamp_str = quotebox.find("div", {"class": "quotebox-time"}).get_text().strip()
    timestamp = parse_timestamp(timestamp_str)

    ## Create Result Dict
    result = {
        "Price": price_float,
        "Currency": currency,
        "Timestamp": timestamp,
        "Commodity": commodity
            }

    ## Convert to Pandas if wanted
    if output == "dataframe":
        result = pd.DataFrame([result])

    ## Return Result
    return result


# Define Function to Search Commodity
def search_commodity(commodity: str, limit: int = -1):

    ## Get Search Result
    result = search(term=commodity, category="commodity", limit=limit)

    ## Return Result
    return result
