import secrets
import requests
import argparse
import sys

def upload(api_key: str, content: str, expire: str):
    API_DEV_KEY = api_key

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        "api_dev_key": API_DEV_KEY,
        "api_paste_code": str(content),
        "api_option": "paste",
        "api_paste_expire_date": expire,
        "api_paste_private": "0",
        "api_paste_name": f"{str(secrets.token_hex(nbytes=4))}",
        "api_paste_format": "lua",
    }

    response = requests.post("https://pastebin.com/api/api_post.php", headers=headers, data=data)
    return [response.content.decode(), "https://pastebin.com/raw/" + response.content.decode()[21:]]

paste = upload("22EYK0SdT99Q30q0rq8N1Z-mFdwnjW8T", 'print("hi")', "N")

print(paste[0] + "\n" + paste[1])