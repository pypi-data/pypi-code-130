from jennifer.api.format import format_function
from jennifer.agent import jennifer_agent
from jennifer.wrap.wsgi import wrap_wsgi_app
from distutils.version import LooseVersion

__hooking_module__ = 'flask'
__minimum_python_version__ = LooseVersion("2.7")


def wrap_dispatch_request(origin, flask):

    def handler(self):
        try:
            from werkzeug.exceptions import NotFound
        except ImportError:
            NotFound = None

        req = flask.ctx._request_ctx_stack.top.request
        if req is not None and req.url_rule is not None:
            this_handler = self.view_functions.get(req.url_rule.endpoint, None)
            handler_name = format_function(this_handler)
            agent = jennifer_agent()
            transaction = agent.current_transaction()
            if transaction is not None and handler_name != '':
                transaction.profiler.set_root_name(handler_name)

        return_value = None
        err = None
        try:
            return_value = origin(self)
        except Exception as e:
            err = e

        if err is not None:
            cur_tx = jennifer_agent().current_transaction()
            if cur_tx is not None:
                profiler = cur_tx.profiler

                if type(err) == NotFound:
                    profiler.not_found(err)
                else:
                    profiler.service_error(err)
            raise err

        return return_value

    return handler


def hook(flask):
    flask.Flask.wsgi_app = wrap_wsgi_app(flask.Flask.wsgi_app)
    flask.Flask.dispatch_request = wrap_dispatch_request(flask.Flask.dispatch_request, flask)
