import pandas as pd

from ._krx import get_json_data


class KrxStock:
    def __init__(self, date, market='ALL', share='1', money='1'):
        self.date = date.strftime('%Y%m%d')
        self.market = market  # 'ALL': 전체, 'STK': KOSPI, 'KSQ': KOSDAQ, 'KNX': KONEX
        self.share = share  # '1':주, '2':천주, '3':백만주
        self.money = money  # '1':원, '2':천원, '3':백만원, '4':십억원

        self.locale = 'ko_KR'
        self.csvxls_is_no = 'false'

    @staticmethod
    def get_output(params):
        dic = get_json_data(params)

        return pd.DataFrame(dic['OutBlock_1'])

    def s12001(self):
        """[12001] 전종목 시세
        :return:
        """
        bld = 'dbms/MDC/STAT/standard/MDCSTAT01501'

        params = {
            'bld': bld,
            'locale': self.locale,
            'mktId': self.market,
            'trdDd': self.date,
            'share': self.share,
            'money': self.money,
            'csvxls_isNo': self.csvxls_is_no
        }
        df = self.get_output(params)

        return df

    def s12005(self):
        """[12005] 전종목 기본정보
        :return:
        """
        bld = 'dbms/MDC/STAT/standard/MDCSTAT01901'

        params = {
            'bld': bld,
            'locale': self.locale,
            'mktId': self.market,
            'share': self.share,
            'csvxls_isNo': self.csvxls_is_no
        }
        df = self.get_output(params)

        return df
