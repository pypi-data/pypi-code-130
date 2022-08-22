"""
getbooru v1.0
Copyright (c) 2022 KuuhakuTeam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import random
import requests
import asyncio

from bs4 import BeautifulSoup as soup

from ..tags import SAFEBOORU_TAGS
from ..errors import InvalidTag, RequestError

class Safebooru:
    def __init__(self) -> None:
        self.safe = "https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=1"

    def get_image(self, tag):
        try:
            if not tag in SAFEBOORU_TAGS:
                raise InvalidTag("Invalid tag, check and insert a valid tag")
            resp = requests.get(self.safe + f"&pid=1&tags={tag}&limit=1")
            if not resp.status_code == 200:
                raise RequestError(
                    "Failed to connect to safebooru servers"
                )
            try:
                posts = int(soup(resp.text, "xml").find("posts")["count"])
                rand_post = requests.get(self.safe + f"&pid={random.randint(1, posts)}&tags={tag}&limit=1&json=1")
                base = "https://safebooru.org/images/"
                result = rand_post.json()[0]
                img = base + f"{result['directory']}/{result['image']}"
                return {'image': img}
            except Exception:
                raise RequestError(
                    "Failed to connect to safebooru servers"
                )
        except asyncio.TimeoutError:
            raise TimeoutError(
                "Internal Server Timeout, Failed to communicate with api server"
            )