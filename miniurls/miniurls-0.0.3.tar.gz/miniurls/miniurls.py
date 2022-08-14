from requests import get

class Short:

  def __init__(self):
    self.api = "https://api.shrtco.de/v2"
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    }
  
  def shortUrl(self, url: str):
    return get(
      f"{self.api}/shorten?url={url}",
      headers = self.headers
    ).json()
  
  def protectUrl(self, url: str, password: str):
    return get(
      f"{self.api}/shorten?url={url}&password={password}",
      headers = self.headers
    ).json()
    
  def emojiUrl(self, url: str):
    return get(
      f"{self.api}/shorten?emoji&url={url}",
      headers = self.headers
    ).json()

  def customUrl(self, url: str, custom_code: str):
    return get(
      f"{self.api}/shorten?url={url}&custom_code={custom_code}",
      headers = self.headers
    ).json()

  def urlInfo(self, url: str, code: str):
    return get(
      f"{self.api}/info?code={code}",
      headers = self.headers
    ).json()
