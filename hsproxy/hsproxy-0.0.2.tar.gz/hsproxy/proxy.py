#!/usr/bin/env python3

from .translate import translate as _translate
from grpclib.utils import graceful_exit
from grpclib.server import Server
from .i18n_pb2 import TranslateA
from .i18n_grpc import I18nBase
from .chrome2hs import CHROME2HS


class I18n(I18nBase):

  async def translate(self, stream):
    request = await stream.recv_message()
    src = request.src
    src = CHROME2HS.get(src, src)
    to = request.to
    to = CHROME2HS.get(to, to)

    li = tuple(_translate(src, to, request.li))

    await stream.send_message(TranslateA(li=li))


async def main(host="0.0.0.0", port=5900):
  uri = f"{host}:{port}"
  print(f'grpc://{uri}')
  server = Server([I18n()])
  with graceful_exit([server]):
    await server.start(host, port)
    await server.wait_closed()


if __name__ == "__main__":
  from fire import Fire
  Fire(main)
