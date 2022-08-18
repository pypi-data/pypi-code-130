import requests 

def wifi_checker():
    url = 'http://google.com'
    timeout = 5
    try:
        requests.get(url=url,timeout=timeout)
        return True
    except(requests.ConnectionError):
        return False
