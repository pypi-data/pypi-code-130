import csv
import json
import logging
import time
from datetime import datetime

import ccxt
import pandas as pd
from ccxt.base.exchange import Exchange
from tqdm import tqdm

logger = logging.getLogger()
unix_month = 2678400000
one_hour = 3600 * 1000


class LoadDataKline:
    def __init__(self, exchange: Exchange, csv_path, *args, **kwargs):
        self.csv_path = csv_path
        self.exchange = exchange
        super(LoadDataKline, self).__init__(*args, **kwargs)

    def load_all(self, *args, **kwargs):
        self.exchange.load_markets()
        with open(self.csv_path, mode="w") as csv_f:
            csv_writer = csv.DictWriter(csv_f, delimiter=",",
                                        fieldnames=["symbol", "timestamp", "open", "close", "low", "high", "vol"])
            csv_writer.writeheader()

            pbr = tqdm(self.exchange.symbols)
            for sym in pbr:
                if ':' not in sym:
                    pbr.set_description(sym)
                    self.load(sym, csv_writer=csv_writer, *args, **kwargs)

    def _load(self, symbol, fetch_since, csv_writer, timeframe='1m', limit=100, try_times=3, *args, **kwargs):
        if try_times <= 0:
            return False, None

        try:
            result = self.exchange.fetch_ohlcv(symbol, timeframe, fetch_since, limit=limit)
            result = self.exchange.sort_by(result, 0)
            if len(result) == 0:
                return False, f'result is empty, fetch_since:{fetch_since}'

            df = pd.DataFrame(result, columns=['timestamp', 'open', 'close', 'low', 'high', 'vol'])
            df['symbol'] = symbol
            csv_writer.writerows(json.loads(df.to_json(orient='records')))
            time.sleep(int(self.exchange.rateLimit / 1000))
            return True, result
        except Exception as e:
            return self._load(symbol, fetch_since, csv_writer, timeframe, limit=limit, try_times=try_times - 1, *args,
                              **kwargs)

    def load(self, symbol, unix_start, unix_end, csv_writer, timeframe='1m', limit=100, *args, **kwargs):
        unix_delta = limit * self.exchange.parse_timeframe(timeframe) * 1000
        unix_temp = unix_start
        for _ in range(unix_end, unix_start, -unix_delta):
            status, result = self._load(symbol, unix_temp - unix_delta, csv_writer, timeframe=timeframe, limit=limit)
            if status is False:
                break
            unix_temp = result[0][0]


class LoadTradeKline:
    def __init__(self, exchange: Exchange, csv_path, *args, **kwargs):
        self.exchange = exchange
        self.csv_path = csv_path
        self.csv_writer = None
        super(LoadTradeKline, self).__init__(*args, **kwargs)

    def load_all(self, *args, **kwargs):
        self.exchange.load_markets()
        with open(self.csv_path, mode="w") as csv_f:
            csv_writer = csv.DictWriter(csv_f, delimiter=",",
                                        fieldnames=["symbol", "id", "timestamp", "type", "side", "price", "amount"])
            csv_writer.writeheader()
            pbr = tqdm(self.exchange.symbols)
            for sym in pbr:
                if ':' not in sym:
                    pbr.set_description(sym)
                    self.load(sym, csv_writer=csv_writer, *args, **kwargs)

    def load(self, symbol, unix_start, unix_end, csv_writer, *args, **kwargs):
        since = unix_start
        previous_trade_id = None
        result = []
        while since < unix_end:
            try:
                trades = self.exchange.fetch_trades(symbol, since, limit=1000)
                if len(trades) == 0:
                    since += one_hour
                    continue
                last_trade = trades[-1]
                if previous_trade_id == last_trade['id']:
                    since += one_hour
                    continue
                since = last_trade['timestamp']
                previous_trade_id = last_trade['id']

                result.extend([{
                    'symbol': trade['symbol'],
                    'id': trade['id'].replace('\n', ''),
                    'timestamp': trade['timestamp'],
                    'type': trade['type'],
                    'side': trade['side'],
                    'price': trade['price'],
                    'amount': trade['amount'],
                } for trade in trades])

                time.sleep(int(self.exchange.rateLimit / 1000))
                if len(result) > 30000:
                    self.write_data(csv_writer, result, unix_end)
                    result.clear()
            except ccxt.NetworkError as e:
                print(type(e).__name__, str(e))
                self.exchange.sleep(10000)
        if len(result) > 0:
            self.write_data(csv_writer, result, unix_end)

    def write_data(self, csv_writer, data_list, unix_end):
        df = pd.DataFrame(data_list)
        df = df[df['timestamp'] <= int(unix_end.timestamp() * 1000)]
        csv_writer.writerows(json.loads(df.to_json(orient='records')))
