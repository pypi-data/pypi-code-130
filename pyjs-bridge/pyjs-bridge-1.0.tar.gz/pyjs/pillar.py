from .transport import websocket
from .registry import client_in_call, get_active_client_class


use_websocket = False


def initialize(use_websocket_transport=True, params=None):
    global use_websocket
    use_websocket = use_websocket_transport
    if use_websocket:
        websocket.init(params["app"], get_active_client_class, client_in_call, params["token_verifier"])


def start_listener():
    pass


def stop_listener():
    pass


def get_js_prototype():
    if use_websocket:
        return websocket.get_js_prototype()


def server_out_call(client, function_call, kwargs):
    if client.expired:
        return False
    if client.transport_type == websocket.TRANSPORT_TYPE:
        websocket.send_data(client.transport, function_call, kwargs)
    else:
        print("mock out call...", function_call, kwargs)
    return True
