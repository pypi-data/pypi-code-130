from flask import current_app, has_app_context


__all__ = ["client"]

g_clients = {}


# TODO: accept client name, not only function
def client(fn):
    if has_app_context():
        app = current_app.config["APPLICATION"]
        assert False, "flasket.client.__init__: Application has a context"
    else:
        g_clients[fn.__name__] = fn
    return fn


## TODO
