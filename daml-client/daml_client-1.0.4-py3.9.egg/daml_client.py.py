import json
import time
import sys
import requests
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))
print(str(Path(__file__).parent.parent.parent.absolute()))

party_token_map = dict()


class PartyToken:

    def __init__(self, token, timeout):
        self.token = token
        self.timeout = timeout


class ZCException(Exception):

    def __init__(self, error_code, error_message):
        super().__init__((error_code, error_message))
        self.error_message = error_message
        self.error_code = error_code

    def __str__(self):
        return {"error_code": str(self.error_code), "error_message": repr(self.error_message)}

    @property
    def message(self):
        return self.error_message

    @property
    def code(self):
        return self.error_code

    def format(self, *args, **kwargs):
        self.error_message = self.error_message.format(*args, **kwargs)
        return self


class DamlApiError:
    """
    访问daml节点返回错误
    error_code : [60000 , 70000)
    """
    DAML_ACCESS_ERROR = ZCException(error_code=60001, error_message="{}")
    GET_TOKEN_ERROR = ZCException(error_code=60002, error_message="get token error")


class Party:

    def __init__(self, user, asx_party, cred="", client_id="", client_secret="", dr_client_id="", dr_client_secret=""):
        """
        :param user: 对应我们系统的用户
        :param asx_party: 对应asx的party
        :param cred: 开发环境下用于获取token的, client_id和client_secret对应其他环境token获取的方式
        :param client_id: 开发环境下用于获取token的, client_id和client_secret对应其他环境token获取的方式
        :param client_secret: 开发环境下用于获取token的, client_id和client_secret对应其他环境token获取的方式
        :param dr_client_id: 开发环境下用于获取token的, client_id和client_secret对应其他环境token获取的方式
        :param dr_client_secret: 开发环境下用于获取token的, client_id和client_secret对应其他环境token获取的方式
        """
        print("init__>>>>>", user, asx_party, cred, client_id, client_secret, dr_client_id, dr_client_secret)
        self.user = user
        self.asx_party = asx_party
        self.cred = cred
        self.client_id = client_id
        self.client_secret = client_secret
        self.dr_client_id = dr_client_id
        self.dr_client_secret = dr_client_secret
        print(
            f"\nself.user>>>   \t{self.user}\n",
            f"self.asx_party>>>   \t{self.asx_party}\n",
            f"self.cred>>>   \t{self.cred}\n",
            f"self.client_id>>>   \t{self.client_id}\n",
            f"self.client_secret>>>   \t{self.client_secret}\n",
            f"self.dr_client_id>>>   \t{self.dr_client_id}\n",
            f"self.dr_client_secret>>>   \t{self.dr_client_secret}\n",

        )


class DamlClient(Party):
    MAX_RETRY_TIMES = 3

    REQUEST_OK = 200
    REQUEST_INVALID_AUTH = 401
    REQUEST_TOO_MANY_REQUESTS = 429
    REQUEST_BAD_GATEWAY = 502
    REQUEST_UNAVAILABLE = 503
    REQUEST_GATEWAY_TIMEOUT = 504

    def __init__(self, user, asx_party, **kwargs):
        super().__init__(user, asx_party, **kwargs)
        self.TOKEN_EXPIRED = 10 * 60 * 60  # token 过期时间
        self.IAM = "https://id.uat.dltsolutions.com.au/oauth/token"  # 获取token的url
        self.DR_IAM = ""  # 容灾 获取token的url
        self.DR_LEDGER_ID = ""  # 容灾 第三方平台分类账ID
        self.LEDGER_ID = "cg01j01"  # 第三方平台分类账ID
        self.JSON_API = "https://{}.uat.dltsolutions.com.au/v1/"  # 第三方平台的接口url

    def get_token_by_api_for_sandbox(self, timeout=10, retry_times=0, is_dr_api=False):
        if is_dr_api:
            pass
            # logger.debug('use dr pointend')
        # get_token_url = "https://id.uat.dltsolutions.com.au/oauth/token"
        get_token_url = self.DR_IAM if is_dr_api else self.IAM
        headers = {
            'content-type': 'application/json',
        }
        # logger.debug(f"get token for {party.asx_party}")
        data = {
            "client_id": self.dr_client_id if is_dr_api else self.client_id,
            "client_secret": self.dr_client_secret if is_dr_api else self.client_secret,
            "audience": "https://zerocap.dltsolutions.com.au/ledger-api",
            "grant_type": "client_credentials"
        }
        try:
            response = requests.post(get_token_url, headers=headers, json=data, timeout=timeout)
        except Exception as e:
            print(e)
            # logger.exception(e)
            # 连接异常，直接切换容灾？
            if not is_dr_api:
                retry_times += 1
                if retry_times < self.MAX_RETRY_TIMES:
                    return self.get_token_by_api_for_sandbox(timeout, retry_times, False)
                else:
                    return self.get_token_by_api_for_sandbox(timeout, retry_times, True)
            else:
                raise DamlApiError.GET_TOKEN_ERROR
        if response.status_code != self.REQUEST_OK:
            print(response.text)
            # logger.debug(response.text)
            if not is_dr_api and (response.status_code in (self.REQUEST_TOO_MANY_REQUESTS,
                                                           self.REQUEST_BAD_GATEWAY,
                                                           self.REQUEST_UNAVAILABLE,
                                                           self.REQUEST_GATEWAY_TIMEOUT) or response.json().get(
                'status') in (
                                          self.REQUEST_TOO_MANY_REQUESTS,
                                          self.REQUEST_BAD_GATEWAY,
                                          self.REQUEST_UNAVAILABLE,
                                          self.REQUEST_GATEWAY_TIMEOUT)):
                # 429，需要等待更长时间
                time.sleep(1 if response.status_code == self.REQUEST_TOO_MANY_REQUESTS else 0.1)
                retry_times += 1
                if retry_times < self.MAX_RETRY_TIMES:
                    return self.get_token_by_api_for_sandbox(timeout, retry_times, False)
                else:
                    return self.get_token_by_api_for_sandbox(timeout, retry_times, True)
            raise DamlApiError.GET_TOKEN_ERROR
        return json.loads(response.text).get('access_token')

    def get_token_by_api(self, timeout=10):
        return self.get_token_by_api_for_sandbox(timeout)

    def reset_token(self):
        party_token_map[self.asx_party] = PartyToken(self.get_token_by_api(), int(time.time()))
        return party_token_map[self.asx_party]

    def get_token(self):

        token = party_token_map.get(self.asx_party, None)

        if not isinstance(token, PartyToken) or \
                int(time.time()) - token.timeout > self.TOKEN_EXPIRED:
            return self.reset_token().token

        return token.token

    def send_request_with_dr_point(self, request_type, data, timeout, retry_times=0, is_dr_api=False):
        if is_dr_api:
            pass
            # logger.debug('use dr point end')

        token = self.get_token()

        headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'Authorization': f"Bearer {token}"
        }
        print("headers >>>>>>", headers)
        asx_url = self.JSON_API.format(self.DR_LEDGER_ID if is_dr_api else self.LEDGER_ID)
        # asx_url = config.get('CONFIG_ASX').get('JSON_API').format(
        #     config.get('CONFIG_ASX').get('DR_LEDGER_ID' if is_dr_api else 'LEDGER_ID'))
        print(f'asx_url: >>> {asx_url}')
        # logger.debug('daml request: ' + asx_url + request_type)
        # logger.debug('daml params: \n' + json.dumps(data, indent=4))
        try:
            response = requests.post(asx_url + request_type, headers=headers, json=data,
                                     timeout=timeout)

            if not is_dr_api and (response.status_code in (self.REQUEST_TOO_MANY_REQUESTS,
                                                           self.REQUEST_BAD_GATEWAY,
                                                           self.REQUEST_UNAVAILABLE,
                                                           self.REQUEST_GATEWAY_TIMEOUT) or response.json().get(
                'status') in (
                                          self.REQUEST_TOO_MANY_REQUESTS,
                                          self.REQUEST_BAD_GATEWAY,
                                          self.REQUEST_UNAVAILABLE,
                                          self.REQUEST_GATEWAY_TIMEOUT)):
                # 429，需要等待更长时间
                time.sleep(1 if response.status_code == self.REQUEST_TOO_MANY_REQUESTS else 0.1)
                retry_times += 1
                if retry_times < self.MAX_RETRY_TIMES:
                    return self.send_request_with_dr_point(request_type, data, timeout, retry_times, False)
                else:
                    return self.send_request_with_dr_point(request_type, data, timeout, retry_times, True)
            return response
        except Exception as e:
            if not is_dr_api:
                return self.send_request_with_dr_point(request_type, data, timeout, retry_times, True)
            raise e

    def daml_request(self, request_type, payload_data, timeout=10):
        """
        :param request_type:            第三方平台请求方法的类型： 如 'query'
        :param payload_data: dict       第三方平台请求方法的有效载荷数据
        :param timeout:                 延迟超时时间
        :return:
        """
        response = self.send_request_with_dr_point(request_type, payload_data, timeout)

        if response.status_code == self.REQUEST_INVALID_AUTH or (
                response.status_code != self.REQUEST_OK and response.text.upper().find('UNAUTHENTICATED') >= 0):
            # 如果拿到的是没有认证的错误，重新获取token，然后重试
            self.reset_token()
            response = self.send_request_with_dr_point(request_type, payload_data, timeout)
        print(response.text)
        # logger.debug(response.text)
        return response


daml_client = DamlClient(

    user="asx_client@eigen.capital",
    asx_party="zerocap_client",
    cred='',
    client_id="1MiDOUYfK0CgeAjUd0tuxu095nmnD1fy",
    client_secret='yX4NMrW3tuzYurj34V6mqnhWaf6sXTPO-XlNKI20PGX4Iv-D3qK3NwI-yjjuF_Z5',
    dr_client_id="wwxxyxYlRDwiWCYrCIlSHegATRGMt08c",
    dr_client_secret="mCn-V6ft884C6gC7jjZRDeSqnM5KP-Did8ioABmBlVzQT6EbBOqdTZJpe54gFXOZ"

)


def get_all_data():
    """
    查询数据集
    :return:
    """
    payload_data = dict(templateIds=[
        '8e664e10953f3ab1b4dc8d8a4421f01d66402f1e0ad829de74a83c2203854b91:Address:Address',
        '8e664e10953f3ab1b4dc8d8a4421f01d66402f1e0ad829de74a83c2203854b91:Balance:Balance',
        '8e664e10953f3ab1b4dc8d8a4421f01d66402f1e0ad829de74a83c2203854b91:Rfq:Quote',
        '8e664e10953f3ab1b4dc8d8a4421f01d66402f1e0ad829de74a83c2203854b91:Rfq:Fill'
    ], query={})
    METHODS_DAML_QUERY = 'query'
    print(f"payload_data:>>>> {payload_data}")
    print(f"METHODS_DAML_QUERY:>>>> {METHODS_DAML_QUERY}")

    response = daml_client.daml_request(METHODS_DAML_QUERY, payload_data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise DamlApiError.DAML_ACCESS_ERROR.format(response.text)


daml_client = DamlClient()

if __name__ == '__main__':

    get_all_data()
    # client_party = Party(
    #     user="asx_client@eigen.capital",
    #     asx_party="zerocap_client",
    #     cred='',
    #     client_id="1MiDOUYfK0CgeAjUd0tuxu095nmnD1fy",
    #     client_secret='yX4NMrW3tuzYurj34V6mqnhWaf6sXTPO-XlNKI20PGX4Iv-D3qK3NwI-yjjuF_Z5',
    #     dr_client_id="wwxxyxYlRDwiWCYrCIlSHegATRGMt08c",
    #     dr_client_secret="mCn-V6ft884C6gC7jjZRDeSqnM5KP-Did8ioABmBlVzQT6EbBOqdTZJpe54gFXOZ"
    # )
