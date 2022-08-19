# -*- coding: utf-8 -*-

# Make Imports
## Built Ins
from datetime import datetime

## Data Structures
import pandas as pd

## Finanzen-Fundamentals
from finanzen_fundamentals.exceptions import NoDataException
from finanzen_fundamentals.scraper import _make_soup
from finanzen_fundamentals.functions import parse_price, parse_timestamp, parse_percentage, check_data
from finanzen_fundamentals.search import search
import finanzen_fundamentals.statics as statics


# Define Function to Extract ETF Data
def get_info(etf: str, output: str = "dataframe"):
    
    ## Transform User Input to Small Letters
    etf = etf.lower()
    output = output.lower()
    
    ## Check User Input
    output_allowed = ["dataframe", "dict"]
    if output not in output_allowed:
        raise ValueError("Output must be either one of: {}".format(", ".join(output_allowed)))
    
    ## Load Data
    soup = _make_soup("https://www.finanzen.net/etf/" + etf)

    ## Check for Data
    if not check_data(soup):
        raise NoDataException("Could not find ETF: {}".format(etf))
    
    ## Find WKN and ISIN
    try:
        wkn = soup.find("span", text="WKN:").next_sibling.strip()
    except Exception:
        wkn = None
    try:
        isin = soup.find("span", text="ISIN:").next_sibling.strip()
    except Exception:
        isin = None

    ## Find Fundamentals
    ### Find Base Table
    table_base = soup.find("div", {"id": "EtfBaseDataContent"})
    
    ### Define Function to Extract Value
    def get_value(table, text: str):
        value = table_base.find("div", text=text)\
            .findNext("div")\
            .get_text()\
            .strip()
        return value
    
    ### Extract Rows
    issuer = get_value(table_base, "Emittent")
    date_issue = get_value(table_base, "Auflagedatum")
    category = get_value(table_base, "Kategorie")
    currency = get_value(table_base, "Fondswährung")
    benchmark = get_value(table_base, "Benchmark")
    distribution = get_value(table_base, "Ausschüttungsart")
    expense_ratio = get_value(table_base, "Total Expense Ratio (TER)")
    volume = get_value(table_base, "Fondsgröße")
    replication = get_value(table_base, "Replikationsart ")
    
    ### Clean Values
    #### Issuer
    if issuer in ["", "-"]:
        issuer = None

    #### Issue Date
    if date_issue not in ["", "-"]:
        date_issue = datetime.strptime(date_issue, "%d.%m.%Y")
    else:
        date_issue = None
        
    #### Category
    if category in ["", "-"]:
        category = None
        
    #### Currency
    if currency in ["", "-"]:
        currency = None
        
    #### Benchmark
    if benchmark in ["", "-"]:
        benchmark = None
        
    #### Distribution
    if distribution in ["", "-"]:
        distribution = None
    
    #### Total Expense Ratio
    if expense_ratio not in ["", "-"]:
        try:
            expense_ratio = parse_percentage(expense_ratio)
        except Exception:
            expense_ratio = None
    else:
        expense_ratio = None
        
    #### Volume
    if volume not in ["", "-"]:
        try:
            volume = float(volume.replace(".", "").replace(",", "."))
        except Exception:
            volume = None
    else:
        volume = None
        
    #### Replication
    if replication in ["", "-"]:
        replication = None
    
    ## Put Result into Dictionary
    result = {
        "ETF": etf,
        "WKN": wkn,
        "ISIN": isin,
        "Issuer": issuer,
        "Issue Date": date_issue,
        "Category": category,
        "Currency": currency,
        "Benchmark": benchmark,
        "Distribution": distribution,
        "Expense Ratio": expense_ratio,
        "Volume": volume,
        "Replication": replication
    }
    
    ## Convert to Pandas DataFrame
    if output == "dataframe":
        result = pd.DataFrame([result])
        
    ## Return Result
    return result


# Define Function to Get Current Price
def get_price(etf: str, exchange: str = "FSE", output: str = "dataframe"):
    
    ## Transform User Input into Small Letters
    etf = etf.lower()
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
    url = f"https://www.finanzen.net/etf/{etf}/{exchange}"
    
    ## Create Soup
    soup = _make_soup(url)

    ## Check Data
    if not check_data(soup):
        raise NoDataException("Could not find ETF: {}".format(etf))
    
    ## Find Quotebox
    quotebox = soup.find("div", {"class": "quotebox"})
    
    ## Raise Error if no Price is Available
    if quotebox is None:
        raise NoDataException("No price available")
    else:
        quotebox = quotebox.find("tr")

    ## Extract Current Price
    try:
        price = quotebox.find("td").get_text()
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
        "ETF": etf,
        "Exchange": exchange
        }
    
    ## Convert to Pandas if wanted
    if output == "dataframe":
        result = pd.DataFrame([result])
    
    ## Return Result
    return result
    

# Define Function to Search ETF
def search_etf(etf: str, limit: int = -1):
    
    ## Get Search Result
    result = search(term=etf, category="etf", limit=limit)
    
    ## Return Result
    return result
