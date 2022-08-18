import aiohttp

class TanukiaRequest:
  base_url = "https://api.saebasol.org/api/hitomi/"
  def __init__(self) -> None:
    pass

  async def request(
    self,
    tag : str,
    code : str
  ):
    URL = self.base_url + tag + "/" + code
    async with aiohttp.ClientSession() as session:
      async with session.get(URL) as response:
        rescode = response.status
        if(rescode==200):
          result = await response.json()
          return result
        else:
          raise