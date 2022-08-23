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
        log.error("You first need to start the server with: `dashcm serve &`")
        raise SystemExit

    from aiohttp import web
    import aiohttp_cors

    cc = tf.munchify({"host": "localhost", "port": 8784})
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    rsc = cors.add(app.router.add_resource("/{name}"))

    async def handler(request):
        name = request.match_info["name"]
        if tf.basename(path) == name:
            return web.FileResponse(path)
        return web.Response(text="not found")

    cors.add(
        rsc.add_route("GET", handler),
        {"*": aiohttp_cors.ResourceOptions(allow_headers="*")},
    )

    async def bootup(_):
        asyncio.create_task(background())

    async def background():
        await asyncio.sleep(0)
        webbrowser.open(f"http://{cc.host}:3000/loader/{tf.basename(path)}")
        await asyncio.sleep(1)
        await app.cleanup()
        await app.shutdown()

    app.on_startup.append(bootup)
    with tf.timeout(5):
        web.run_app(app, **cc)

    log.info("Finished")


log = logging.getLogger(__name__)
