# -*- coding: utf-8 -*-

# Make Imports
import re
from datetime import datetime
from finanzen_fundamentals.exceptions import ParsingException


# Define Function to Extract Price and Currency
def parse_price(price_str: str):
    price_str = re.search(r"([\d,]+)(\D+)", price_str)
    price_float = float(price_str.group(1).replace(",", "."))
    currency = price_str.group(2).strip()
    return price_float, currency


# Define Function to Parse Timestamp from Price
def parse_timestamp(timestamp_str: str):
    
    if "T" in timestamp_str:
        timestamp_format = "%Y-%m-%dT%H:%M:%S"
        timestamp = datetime.strptime(timestamp_str, timestamp_format)
    elif ":" in timestamp_str:
        if "Uhr" in timestamp_str:
            timestamp_str = timestamp_str.replace("Uhr", "").strip()
            timestamp_format = "%H:%M"
        else:
            timestamp_format = "%H:%M:%S"
        now = datetime.now()
        timestamp = datetime.strptime(timestamp_str, timestamp_format)
        timestamp = timestamp.replace(year=now.year, month=now.month, day=now.day)
    elif "." in timestamp_str:
        if len(timestamp_str) == 8:
            timestamp_format = "%d.%m.%y"
        else:
            timestamp_format = "%d.%m.%Y"
        timestamp = datetime.strptime(timestamp_str, timestamp_format)
    else:
        raise ParsingException("Can not parse timestamp")
    return timestamp

# Define Function to Extract Percentage
def parse_percentage(percentage_str: str):
    
    ## Replace Comma with Dot
    percentage_str = percentage_str.replace(",", ".")
    
    ## Extract Number
    percentage = re.search(r"-?\d+\.\d+", percentage_str)
    if percentage is None:
        raise ParsingException("Can not Find Percentage")
    else:
        percentage = float(percentage.group(0))
        
    ## Return Result
    return percentage


# Parse Decimal
def parse_decimal(decimal_str: str):
    
    ## Replace Comma with Dot
    decimal_str = decimal_str.replace(",", ".")
    
    ## Convert to Float
    decimal = float(decimal_str)
    
    ## Return Result
    return decimal


# Check for Data
def check_data(soup):

    ## Check if Error Message on Site
    msg_error = "Die gewünschte Seite kann nicht angezeigt werden"
    if msg_error in soup.get_text():
        result = False
    else:
        result = True

    ## Return Result
    return result
