import pandas as pd

from ._krx import get_json_data


class KrxIndex:
    def __init__(self, date, sector='01', share='2', money='3'):
        self.date = date.strftime('%Y%m%d')
        self.sector = sector  # '01': KRX, '02': KOSPI, '03': KOSDAQ, '04': 테마
        self.share = share  # '1':주, '2':천주, '3':백만주
        self.money = money  # '1':원, '2':천원, '3':백만원, '4':십억원

        self.locale = 'ko_KR'
        self.csvxls_is_no = 'false'

    @staticmethod
    def get_output(params):
        # params['name'] = 'fileDown'
        # params['url'] = params['bld']
        # del params['bld']
        # csv = download_csv(params)
        # return pd.read_csv(csv, encoding='utf-8')

        dic = get_json_data(params)

        return pd.DataFrame(dic['output'])

    def s11001(self):
        """[11001] 전체지수 시세
        :return:
        """
        bld = 'dbms/MDC/STAT/standard/MDCSTAT00101'

        params = {
            'bld': bld,
            'locale': self.locale,
            'idxIndMidclssCd': self.sector,
            'trdDd': self.date,
            'share': self.share,
            'money': self.money,
            'csvxls_isNo': self.csvxls_is_no
        }
        df = self.get_output(params)

        return df

    def s11002(self, start_date):
        """[11002] 전체지수 등락률
        :return:
        """
        bld = 'dbms/MDC/STAT/standard/MDCSTAT00201'

        params = {
            'bld': bld,
            'locale': self.locale,
            'idxIndMidclssCd': self.sector,
            'strtDd': start_date,
            'endDd': self.date,
            'share': self.share,
            'money': self.money,
            'csvxls_isNo': self.csvxls_is_no
        }
        df = self.get_output(params)

        return df
