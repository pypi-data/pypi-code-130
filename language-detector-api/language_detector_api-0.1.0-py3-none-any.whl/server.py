#!/usr/bin/env python3.7
import sys
import logging
import uvloop
import asyncio
from engine import validate_language 
from aiohttp import web



asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class LanguageDetectorServer:

    def __init__(self):
        self._app = web.Application()
        self._app.router.add_post("/validate_language", validate_language_server)
        
    def start(self, port: int):
        web.run_app(self._app, port=port)

async def validate_language_server(req):

    try:
        req = await req.json()
        batch = req.get("srcs")
        pred_label, score = validate_language(batch)
        ans = {
            "tus": [{'src_detected':pred_label,'src_lang_confidence':score}]
        }
        return web.json_response(ans, status=200)

    except Exception as e:
        logging.exception(str(e))
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Three arguments needed: ")
        print("config and port")
    else:
        try:
            server = LanguageDetectorServer(args[0])
            server.start(int(args[1]))
        except Exception as e:
            logging.exception(str(e))
            raise Exception("Error") from e