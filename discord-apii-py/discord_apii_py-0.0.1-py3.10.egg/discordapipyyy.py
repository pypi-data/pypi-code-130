import requests, threading

class Discord:
    def sniper(token, code, guild):
        headers = {'authorization': token}
        vanity = {"code":code}
        r = requests.patch(f'https://discord.com//api/v9/guilds/{guild}/vanity-url', headers=headers, json=vanity)
        print(r.text)