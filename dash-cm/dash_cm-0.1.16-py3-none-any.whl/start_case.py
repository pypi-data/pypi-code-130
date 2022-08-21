import asyncio
import logging
import socket
import webbrowser

import treefiles as tf


def start_app(path):
    """
    Before calling this function, do in a terminal:
        pip install dash_cm
        python -m dash_cm serve

    It will start the dashboard app server
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sock.connect_ex(("localhost", 3000)) != 0:
        log.error("You should start the server with: `dashcm serve &`")
        raise SystemExit

    from aiohttp import web

    app = web.Application()
    routes = web.RouteTableDef()
    cc = tf.munchify({"host": "localhost", "port": 8784})

    @routes.get("/{name}")
    async def handle(request):
        name = request.match_info["name"]
        if tf.basename(path) == name:
            return web.FileResponse(path)
        return web.Response(text="not found")

    async def bootup(_):
        asyncio.create_task(background())

    async def background():
        await asyncio.sleep(1)
        webbrowser.open(f"http://{cc.host}:3000/loader/{tf.basename(path)}")
        await asyncio.sleep(2)
        await app.cleanup()
        await app.shutdown()

    app.add_routes(routes)
    app.on_startup.append(bootup)
    with tf.timeout(5):
        web.run_app(app, **cc)

    log.info("Finished")


log = logging.getLogger(__name__)
