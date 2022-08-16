import http.client


class KeycloakApi(object):

    @staticmethod
    def get_token(tenant, username, password):
        conn = http.client.HTTPSConnection("v2sso-dev.cropin.co.in")
        payload = 'client_id=web_app&username={}&password={}&grant_type=password'.format(username, password)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/auth/realms/{}/protocol/openid-connect/token".format(tenant), payload, headers)
        res = conn.getresponse()
        data = res.read()

        return data
