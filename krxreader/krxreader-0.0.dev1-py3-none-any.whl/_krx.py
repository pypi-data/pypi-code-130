import requests


def get_json_data(data):
    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

    r = requests.post(url=url, data=data)
    dic = r.json()

    return dic


def download_csv(data):
    # 1. Generate OTP
    generate_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

    r = requests.post(url=generate_url, data=data)
    otp = {
        'code': r.text
    }

    # 2. Download CSV
    download_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

    r = requests.post(url=download_url, data=otp)
    csv = r.content.decode(encoding='euc_kr')

    return csv


if __name__ == '__main__':
    params = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT00101',
        'locale': 'ko_KR',
        'idxIndMidclssCd': '01',
        'trdDd': '20220822',
        'share': '2',
        'money': '3',
        'csvxls_isNo': 'false'
    }

    d = get_json_data(params)

    print('=======================================')
    print(type(d))
    print(d)

    params['name'] = 'fileDown'
    params['url'] = params['bld']
    del params['bld']

    c = download_csv(params)

    print('=======================================')
    print(type(c))
    print(c)
