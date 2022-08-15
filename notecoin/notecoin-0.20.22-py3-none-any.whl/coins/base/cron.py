import logging

from ccxt import okex
from notecoin.coins.base.file import DataFileProperty

logger = logging.getLogger()
logger.setLevel(logging.INFO)

path_root = '/home/bingtao/workspace/tmp'


def load():
    file_pro = DataFileProperty(exchange=okex(),  path=path_root)
    file_pro.change_data_type('trade')
    file_pro.change_timeframe('detail')
    file_pro.change_freq('daily')
    file_pro.load(total=450)
    file_pro.change_freq('weekly')
    file_pro.load(total=60)

    file_pro.change_data_type('kline')
    file_pro.change_timeframe('1m')
    file_pro.change_freq('daily')
    file_pro.load(total=450)
    file_pro.change_freq('weekly')
    file_pro.load(total=60)


load()

