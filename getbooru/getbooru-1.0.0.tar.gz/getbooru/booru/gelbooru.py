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

import requests
import asyncio

from bs4 import BeautifulSoup as soup

from ..tags import GELBOORU_TAGS
from ..errors import InvalidTag, RequestError

class Gelbooru:
    def __init__(self) -> None:
        self.gel = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags=sort%3Arandom+"

    def get_image(self, tag):
        try:
            if not tag in GELBOORU_TAGS:
                raise InvalidTag("Invalid tag, check and insert a valid tag")
            resp = requests.get(self.gel + tag)
            if not resp.status_code == 200:
                raise RequestError(
                    "Failed to connect to gelbooru servers"
                )
            try:
                sp = soup(resp.content, "xml", from_encoding="utf-8")
                img = sp.find("file_url").text
                return {'image': img}
            except Exception:
                raise RequestError(
                    "Failed to connect to gelbooru servers"
                )
        except asyncio.TimeoutError:
            raise TimeoutError(
                "Internal Server Timeout, Failed to communicate with api server"
            )