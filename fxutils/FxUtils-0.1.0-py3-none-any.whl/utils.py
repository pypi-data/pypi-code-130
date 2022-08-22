



# Margin required in dollar for unit lot, with 1:1 lerverage
# Parsed from https://www.forex.com/en-us/support/margin-pip-calculator/
MARGIN_UNIT = {'AUDUSD': 73412,
 'EURUSD': 117478,
 'GBPUSD': 138016,
 'USDCAD': 100000,
 'USDCHF': 100000,
 'USDJPY': 100000,
 'AUDCAD': 73413,
 'AUDCHF': 73405,
 'AUDJPY': 73410,
 'AUDNZD': 73378,
 'CADCHF': 79874,
 'CADJPY': 79875,
 'CHFJPY': 108442,
 'EURAUD': 117441,
 'EURCAD': 117467,
 'EURCHF': 117466,
 'EURGBP': 117449,
 'EURJPY': 117465,
 'EURNZD': 117408,
 'EURSGD': 135704,
 'GBPAUD': 137983,
 'GBPCAD': 138011,
 'GBPCHF': 138010,
 'GBPJPY': 138011,
 'GBPNZD': 137960,
 'NZDCAD': 70031,
 'NZDCHF': 70030,
 'NZDJPY': 70040,
 'NZDUSD': 70037,
 'XAGUSD': 11653,
 'XAUUSD': 175849}

"""
# From myfxbook https://www.myfxbook.com/forex-calculators/pip-calculator
# Currency	Standard Lot	Mini Lot	Micro Lot	Price	Pip value

PipValue = {}
for string in pip_value_raw.split('\n')[1:-1]:
    row = string.replace('\t', '').split('$')[:2]
    PipValue[row[0]] = float(row[1].replace(',', ''))

"""
PIP_VALUE = {
    'AUDCAD': 7.7932,
    'AUDCHF': 10.88198,
    'AUDJPY': 9.11012,
    'AUDNZD': 6.817,
    'AUDSGD': 7.32649,
    'AUDUSD': 10.0,
    'CADCHF': 10.88198,
    'CADJPY': 9.11012,
    'CHFJPY': 9.11012,
    'CHFSGD': 7.32649,
    'EURAUD': 7.1449,
    'EURCAD': 7.7932,
    'EURCHF': 10.88198,
    'EURCZK': 0.45749,
    'EURGBP': 13.629,
    'EURHUF': 3.32827,
    'EURJPY': 9.11012,
    'EURMXN': 0.49553,
    'EURNOK': 1.10636,
    'EURNZD': 6.817,
    'EURPLN': 2.54996,
    'EURSGD': 7.32649,
    'EURTRY': 1.17305,
    'EURUSD': 10.0,
    'EURZAR': 0.65709,
    'GBPAUD': 7.1449,
    'GBPCAD': 7.7932,
    'GBPCHF': 10.88198,
    'GBPJPY': 9.11012,
    'GBPNZD': 6.817,
    'GBPUSD': 10.0,
    'NZDCAD': 7.7932,
    'NZDCHF': 10.88198,
    'NZDJPY': 9.11012,
    'NZDUSD': 10.0,
    'USDCAD': 7.7932,
    'USDCHF': 10.88198,
    'USDJPY': 9.11012,
    'USDSGD': 7.32649,
    'XAGUSD': 500.0,
    'XAUUSD': 10.0
} 

ALL_SYMBOLS = PIP_VALUE.keys()


def get_pippoint(Symbol):
    if 'JPY' in Symbol.upper():
        return 100
    elif 'XAU' in Symbol.upper():
        return 10
    elif 'XAG' in Symbol.upper():
        return 1000
    else:
        return 10000

def standardize_symbol(Symbol):
    for Symbol_standard in ALL_SYMBOLS:
        if Symbol_standard in Symbol:
            Symbol = Symbol_standard
    assert Symbol in ALL_SYMBOLS, f'{Symbol} not found!'
    return Symbol
        