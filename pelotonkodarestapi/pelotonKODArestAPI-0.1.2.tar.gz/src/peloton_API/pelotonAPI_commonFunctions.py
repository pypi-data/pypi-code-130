import requests as r

#Global Variables
authurl = r'https://id.peloton.com/connect/authorize'
tokenurl = r'https://id.peloton.com/connect/token'
callbackurl = r'https://portal.peloton.com'
Scope = r'openid profile offline_access'
rooturl = r'https://api.peloton.com/v1.1'
TokenName = r'Prod PCE'
target_app = r'wellview'
lookuptablename = r'libjobjobtyp'

#access token grants below

token_headers = {"Content-type": 'application/x-www-form-urlencoded'}

def getAccessToken(refreshToken,clientID,clientSecret):
    token_params =  {
            'grant_type': 'refresh_token',
           'refresh_token':refreshToken,
           'client_id':clientID,
           'client_secret':clientSecret
                     }
    auth = r.post(tokenurl,data=token_params,headers=token_headers)
    if auth.status_code == 200:
        return auth
    else:
        print('Bad API Request: Status %s ' %(auth.status_code), ',Status Text: %s' %(auth.text))
        return auth


#API Calls
def getUser(access_token,subscription_key):
    call_headers = {"Content-Type":'application/json',
                    "Authorization":"Bearer %s" %(access_token),
                    "Ocp-Apim-Subscription-Key":subscription_key}
    user = r.get(url=rooturl+'/user',headers=call_headers)
    if user.status_code == 200:
        return user
    else:
        print('Bad API Request: Status %s ' %(user.status_code), ',Status Text: %s' %(user.text))
        return user

def getApplicationHeaders(user):
    apps = user.json()['organizations'][0]['applications']
    for i in range(0,len(apps)):
        if apps[i]['appid'] == 'SiteView':
            siteView = apps[i]['headervalue']
        elif apps[i]['appid'] =='WellView':
            wellView = apps[i]['headervalue']
    return siteView,wellView
        
