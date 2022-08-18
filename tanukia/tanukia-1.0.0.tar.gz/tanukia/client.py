from tanukia.http import TanukiaRequest
from tanukia.model import HitoTanu

class Hitomi(TanukiaRequest):
  """
  [**Saebasol**](https://github.com/Saebasol/Heliotrope)님이 만드신 `Heliotrope API`를 사용한 히토미 라이브러리 입니다.
  """
  def __init__(
    self
  ) -> None:
    pass

  async def gallery(self, code : str) -> HitoTanu:
    tag = "galleryinfo"
    result = await self.request(tag, code)
    list = ['japanese_title', 'video', 'language_url', 'videofilename','scene_indexes']
    for i in list:
      del result[i]
    return HitoTanu(result, **result)