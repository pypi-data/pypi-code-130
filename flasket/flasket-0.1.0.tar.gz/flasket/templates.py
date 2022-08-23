from flask import current_app, has_app_context

g_template_global = {}


# TODO: accept client name, not only function
def template_global(fn):
    """Mark function as a Jinja2 global template"""
    # pylint: disable=protected-access
    if has_app_context():
        app = current_app.config["APPLICATION"]
        assert False, "flasket.__init__: Application has a context"
        app.app.add_template_global(fn)
    else:
        g_template_global[fn.__name__] = fn
    return fn


# TODO
