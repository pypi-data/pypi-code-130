from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import List
from functools import partial
import asyncio
import os

file_path = os.path.dirname(os.path.abspath(__file__))
TRANSPORT_TYPE = "ws"


def get_js_prototype():
    with open(os.path.join(file_path, 'proto.js')) as js_file:
        content = js_file.read()
    return content


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.id_2_client = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


def init(app, get_active_client_class, on_receive_msg, token_verifier=None):
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
        if token_verifier is not None:
            token_data = token_verifier(token)
            if token_data is None:
                return
        await manager.connect(websocket)
        # transport is the socket.
        client_obj = get_active_client_class()(websocket, TRANSPORT_TYPE, token_data)
        try:
            while True:
                package = await websocket.receive_json()
                if "f" not in package:
                    raise WebSocketDisconnect()
                on_receive_msg(client_obj, package["f"], [], package["d"])
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            client_obj.expired = True


def send_data(websocket, function_call, kwargs):
    package = {
        "f": function_call,
        "d": kwargs
    }
    asyncio.ensure_future(partial(websocket.send_json, package)())
