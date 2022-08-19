# -*- coding: utf-8 -*-

# Make Imports
## Built Ins
import re

## Data Structures
import pandas as pd

## Finanzen-Fundamentals
from finanzen_fundamentals.exceptions import NoDataException, ParsingException
from finanzen_fundamentals.scraper import _make_soup
from finanzen_fundamentals.functions import parse_price, parse_timestamp, parse_percentage, parse_decimal, check_data
from finanzen_fundamentals.search import search
import finanzen_fundamentals.statics as statics


# Define Function to Extract Info
def get_info(fund: str, output: str = "dataframe"):

    ## Transform User Input to Small Letters
    fund = fund.lower()
    output = output.lower()

    ## Check User Input
    output_allowed = ["dataframe", "dict"]
    if output not in output_allowed:
        raise ValueError("Output must be either one of: {}".format(", ".join(output_allowed)))

    ## Load Data
    soup = _make_soup("https://www.finanzen.net/fonds/" + fund)

    ## Check Data
    if not check_data(soup):
        raise NoDataException("Could not find fund: {}".format(fund))

    ## Find WKN and ISIN
    try:
        wkn = soup.find("span", cptxt="WKN")["cpval"]
    except Exception:
        wkn = None
    try:
        isin = soup.find("span", cptxt="ISIN")["cpval"]
    except Exception:
        isin = None

    ## Find Fundamentals
    ### Find Base Table
    table_base = soup.find("h2", {"class": "box-headline"},
                           text = "Wichtige Kennzahlen").parent
    table_rows = table_base.find_all("tr")

    ### Define Function to Extract Row
    def extract_row(rows, text: str):
        extract = [x for x in rows if x.find("strong", text=text) is not None]
        if len(extract) > 0:
            extract = extract[0].find("td", {"class": "text-right"}).get_text().strip()
        else:
            extract = None
        return extract

    ### Extract Rows
    issuer = extract_row(table_rows, "Fondsgesellschaft")
    currency = extract_row(table_rows, "Währung")
    premium = extract_row(table_rows, "Ausgabeaufschlag regulär")
    expense_ratio = extract_row(table_rows, "Total Expense Ratio (TER)")
    benchmark = extract_row(table_rows, "Benchmark")
    volume = extract_row(table_rows, "Fondsvolumen")
    distribution = extract_row(table_rows, "Ausschüttungsart")
    capture_ratio_up = extract_row(table_rows, "Capture Ratio Up")
    capture_ratio_down = extract_row(table_rows, "Capture Ratio Down")
    batting_average = extract_row(table_rows, "Batting Average")
    alpha = extract_row(table_rows, "Alpha")
    beta = extract_row(table_rows, "Beta")
    r2 = extract_row(table_rows, "R2")
    perf_1y = table_base.find("a", {"href": "#moreperformance"})\
        .parent\
        .parent\
        .parent\
        .find("span")\
        .get_text()\
        .strip()
    vola_1y = table_base.find("a", {"href": "#morevola"})\
        .parent\
        .parent\
        .parent\
        .find("td", {"class": "text-right"})\
        .get_text()\
        .strip()

    ### Clean Rows
    #### Define Function to Clean Percentages
    def clean_percentage(percentage: str):
        try:
            percentage = parse_percentage(percentage)
        except ParsingException:
            percentage = None
        return percentage

    #### Issuer
    if issuer in ["-", ""]:
        issuer = None

    #### Currency
    if currency in ["-", ""]:
        currency = None

    ####  Premiums
    if premium not in ["-", ""]:
        premium = clean_percentage(premium)
    else:
        premium = None

    #### Expense Ratio
    if expense_ratio not in ["-", ""]:
        expense_ratio = clean_percentage(expense_ratio)
    else:
        expense_ratio = None

    #### Benchmark
    if benchmark in ["-", "", "N/A"]:
        benchmark = None

    #### Volume
    if volume not in ["-", ""] and not volume.startswith("0,00"):
        ##### Get Currency
        multiplier = re.search(r"Mio\.|Mrd\.", volume)
        if multiplier is not None:
            multiplier = multiplier.group(0)
            multiplier_map = {"Mio.": 1000000, "Mrd.": 1000000000}
            multiplier = multiplier_map[multiplier]
        else:
            multiplier = 1

        ##### Get Numerical Value of Volume
        volume = re.search(r"^[\d\,]+", volume).group(0).replace(",", ".")
        volume = round(float(volume) * multiplier, 2)
    else:
        volume = None

    #### Distribution
    if distribution in ["-", ""]:
        distribution = None

    #### Caputre Ratio Up
    if capture_ratio_up not in ["-", ""]:
        capture_ratio_up = parse_decimal(capture_ratio_up)
    else:
        capture_ratio_up = None

    #### Capture Ratio Down
    if capture_ratio_down not in ["-", ""]:
        capture_ratio_down = parse_decimal(capture_ratio_down)
    else:
        capture_ratio_down = None

    #### Batting Average
    if batting_average not in ["-", ""]:
        batting_average = parse_percentage(batting_average)
    else:
        batting_average = None

    #### Alpha
    if alpha not in ["-", ""]:
        alpha = parse_decimal(alpha)
    else:
        alpha = None

    #### Beta
    if beta not in ["-", ""]:
        beta = parse_decimal(beta)
    else:
        beta = None

    #### R2
    if r2 not in ["-", ""]:
        r2 = parse_percentage(r2)
    else:
        r2 = None

    #### Performance
    if perf_1y not in ["-", ""]:
        perf_1y = parse_percentage(perf_1y)

    #### Volatility
    if vola_1y not in ["-", ""]:
        vola_1y = parse_percentage(vola_1y)

    ## Create Result Dict
    result = {
        "Fund": fund,
        "WKN": wkn,
        "ISIN": isin,
        "Issuer": issuer,
        "Currency": currency,
        "Premium": premium,
        "Expense Ratio": expense_ratio,
        "Benchmark": benchmark,
        "Volume": volume,
        "Distribution": distribution,
        "Performance 1Y": perf_1y,
        "Volatility 1Y": vola_1y,
        "Capture Ratio Up": capture_ratio_up,
        "Capture Ratio Down": capture_ratio_down,
        "Batting Average": batting_average,
        "Alpha": alpha,
        "Beta": beta,
        "R2": r2
        }

    ## Convert to Pandas DataFrame
    if output == "dataframe":
        result = pd.DataFrame([result])

    ## Return Result
    return result


# Define Function to Get Current Price
def get_price(fund: str, exchange: str = "FSE", output: str = "dataframe"):

    ## Transform User Input into Small Letters
    fund = fund.lower()
    exchange = exchange.upper()
    output = output.lower()

    ## Check User Input
    if output not in ["dataframe", "dict"]:
        raise ValueError("output must either be 'dict' or 'dataframe'")

    ## Check that Exchange is Valid
    if exchange not in statics.exchanges:
        exchanges_str = ", ".join(statics.exchanges)
        raise ValueError("'exchange' must be either one of: " + exchanges_str)

    ## Create URL
    url = f"https://www.finanzen.net/fonds/{fund}/{exchange}"

    ## Create Soup
    soup = _make_soup(url)

    ## Check Data
    if not check_data(soup):
        raise NoDataException("Could not find fund: {}".format(fund))

    ## Find Quotebox
    quotebox = soup.find("div", {"class": "quotebox"})

    ## Raise Error if no Price is Available
    if quotebox is None:
        raise NoDataException("No price available")
    else:
        price = quotebox.find("div", {"class": "text-nowrap"})

    ## Extract Current Price
    try:
        price = price.get_text()
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
        "Fund": fund,
        "Exchange": exchange
        }

    ## Convert to Pandas if wanted
    if output == "dataframe":
        result = pd.DataFrame([result])

    ## Return Result
    return result


# Search Function
def search_fund(fund: str, limit: int = -1):

    ## Get Search Result
    result = search(term=fund, category="fund", limit=limit)

    ## Return Result
    return result
